import pandas as pd
import joblib

from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(r"D:\legal\data\case_dataset.csv")

print("Dataset size:", len(df))

# =========================
# FEATURES / LABEL
# =========================
X = df["text"]
y = df["label"]

# =========================
# SPLIT
# =========================
X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42
)

# =========================
# VECTORIZER
# =========================
vectorizer = TfidfVectorizer(max_features=5000)

X_train_vec = vectorizer.fit_transform(X_train)
X_test_vec = vectorizer.transform(X_test)

# =========================
# MODEL
# =========================
model = LogisticRegression(max_iter=1000)
model.fit(X_train_vec, y_train)

# =========================
# EVALUATION
# =========================
acc = model.score(X_test_vec, y_test)
print("Accuracy:", acc)

# =========================
# SAVE
# =========================
joblib.dump(
    (vectorizer, model),
    r"D:\legal\models\real_case_model.pkl"
)

print("✅ Model saved")