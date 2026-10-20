import os
import joblib

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression

MODEL_PATH = r"D:\legal\models\case_model.pkl"


def train_dummy_model():
    """
    Temporary training (since you don't yet have labeled case outcome data)
    """

    texts = [
        "strong evidence theft witness present",
        "clear fraud bank transaction proof",
        "no evidence weak case",
        "false accusation no proof",
        "clear contract breach documents available",
        "no documents weak claim"
    ]

    labels = [1, 1, 0, 0, 1, 0]  # 1 = win, 0 = lose

    vectorizer = TfidfVectorizer()
    X = vectorizer.fit_transform(texts)

    model = LogisticRegression()
    model.fit(X, labels)

    joblib.dump((vectorizer, model), MODEL_PATH)

    print("✅ Dummy model trained")


def load_model():
    if not os.path.exists(MODEL_PATH):
        train_dummy_model()

    return joblib.load(MODEL_PATH)


def predict_case(text: str):
    vectorizer, model = load_model()

    X = vectorizer.transform([text])
    prob = model.predict_proba(X)[0][1]

    return {
        "win_probability": round(prob * 100, 2),
        "risk_level": "High Chance" if prob > 0.6 else "Low Chance"
    }