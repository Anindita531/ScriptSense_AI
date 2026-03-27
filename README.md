
# ScriptSense AI - Handwritten Evaluation Grading System

**ScriptSense AI** is an advanced AI-based platform for automatically evaluating handwritten student scripts against model answers. It extracts text from handwritten PDFs or images, grades them, and provides detailed feedback.

---

## Features

- ✅ Upload student scripts (PDF or image)  
- ✅ Upload model answer (PDF or text)  
- ✅ AI extracts handwriting and converts it to text  
- ✅ Automatic grading based on model answers  
- ✅ Provides detailed feedback & suggestions  
- ✅ Score visualization with performance status  

---

## Technologies Used

- **Backend:** Python, Flask  
- **Frontend:** HTML, CSS, JavaScript, Bootstrap 5  
- **PDF Processing:** PyMuPDF (`fitz`)  
- **AI Evaluation:** Groq AI (Llama 4 Scout model)  
- **Image Handling:** Base64 encoding of images  
- **Deployment-ready:** Supports Render, Railway, or Heroku  

---

## Project Structure

```
ScriptSenseAI/
├── app.py                # Main Flask application
├── public/               # Frontend static files
│   ├── index.html
│   ├── style.css
│   └── script.js
├── uploads/              # Temporary folder for uploaded scripts/PDFs
├── requirements.txt      # Python dependencies
├── Procfile              # Deployment command (for Render/Heroku)
├── .gitignore            # Ignored files for Git
└── README.md             # Project documentation
```

---

## Installation & Setup

1. **Clone the repository**

```bash
git clone https://github.com/<your-username>/ScriptSenseAI.git
cd ScriptSenseAI
```

2. **Create & activate a virtual environment**

```bash
python -m venv venv
# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies**

```bash
pip install -r requirements.txt
```

4. **Set environment variables**

Create a `.env` file in the root folder:

```env
GROQ_API_KEY=<your-groq-api-key>
PORT=3000
```

5. **Run the app locally**

```bash
python app.py
```

Open in browser: `http://127.0.0.1:3000`

---

## How to Use

1. Upload a **model answer** (text or PDF)  
2. Set the **maximum marks**  
3. Upload the **student’s handwritten script** (image or PDF)  
4. Click **“Grade Script Now”**  
5. View **marks obtained, AI transcription, and feedback**  

---

## Deployment Instructions

**Render Deployment:**

1. Create a new web service on [Render](https://render.com/)  
2. Connect to GitHub repo  
3. Set **Python 3 runtime**  
4. Build command: `pip install -r requirements.txt`  
5. Start command: `python app.py`  
6. Add environment variable: `GROQ_API_KEY=<your-key>`  

**Railway Deployment:**  

- Similar steps: Deploy from GitHub, set environment variable, start command.  

---

## Notes

- Do **not commit `.env`** to GitHub (keeps your API key safe)  
- `uploads/` stores temporary files; can be cleared periodically  
- Supports handwritten PDFs and images only  

---

## License

MIT License © 2026  
You are free to use, modify, and distribute this project.
