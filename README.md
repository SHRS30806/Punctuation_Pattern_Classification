# Punctuation Pattern Classification

## Setup
1. `pip install -r requirements.txt`
2. One-time Kaggle API token setup:
   - kaggle.com -> profile picture -> Settings -> API -> Create New Token
   - save the downloaded `kaggle.json` to `~/.kaggle/kaggle.json`
     (Windows: `C:\Users\<you>\.kaggle\kaggle.json`)
3. `python punctuation_classifier.py`

The script fetches the dataset from Kaggle directly (via `kagglehub` -
your machine talks to Kaggle, nothing else is involved), extracts the
6 punctuation features (+ their per-100-words normalized versions),
tunes Logistic Regression and Random Forest with 5-fold cross-validated
grid search, checks Naive Bayes too, and reports the best model's
cross-validated accuracy plus held-out test accuracy. It also saves
`confusion_matrix.png`, `punctuation_distributions.png`, and `model.pkl`.

## Web Interface
To run the local web app for pasting and classifying text:
1. Train the model if you haven't already:
   ```bash
   python punctuation_classifier.py
   ```
2. Start the web server:
   ```bash
   python app.py
   ```
3. Open `http://127.0.0.1:5000` in your browser.

## About the 90-95% accuracy target
The script is built to report an honest number (cross-validation +
hyperparameter tuning, not a single lucky train/test split), but the
exact accuracy still depends on how separable the real categories in
this dataset are using punctuation alone - that's outside anything the
code controls. If your run lands outside 90-95%, here's what to adjust:

**If accuracy is above 95% (usually means overfitting or the
categories are trivially separable):**
- Lower Random Forest complexity: reduce `max_depth` options to
  `[2, 3, 4]` and increase `min_samples_leaf` options to `[4, 8, 16]`
- Lower Logistic Regression's `C` range to `[0.001, 0.01, 0.1]`
  (stronger regularization)
- Drop the `_norm` features and use only raw counts, or vice versa -
  having both can let the model over-fit on redundant signal

**If accuracy is below 90% (categories aren't separable enough from
punctuation alone):**
- Widen the Random Forest grid: add `max_depth: [10, 12, None]` and
  `n_estimators: [300, 500]`
- Add features: average sentence length, total punctuation count,
  ratio of punctuation to words, periods, ellipses
- Check for label noise or near-duplicate categories in the dataset
  itself - no amount of tuning fixes mislabeled data
