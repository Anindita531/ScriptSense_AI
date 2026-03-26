from flask import Flask, request, jsonify, send_from_directory
import os
import fitz  # PyMuPDF
import base64
from flask.cli import load_dotenv
from groq import Groq
from werkzeug.utils import secure_filename
import json

load_dotenv()  # Load environment variables from .env

app = Flask(__name__, static_folder='static', template_folder='public')
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Initialize Groq client
groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

# Serve static files
@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory('static', filename)

@app.route('/evaluate', methods=['POST'])
def evaluate():
    script_file = request.files.get('script')
    model_pdf = request.files.get('modelPdf')
    model_answer = request.form.get('modelAnswer', '')
    max_marks = request.form.get('maxMarks', '10')

    if not script_file:
        return jsonify({"error": "Student script required"}), 400

    # Save student script
    script_path = os.path.join(UPLOAD_FOLDER, secure_filename(script_file.filename))
    script_file.save(script_path)

    # Process model answer
    final_model_answer = model_answer
    if model_pdf:
        model_path = os.path.join(UPLOAD_FOLDER, secure_filename(model_pdf.filename))
        model_pdf.save(model_path)
        doc = fitz.open(model_path)
        text = ""
        for page in doc:
            text += page.get_text()
        final_model_answer = text

    # Convert student script to image if PDF
    mime = script_file.mimetype
    image_path = script_path
    if mime == "application/pdf":
        doc = fitz.open(script_path)
        page = doc[0]
        pix = page.get_pixmap()
        image_path = script_path + ".png"
        pix.save(image_path)

    # Convert image to base64
    with open(image_path, "rb") as f:
        base64_image = base64.b64encode(f.read()).decode()

    # AI Evaluation
    try:
        response = groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""You are an expert teacher.

Carefully analyze the handwritten answer.

IMPORTANT:
- Try to read unclear handwriting
- Extract as much text as possible
- Do NOT say blank unless nothing visible

Model Answer:
"{final_model_answer}"

Max Marks: {max_marks}

Return JSON:
{{
  "marks_obtained": number,
  "feedback": "detailed feedback",
  "transcription": "extracted text"
}}"""
                    },
                    {
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    }
                ]
            }],
            response_format={"type": "json_object"}
        )

        # Convert AI response to Python dict safely
        result_str = response.choices[0].message.content
        try:
            result_dict = json.loads(result_str)
        except json.JSONDecodeError:
            return jsonify({"error": "AI Evaluation failed: invalid JSON"}), 500

        return jsonify(result_dict)

    except Exception as e:
        return jsonify({"error": f"AI Evaluation failed: {str(e)}"}), 500


if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(host='0.0.0.0', port=port)