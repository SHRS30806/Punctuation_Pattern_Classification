import docx
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# The 6 features strictly as specified in the problem statement
feature_names = [
    "commas",
    "semicolons",
    "colons",
    "question_marks",
    "exclaim_marks",
    "parentheses",
]


def count_punctuation(text):
    text = str(text)
    words = text.split()
    word_count = len(words)
    char_count = len(text)

    counts = {
        "commas": text.count(","),
        "semicolons": text.count(";"),
        "colons": text.count(":"),
        "question_marks": text.count("?"),
        "exclaim_marks": text.count("!"),
        "parentheses": text.count("(") + text.count(")"),
    }

    total_punctuation = 0
    for key in counts:
        total_punctuation = total_punctuation + counts[key]

    return counts, word_count, char_count, total_punctuation


def extract_text_from_upload(file_storage):
    """Extracts text from an uploaded .txt or .docx file."""
    filename = file_storage.filename.lower()
    if filename.endswith(".docx"):
        doc = docx.Document(file_storage)
        paragraphs = []
        for p in doc.paragraphs:
            if p.text:
                paragraphs.append(p.text)
        return "\n".join(paragraphs)
    else:
        raw_bytes = file_storage.read()
        try:
            return raw_bytes.decode("utf-8")
        except UnicodeDecodeError:
            return raw_bytes.decode("latin-1", errors="ignore")


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/read_file", methods=["POST"])
def read_file():
    """Receives an uploaded .txt or .docx file and returns its extracted text."""
    if "file" not in request.files:
        return jsonify({"error": "No file uploaded."}), 400

    uploaded_file = request.files["file"]
    if uploaded_file.filename == "":
        return jsonify({"error": "No file selected."}), 400

    try:
        extracted_text = extract_text_from_upload(uploaded_file)
        return jsonify({
            "success": True,
            "text": extracted_text,
            "filename": uploaded_file.filename
        })
    except Exception as e:
        return jsonify({"error": f"Failed to read file: {str(e)}"}), 500


@app.route("/predict", methods=["POST"])
def predict():
    """Analyzes text for punctuation patterns."""
    data = request.get_json()
    if data is None:
        return jsonify({"error": "No data received."}), 400

    text = data.get("text", "")
    if text == "":
        return jsonify({"error": "Please enter or upload some text to analyze."}), 400

    counts, word_count, char_count, total_punctuation = count_punctuation(text)

    return jsonify({
        "word_count": word_count,
        "char_count": char_count,
        "total_punctuation": total_punctuation,
        "counts": counts,
    })


if __name__ == "__main__":
    app.run(debug=True)
