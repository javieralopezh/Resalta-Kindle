from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import os

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def parse_highlights(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")
    
    highlights = []
    
    for section in soup.find_all("div", class_="section"):
        title = section.find("h3").text if section.find("h3") else "Sin título"
        for highlight in section.find_all("p", class_="highlight"):
            text = highlight.text.strip()
            page = highlight.get("data-page", "N/A")
            note = highlight.find_next_sibling("p", class_="note")
            note_text = note.text.strip() if note else ""
            
            formatted = f"📎 {text} (📖 {page})"
            if note_text:
                formatted += f"\n    🖊️ *{note_text}*"
            
            highlights.append(f"**Capítulo {title}**\n\n{formatted}")
    
    return "\n\n".join(highlights)

@app.route("/", methods=["GET", "POST"])
def index():
    formatted_text = None
    
    if request.method == "POST":
        file = request.files["file"]
        if file and file.filename.endswith(".html"):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            formatted_text = parse_highlights(file_path)

    return render_template("index.html", formatted_text=formatted_text)

if __name__ == "__main__":
    app.run(debug=True)
