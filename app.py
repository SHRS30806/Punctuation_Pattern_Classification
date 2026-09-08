import os
import joblib
import pandas as pd
from flask import Flask, render_template, request, jsonify

app = Flask(__name__)

# The 12 features that the model expects in this exact order
feature_columns = [
    "commas",
    "semicolons",
    "colons",
    "question_marks",
    "exclaim_marks",
    "parentheses",
    "commas_norm",
    "semicolons_norm",
    "colons_norm",
    "question_marks_norm",
    "exclaim_marks_norm",
    "parentheses_norm",
]


def count_punctuation(text):
    text = str(text)
    words = text.split()
    word_count = len(words)
    if word_count == 0:
        word_count = 1

    # Count raw punctuation marks
    commas = text.count(",")
    semicolons = text.count(";")
    colons = text.count(":")
    question_marks = text.count("?")
    exclaim_marks = text.count("!")
    parentheses = text.count("(") + text.count(")")

    # Calculate rates per 100 words
    commas_norm = (commas / word_count) * 100
    semicolons_norm = (semicolons / word_count) * 100
    colons_norm = (colons / word_count) * 100
    question_marks_norm = (question_marks / word_count) * 100
    exclaim_marks_norm = (exclaim_marks / word_count) * 100
    parentheses_norm = (parentheses / word_count) * 100

    raw_counts = {
        "commas": commas,
        "semicolons": semicolons,
        "colons": colons,
        "question_marks": question_marks,
        "exclaim_marks": exclaim_marks,
        "parentheses": parentheses,
    }

    rates = {
        "commas": commas_norm,
        "semicolons": semicolons_norm,
        "colons": colons_norm,
        "question_marks": question_marks_norm,
        "exclaim_marks": exclaim_marks_norm,
        "parentheses": parentheses_norm,
    }

    all_features = {
        "commas": commas,
        "semicolons": semicolons,
        "colons": colons,
        "question_marks": question_marks,
        "exclaim_marks": exclaim_marks,
        "parentheses": parentheses,
        "commas_norm": commas_norm,
        "semicolons_norm": semicolons_norm,
        "colons_norm": colons_norm,
        "question_marks_norm": question_marks_norm,
        "exclaim_marks_norm": exclaim_marks_norm,
        "parentheses_norm": parentheses_norm,
    }

    return raw_counts, rates, all_features, word_count


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/predict", methods=["POST"])
def predict():
    if not os.path.exists("model.pkl"):
        return jsonify({
            "error": "model.pkl not found. Please run punctuation_classifier.py first."
        }), 400

    saved_data = joblib.load("model.pkl")
    model = saved_data["model"]
    scaler = saved_data["scaler"]
    le = saved_data["le"]

    data = request.get_json()
    if data is None:
        return jsonify({"error": "No data received."}), 400

    text = data.get("text", "")
    if text == "":
        return jsonify({"error": "Please enter some text to classify."}), 400

    raw_counts, rates, all_features, word_count = count_punctuation(text)

    # Put the features into a single-row DataFrame
    feature_row = pd.DataFrame([all_features], columns=feature_columns)

    # Scale the features using the saved scaler
    scaled_row = scaler.transform(feature_row)

    # Predict the category
    pred_number = model.predict(scaled_row)[0]
    category_name = le.inverse_transform([pred_number])[0]

    # Calculate total punctuation marks by adding each count
    total_punctuation = 0
    for key in raw_counts:
        total_punctuation = total_punctuation + raw_counts[key]

    return jsonify({
        "category": str(category_name),
        "word_count": word_count,
        "total_punctuation": total_punctuation,
        "counts": raw_counts,
        "rates": rates,
    })


if __name__ == "__main__":
    app.run(debug=True)
