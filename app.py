from flask import Flask, request, jsonify, send_from_directory
import os
import fitz  # PyMuPDF
import base64
from flask.cli import load_dotenv
from groq import Groq
from werkzeug.utils import secure_filename
import json
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib.pagesizes import letter
from flask import send_file
import io
load_dotenv()

app = Flask(__name__, static_folder='static', template_folder='public')
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

groq = Groq(api_key=os.getenv("GROQ_API_KEY"))

# =========================
# ROUTES
# =========================

@app.route('/')
def serve_index():
    return send_from_directory('public', 'index.html')

@app.route('/download-pdf', methods=['POST'])
def download_pdf():
    data = request.json

    marks = data.get("marks", 0)
    max_marks = data.get("maxMarks", 10)
    feedback = data.get("feedback", "")
    transcription = data.get("transcription", "")

    buffer = io.BytesIO()

    doc = SimpleDocTemplate(buffer, pagesize=letter)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Evaluation Report", styles['Title']))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph(f"Score: {marks} / {max_marks}", styles['Heading2']))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Transcription:", styles['Heading3']))
    elements.append(Paragraph(transcription, styles['Normal']))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Feedback:", styles['Heading3']))
    elements.append(Paragraph(feedback, styles['Normal']))

    doc.build(elements)

    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name="evaluation_report.pdf", mimetype='application/pdf')
@app.route('/evaluate', methods=['POST'])
def evaluate():
    script_file = request.files.get('script')
    model_pdf = request.files.get('modelPdf')
    model_answer = request.form.get('modelAnswer', '')
    max_marks = request.form.get('maxMarks', '10')

    if not script_file:
        return jsonify({"error": "Student script required"}), 400

    script_path = os.path.join(UPLOAD_FOLDER, secure_filename(script_file.filename))
    script_file.save(script_path)

    model_path = None

    try:
        # =========================
        # 1. MODEL ANSWER
        # =========================
        final_model_answer = model_answer

        if model_pdf:
            model_path = os.path.join(UPLOAD_FOLDER, secure_filename(model_pdf.filename))
            model_pdf.save(model_path)

            # ✅ SAFE FILE HANDLING (auto close)
            with fitz.open(model_path) as doc:
                text = ""
                for page in doc:
                    text += page.get_text()

            final_model_answer = text

        # =========================
        # 2. STUDENT SCRIPT
        # =========================
        mime = script_file.mimetype
        image_parts = []

        if mime == "application/pdf":

            with fitz.open(script_path) as doc:

                all_pages = list(doc)
                useful_pages = []

                # Skip empty / cover pages
                for page in all_pages:
                    text = page.get_text().strip()
                    if len(text) > 50:
                        useful_pages.append(page)

                if not useful_pages:
                    useful_pages = all_pages

                MAX_PAGES = 8
                selected_pages = useful_pages[:MAX_PAGES]

                for i, page in enumerate(selected_pages):
                    pix = page.get_pixmap()
                    img_path = f"{script_path}_{i}.png"
                    pix.save(img_path)

                    with open(img_path, "rb") as f:
                        base64_image = base64.b64encode(f.read()).decode()

                    image_parts.append({
                        "type": "image_url",
                        "image_url": {
                            "url": f"data:image/png;base64,{base64_image}"
                        }
                    })

                    os.remove(img_path)

        else:
            with open(script_path, "rb") as f:
                base64_image = base64.b64encode(f.read()).decode()

            image_parts.append({
                "type": "image_url",
                "image_url": {
                    "url": f"data:{mime};base64,{base64_image}"
                }
            })

        # =========================
        # 3. AI EVALUATION
        # =========================
        response = groq.chat.completions.create(
            model="meta-llama/llama-4-scout-17b-16e-instruct",
            messages=[{
                "role": "user",
                "content": [
                    {
                        "type": "text",
                        "text": f"""
You are an expert examiner.

IMPORTANT:
- Ignore cover/title pages
- Read all answer pages carefully
- Extract meaningful content only

Model Answer:
{final_model_answer}

Max Marks: {max_marks}

Return STRICT JSON:
{{
  "marks_obtained": number,
  "feedback": "clear feedback",
  "transcription": "answer content only"
}}
"""
                    },
                    *image_parts
                ]
            }],
            response_format={"type": "json_object"}
        )

        result_str = response.choices[0].message.content

        try:
            result = json.loads(result_str)
        except:
            return jsonify({"error": "Invalid AI response"}), 500

        return jsonify(result)

    except Exception as e:
        return jsonify({"error": str(e)}), 500

    finally:
        # =========================
        # SAFE CLEANUP
        # =========================
        try:
            if os.path.exists(script_path):
                os.remove(script_path)
        except:
            pass

        try:
            if model_path and os.path.exists(model_path):
                os.remove(model_path)
        except:
            pass


# =========================
# RUN SERVER
# =========================
if __name__ == '__main__':
    port = int(os.environ.get("PORT", 3000))
    app.run(debug=True, host='0.0.0.0', port=port)
