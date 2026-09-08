const form = document.getElementById("classify-form");
const textInput = document.getElementById("text-input");
const charCount = document.getElementById("char-count");
const wordCount = document.getElementById("word-count");
const clearBtn = document.getElementById("clear-btn");
const submitBtn = document.getElementById("submit-btn");
const errorBox = document.getElementById("error-message");
const resultsSection = document.getElementById("results");

const predictedCategory = document.getElementById("predicted-category");
const resWordCount = document.getElementById("res-word-count");
const resPunctCount = document.getElementById("res-punct-count");
const tableBody = document.getElementById("features-table-body");

const featureLabels = {
  commas: { label: "Commas", mark: "," },
  semicolons: { label: "Semicolons", mark: ";" },
  colons: { label: "Colons", mark: ":" },
  question_marks: { label: "Question Marks", mark: "?" },
  exclaim_marks: { label: "Exclamation Marks", mark: "!" },
  parentheses: { label: "Parentheses", mark: "( )" }
};

function updateCounts() {
  const text = textInput.value;
  charCount.textContent = `${text.length} characters`;

  const words = text.trim() ? text.trim().split(/\s+/).length : 0;
  wordCount.textContent = `${words} words`;
}

textInput.addEventListener("input", updateCounts);

clearBtn.addEventListener("click", () => {
  textInput.value = "";
  updateCounts();
  errorBox.style.display = "none";
  resultsSection.style.display = "none";
  textInput.focus();
});

form.addEventListener("submit", async (e) => {
  e.preventDefault();

  const text = textInput.value.trim();
  if (!text) {
    errorBox.textContent = "Please enter some text to classify.";
    errorBox.style.display = "block";
    resultsSection.style.display = "none";
    return;
  }

  errorBox.style.display = "none";
  submitBtn.disabled = true;
  submitBtn.textContent = "Classifying...";

  try {
    const res = await fetch("/predict", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ text })
    });

    const data = await res.json();

    if (!res.ok || data.error) {
      errorBox.textContent = data.error || "An error occurred during classification.";
      errorBox.style.display = "block";
      resultsSection.style.display = "none";
      return;
    }

    predictedCategory.textContent = data.category;
    resWordCount.textContent = data.word_count;
    resPunctCount.textContent = data.total_punctuation;

    tableBody.innerHTML = "";
    Object.keys(featureLabels).forEach((key) => {
      const info = featureLabels[key];
      const count = data.counts[key] || 0;
      const rate = data.rates[key] !== undefined ? data.rates[key].toFixed(2) : "0.00";

      const tr = document.createElement("tr");
      tr.innerHTML = `
        <td>${info.label}</td>
        <td><code>${info.mark}</code></td>
        <td>${count}</td>
        <td>${rate}</td>
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
    submitBtn.textContent = "Classify";
  }
});
