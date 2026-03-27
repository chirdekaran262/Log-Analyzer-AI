"""
ml_model.py
Unsupervised anomaly detection using TF-IDF ? TruncatedSVD ? IsolationForest.

FIX: sklearn Pipeline does not expose decision_function() end-to-end for
IsolationForest. We store the transformer and estimator separately so we can
call transform() on the pipeline prefix and score_samples() on the estimator.
"""

import os
import joblib
import numpy as np
from sklearn.ensemble import IsolationForest
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
from sklearn.pipeline import Pipeline

MODEL_DIR = "model"
MODEL_PATH = os.path.join(MODEL_DIR, "advanced_model.pkl")


def _build_pipeline(max_features: int, svd_components: int, contamination: float) -> Pipeline:
    n_components = min(svd_components, max_features - 1)
    return Pipeline(
        [
            ("tfidf", TfidfVectorizer(max_features=max_features, sublinear_tf=True)),
            ("svd", TruncatedSVD(n_components=n_components, random_state=42)),
            ("isolation", IsolationForest(contamination=contamination, random_state=42)),
        ]
    )


def train_model(logs: list[dict]):
    
    texts = []

    for log in logs:
        msg = log.get("message", "")
        level = log.get("level", "")
        
        # Combine level + message (IMPORTANT UPGRADE)
        combined = f"{level} {msg}"
        texts.append(combined)
    # Numerical features
    lengths = [len(t) for t in texts]
    num_features = np.array(lengths).reshape(-1, 1)

    pipeline = Pipeline([
        ("tfidf", TfidfVectorizer(max_features=200)),
        ("clf", IsolationForest(contamination=0.05))
    ])

    pipeline.fit(texts)

    joblib.dump(pipeline, MODEL_PATH)


def load_model() -> Pipeline | None:
    if not os.path.exists(MODEL_PATH):
        return None
    try:
        return joblib.load(MODEL_PATH)
    except Exception:
        return None


def predict_anomaly(logs: list[dict]) -> dict:
    
    model = load_model()

    if model is None:
        return {
            "prediction": "Model not trained",
            "anomaly_logs": 0,
            "avg_score": 0.0,
            "anomaly_ratio": 0.0,
        }

    texts = []

    for log in logs:
        msg = log.get("message", "")
        level = log.get("level", "")
        texts.append(f"{level} {msg}")
    if not texts:
        return {
            "prediction": "Normal",
            "anomaly_logs": 0,
            "avg_score": 0.0,
            "anomaly_ratio": 0.0,
        }

    try:
        # Predict labels: -1 = anomaly, 1 = normal
        predictions = model.predict(texts)  # works end-to-end ?

        # BUG FIX: Pipeline.decision_function() propagates through all steps but
        # IsolationForest.decision_function is not the same as score_samples in
        # older sklearn versions. Use the named step directly after transforming.
        tfidf_svd = Pipeline(model.steps[:-1])          # TF-IDF + SVD only
        X_transformed = tfidf_svd.transform(texts)
        iso: IsolationForest = model.named_steps["isolation"]
        scores = iso.score_samples(X_transformed)       # shape (n,)

    except Exception as exc:
        return {
            "prediction": "Model error",
            "anomaly_logs": 0,
            "avg_score": 0.0,
            "anomaly_ratio": 0.0,
            "error_detail": str(exc),
        }

    anomaly_count = int(np.sum(predictions == -1))
    anomaly_ratio = anomaly_count / len(logs) if logs else 0.0
    overall = "Anomaly" if anomaly_ratio > 0.30 else "Normal"
    avg_score = float(np.mean(scores))

    return {
        "prediction": overall,
        "anomaly_logs": anomaly_count,
        "avg_score": round(avg_score, 4),
        "anomaly_ratio": round(anomaly_ratio, 4),
    }