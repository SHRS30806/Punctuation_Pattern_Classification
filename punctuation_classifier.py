import os
import pandas as pd
# pyrefly: ignore [missing-import]
import kagglehub
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

from sklearn.model_selection import train_test_split, StratifiedKFold, GridSearchCV, cross_val_score
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix

# 1. Fetch dataset from Kaggle

dataset_dir = kagglehub.dataset_download("takuji/punctuation-model-dataset")

# Find the csv file inside the dataset folder
all_files = os.listdir(dataset_dir)
csv_file = None
for file in all_files:
    if file.endswith(".csv"):
        csv_file = file
        break

csv_path = os.path.join(dataset_dir, csv_file)
df = pd.read_csv(csv_path)

# Rename the first and last columns to text and category
first_column_name = df.columns[0]
last_column_name = df.columns[-1]

df = df.rename(columns={first_column_name: "text", last_column_name: "category"})
df = df[["text", "category"]]
df = df.dropna()

# 2. Feature extraction

def extract_features(text):
    text = str(text)
    words = text.split()
    word_count = len(words)
    if word_count == 0:
        word_count = 1

    # Count each punctuation mark
    commas = text.count(",")
    semicolons = text.count(";")
    colons = text.count(":")
    question_marks = text.count("?")
    exclaim_marks = text.count("!")
    parentheses = text.count("(") + text.count(")")

    # Calculate the rate of each mark per 100 words
    commas_norm = (commas / word_count) * 100
    semicolons_norm = (semicolons / word_count) * 100
    colons_norm = (colons / word_count) * 100
    question_marks_norm = (question_marks / word_count) * 100
    exclaim_marks_norm = (exclaim_marks / word_count) * 100
    parentheses_norm = (parentheses / word_count) * 100

    return {
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

# Extract features for all rows in the dataset
feature_list = []
for text in df["text"]:
    row_features = extract_features(text)
    feature_list.append(row_features)

feat_df = pd.DataFrame(feature_list)

df = df.reset_index(drop=True)
data = pd.concat([df, feat_df], axis=1)

feature_cols = [
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

X = data[feature_cols]

le = LabelEncoder()
y = le.fit_transform(data["category"])

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

scaler = StandardScaler()
X_train_s = scaler.fit_transform(X_train)
X_test_s = scaler.transform(X_test)

# 3. Model training and hyperparameter tuning with 5-fold cross-validation

cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)

# Model 1: Logistic Regression
lr = LogisticRegression(max_iter=2000)
lr_params = {"C": [0.01, 0.1, 1, 10]}
lr_search = GridSearchCV(lr, lr_params, cv=cv, scoring="accuracy", n_jobs=-1)
lr_search.fit(X_train_s, y_train)
print("Logistic Regression best score:", lr_search.best_score_)
print("Logistic Regression best params:", lr_search.best_params_)

# Model 2: Random Forest
rf = RandomForestClassifier(random_state=42)
rf_params = {
    "n_estimators": [100, 200],
    "max_depth": [4, 6, 8, None],
    "min_samples_leaf": [1, 2, 4],
}
rf_search = GridSearchCV(rf, rf_params, cv=cv, scoring="accuracy", n_jobs=-1)
rf_search.fit(X_train_s, y_train)
print("Random Forest best score:", rf_search.best_score_)
print("Random Forest best params:", rf_search.best_params_)

# Model 3: Naive Bayes
nb = GaussianNB()
nb_scores = cross_val_score(nb, X_train_s, y_train, cv=cv, scoring="accuracy")
nb_score = nb_scores.mean()
print("Naive Bayes CV accuracy:", nb_score)

# Find the best model among the three
best_model = lr_search.best_estimator_
best_score = lr_search.best_score_
best_name = "Logistic Regression"

if rf_search.best_score_ > best_score:
    best_model = rf_search.best_estimator_
    best_score = rf_search.best_score_
    best_name = "Random Forest"

if nb_score > best_score:
    nb.fit(X_train_s, y_train)
    best_model = nb
    best_score = nb_score
    best_name = "Naive Bayes"

print("\nBest model:", best_name)
print("Best cross-validation accuracy:", best_score)

# 4. Final evaluation on held-out test set

preds = best_model.predict(X_test_s)
test_acc = accuracy_score(y_test, preds)
print("Held-out test accuracy:", test_acc)
print(classification_report(y_test, preds, target_names=le.classes_, zero_division=0))

# 5. Confusion matrix

cm = confusion_matrix(y_test, preds)
plt.figure(figsize=(6, 5))
sns.heatmap(
    cm,
    annot=True,
    fmt="d",
    cmap="Blues",
    xticklabels=le.classes_,
    yticklabels=le.classes_
)
plt.xlabel("Predicted")
plt.ylabel("Actual")
plt.title("Confusion Matrix - " + best_name)
plt.tight_layout()
plt.savefig("confusion_matrix.png")

# 6. Punctuation distribution per category plot

raw_features = [
    "commas",
    "semicolons",
    "colons",
    "question_marks",
    "exclaim_marks",
    "parentheses",
]

fig, axes = plt.subplots(2, 3, figsize=(14, 8))
flat_axes = axes.flatten()

for i in range(len(raw_features)):
    column = raw_features[i]
    ax = flat_axes[i]
    sns.boxplot(data=data, x="category", y=column, ax=ax)
    ax.set_title(column)
    ax.tick_params(axis="x", rotation=45)

plt.tight_layout()
plt.savefig("punctuation_distributions.png")

print("\nSaved confusion_matrix.png and punctuation_distributions.png")

# 7. Save trained model for the web interface

model_data = {
    "model": best_model,
    "scaler": scaler,
    "le": le,
}
joblib.dump(model_data, "model.pkl")
print("Saved model.pkl")
