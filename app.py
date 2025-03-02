from flask import Flask, render_template, request
from bs4 import BeautifulSoup
import os
import re

app = Flask(__name__)
UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def parse_highlights(file_path, format_type="default", custom_symbols=None):
    with open(file_path, "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, "html.parser")

    highlights = []
    current_chapter = None
    is_note = False

    formats = {
        "default": {"highlight": "📎", "page": "📖", "bookmark": "🔖", "note": "🖊️"},
        "minimalista": {"highlight": "•", "page": "Página", "bookmark": "Marcador", "note": "Nota:"},
    }

    symbols = custom_symbols if custom_symbols else formats.get(format_type, formats["default"])

    for element in soup.find_all(["div"], class_=["sectionHeading", "noteHeading", "noteText"]):
        if "sectionHeading" in element.get("class", []):
            chapter_name = element.text.strip()
            if chapter_name.lower().startswith("capítulo"):
                formatted_chapter = f"**{chapter_name}**"
            else:
                formatted_chapter = f"**Capítulo {chapter_name}**"  
            current_chapter = formatted_chapter  
            highlights.append(f"\n{current_chapter}\n")  

        elif "noteHeading" in element.get("class", []):
            match = re.search(r"Página (\d+)", element.text)
            page = match.group(1) if match else "N/A"
            is_note = False

            if "Marcador" in element.text:
                highlights.append(f"\n{symbols['bookmark']} Página {page}\n")
            elif "Nota" in element.text:
                is_note = True

        elif "noteText" in element.get("class", []):
            text = element.text.strip()
            if is_note:
                highlights.append(f"\n    {symbols['note']} {text}\n")
                is_note = False
            else:
                highlights.append(f"\n{symbols['highlight']} {text} ({symbols['page']} {page})\n")

    return "".join(highlights).strip() if highlights else "No se encontraron notas en el archivo."

@app.route("/", methods=["GET", "POST"])
def index():
    formatted_text_default = None
    formatted_text_minimalista = None
    formatted_text_personalizado = None

    if request.method == "POST":
        file = request.files.get("file")
        if file and file.filename.endswith(".html"):
            file_path = os.path.join(UPLOAD_FOLDER, file.filename)
            file.save(file_path)
            print(f"Archivo recibido: {file.filename}")

            formatted_text_default = parse_highlights(file_path, "default")
            formatted_text_minimalista = parse_highlights(file_path, "minimalista")

            custom_symbols = {
                "highlight": request.form.get("custom_highlight", "📎"),
                "page": request.form.get("custom_page", "📖"),
                "bookmark": request.form.get("custom_bookmark", "🔖"),
                "note": request.form.get("custom_note", "🖊️")
            }
            formatted_text_personalizado = parse_highlights(file_path, "custom", custom_symbols)

            print("Texto procesado correctamente. Enviando a la plantilla.")
            return render_template("index.html", 
                                   formatted_text_default=formatted_text_default,
                                   formatted_text_minimalista=formatted_text_minimalista,
                                   formatted_text_personalizado=formatted_text_personalizado)

    print("No se recibió archivo válido o se accedió por GET.")
    return render_template("index.html", formatted_text_default=None, formatted_text_minimalista=None, formatted_text_personalizado=None)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)