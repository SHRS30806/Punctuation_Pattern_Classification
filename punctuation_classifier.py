import os
import docx

# 54. Punctuation Pattern Classification
# Problem Statement:
# Investigate whether punctuation patterns can distinguish different writing categories.
# Features:
# • Commas
# • Semicolons
# • Colons
# • Question marks
# • Exclamation marks
# • Parentheses

feature_names = [
    "commas",
    "semicolons",
    "colons",
    "question_marks",
    "exclaim_marks",
    "parentheses",
]


def extract_features(text):
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

    return {
        "word_count": word_count,
        "char_count": char_count,
        "total_punctuation": total_punctuation,
        "counts": counts,
    }


def analyze_file(file_path):
    """Extracts text and punctuation patterns from a .txt or .docx file."""
    if file_path.endswith(".docx"):
        doc = docx.Document(file_path)
        paragraphs = []
        for p in doc.paragraphs:
            if p.text:
                paragraphs.append(p.text)
        text = "\n".join(paragraphs)
    else:
        with open(file_path, "r", encoding="utf-8", errors="ignore") as f:
            text = f.read()

    return extract_features(text)


if __name__ == "__main__":
    sample_text = (
        "Hello, world! Can punctuation patterns be classified? "
        "Here are details: semicolons; colons; and parentheses (like this)."
    )

    print("Sample text:")
    print(sample_text)
    print("\n--- Punctuation Pattern Analysis ---")

    result = extract_features(sample_text)
    print("Total Words:", result["word_count"])
    print("Total Characters:", result["char_count"])
    print("Total Punctuation Marks:", result["total_punctuation"])
    print("\nFeature Counts:")
    for feature in feature_names:
        print(f"  {feature}: {result['counts'][feature]}")
