document.getElementById('uploadForm').addEventListener('submit', async (e) => {
    e.preventDefault();
    
    const submitBtn = document.getElementById('submitBtn');
    const loader = document.getElementById('loader');
    const resultArea = document.getElementById('resultArea');

    // UI Updates
    submitBtn.disabled = true;
    submitBtn.innerText = "Analyzing Content...";
    loader.style.display = 'block';
    resultArea.style.display = 'none';

    // Prepare Form Data
    const formData = new FormData();
    formData.append('modelAnswer', document.getElementById('modelAnswer').value);
    formData.append('maxMarks', document.getElementById('maxMarks').value);
    formData.append('script', document.getElementById('scriptFile').files[0]);

    const modelPdfFile = document.getElementById('modelPdf').files[0];
    if (modelPdfFile) {
        formData.append('modelPdf', modelPdfFile);
    }

    try {
        const response = await fetch('/evaluate', { method: 'POST', body: formData });
        const data = await response.json();

        if (data.error) throw new Error(data.error);

        // Populate Results safely
        document.getElementById('marksDisplay').innerText = data.marks_obtained ?? 0;
        document.getElementById('maxMarksDisplay').innerText = document.getElementById('maxMarks').value;

        document.getElementById('transcriptionBox').innerText =
            typeof data.transcription === 'string'
                ? data.transcription
                : JSON.stringify(data.transcription, null, 2);

        document.getElementById('feedbackBox').innerHTML =
            data.feedback ? data.feedback.replace(/\n/g, '<br>') : "No specific feedback.";

        // Status Badge Logic
        const percentage = (data.marks_obtained / document.getElementById('maxMarks').value) * 100;
        const badge = document.getElementById('statusBadge');

        if (percentage >= 80) {
            badge.innerText = "Excellent Result";
            badge.style.backgroundColor = "#d1e7dd";
            badge.style.color = "#0f5132";
        } else if (percentage >= 40) {
            badge.innerText = "Average Performance";
            badge.style.backgroundColor = "#fff3cd";
            badge.style.color = "#664d03";
        } else {
            badge.innerText = "Needs Improvement";
            badge.style.backgroundColor = "#f8d7da";
            badge.style.color = "#842029";
        }

        resultArea.style.display = 'block';
        resultArea.scrollIntoView({ behavior: 'smooth' });

    } catch (error) {
        console.error("Evaluation Error:", error);
        alert("Something went wrong: " + error.message);
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerText = "Grade Script Now";
        loader.style.display = 'none';
    }
});
function downloadPDF() {
    const data = {
        marks: document.getElementById('marksDisplay').innerText,
        maxMarks: document.getElementById('maxMarksDisplay').innerText,
        feedback: document.getElementById('feedbackBox').innerText,
        transcription: document.getElementById('transcriptionBox').innerText
    };

    fetch('https://scriptsense-ai.onrender.com/download-pdf', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify(data)
    })
    .then(response => response.blob())
    .then(blob => {
        const url = window.URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = "evaluation_report.pdf";
        a.click();
    })
    .catch(err => {
        console.error("Download error:", err);
        alert("Failed to download PDF");
    });
}
