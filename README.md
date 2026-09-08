# 54. Punctuation Pattern Classification

## Problem Statement
Investigate whether punctuation patterns can distinguish different writing categories.

## Features
- Commas (`,`)
- Semicolons (`;`)
- Colons (`:`)
- Question marks (`?`)
- Exclamation marks (`!`)
- Parentheses (`( )`)

---

## Setup
1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
2. Run the script in the terminal:
   ```bash
   python punctuation_classifier.py
   ```

## Web Interface
1. Run the web server:
   ```bash
   python app.py
   ```
2. Open `http://127.0.0.1:5000` in your browser.

### Features
- **Pasting & Uploading**: Paste text directly into the text area or click **Upload .txt or .docx** to load any `.txt` or Word `.docx` document. (Uploaded files are only read for punctuation classification, not stored).
- **Pattern Analysis**: Displays:
  - Total Words
  - Total Characters
  - Total Punctuation Marks
  - Individual counts for each of the 6 punctuation features (Commas, Semicolons, Colons, Question marks, Exclamation marks, Parentheses).
