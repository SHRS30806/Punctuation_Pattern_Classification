const classifyForm = document.getElementById("classify-form");
const textInput = document.getElementById("text-input");
const charCount = document.getElementById("char-count");
const wordCount = document.getElementById("word-count");
const clearBtn = document.getElementById("clear-btn");
const submitBtn = document.getElementById("submit-btn");
const fileUpload = document.getElementById("file-upload");
const errorBox = document.getElementById("error-message");
const resultsSection = document.getElementById("results");

const resWordCount = document.getElementById("res-word-count");
const resCharCount = document.getElementById("res-char-count");
const resPunctCount = document.getElementById("res-punct-count");
const tableBody = document.getElementById("features-table-body");

// The 6 features as specified in the problem statement
const featureLabels = {
  commas: { label: "Commas", mark: "," },
  semicolons: { label: "Semicolons", mark: ";" },
  colons: { label: "Colons", mark: ":" },
  question_marks: { label: "Question marks", mark: "?" },
  exclaim_marks: { label: "Exclamation marks", mark: "!" },
  parentheses: { label: "Parentheses", mark: "( )" }
};

function updateCounts() {
  const text = textInput.value;
  charCount.textContent = `${text.length} characters`;

  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  wordCount.textContent = `${words} words`;
}

textInput.addEventListener("input", updateCounts);

// Handle file upload for .txt and .docx documents
fileUpload.addEventListener("change", async (e) => {
  const file = e.target.files[0];
  if (!file) return;

  errorBox.style.display = "none";
  submitBtn.disabled = true;

  const formData = new FormData();
  formData.append("file", file);

  try {
    const res = await fetch("/read_file", {
      method: "POST",
      body: formData
    });

    const data = await res.json();
    if (!res.ok || data.error) {
      errorBox.textContent = data.error || "Failed to read document.";
      errorBox.style.display = "block";
      return;
    }

    textInput.value = data.text;
    updateCounts();
  } catch (err) {
    errorBox.textContent = "Failed to upload and extract document text.";
    errorBox.style.display = "block";
  } finally {
    submitBtn.disabled = false;
  }
});

clearBtn.addEventListener("click", () => {
  textInput.value = "";
  fileUpload.value = "";
  updateCounts();
  errorBox.style.display = "none";
  resultsSection.style.display = "none";
  textInput.focus();
});

// Classify / Analyze Form Submit
classifyForm.addEventListener("submit", async (e) => {
  e.preventDefault();

  const text = textInput.value.trim();
  if (!text) {
    errorBox.textContent = "Please enter text or upload a document to analyze.";
    errorBox.style.display = "block";
    resultsSection.style.display = "none";
    return;
  }

  errorBox.style.display = "none";
  submitBtn.disabled = true;
  submitBtn.textContent = "Analyzing...";

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    if (!res.ok || data.error) {
      errorBox.textContent = data.error || "An error occurred during analysis.";
      errorBox.style.display = "block";
      resultsSection.style.display = "none";
      return;
    }

    resWordCount.textContent = data.word_count.toLocaleString();
    resCharCount.textContent = data.char_count.toLocaleString();
    resPunctCount.textContent = data.total_punctuation.toLocaleString();

    tableBody.innerHTML = "";
    Object.keys(featureLabels).forEach((key) => {
      const info = featureLabels[key];
      const count = data.counts[key] || 0;

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${info.label}</td>
        <td><code>${info.mark}</code></td>
        <td>${count.toLocaleString()}</td>
      `;
      tableBody.appendChild(tr);
    });

    resultsSection.style.display = "block";
  } catch (err) {
    errorBox.textContent = "Could not connect to the server. Make sure app.py is running.";
    errorBox.style.display = "block";
    resultsSection.style.display = "none";
  } finally {
    submitBtn.disabled = false;
    submitBtn.textContent = "Analyze Punctuation";
  }
});
