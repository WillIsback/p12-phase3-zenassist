from __future__ import annotations

from pathlib import Path
from pickle import load
from typing import Any, TypedDict

MODEL_PATH = Path(__file__).resolve().parents[2] / "model" / "best_ml_classifier.pkl"
_CLF_CACHE: Any | None = None


class ModelBundle(TypedDict):
    classifier: Any
    vectorizer: Any
    label_encoder: Any
    label_consolidation_map: dict[str, str]


class TagPrediction(TypedDict):
    tag: str
    confidence: float | None


API_TAG_MAP = {
    "Bank account": "Checking or savings account",
    "Credit card": "Credit card or prepaid card",
    "Credit reporting": "Other financial services",
    "Money transfer": "Money transfer, virtual currency, or money service",
    "Other financial service": "Other financial services",
    "Payday loan": "Payday loan, title loan, or personal loan",
}


def model_loader() -> ModelBundle:
    global _CLF_CACHE
    if _CLF_CACHE is None:
        with MODEL_PATH.open("rb") as f:
            bundle = load(f)
        if not isinstance(bundle, dict):
            raise TypeError("Le fichier modele doit contenir un dictionnaire.")
        _CLF_CACHE = bundle
    return _CLF_CACHE


def _normalize_tag(raw_tag: str, consolidation_map: dict[str, str]) -> str:
    consolidated_tag = consolidation_map.get(raw_tag, raw_tag)
    return API_TAG_MAP.get(consolidated_tag, consolidated_tag)


def get_tag(claim_text: str) -> TagPrediction:
    claim_text = claim_text.strip()
    if not claim_text:
        raise ValueError("Le texte de la réclamation ne peut pas être vide.")

    bundle = model_loader()
    classifier = bundle["classifier"]
    vectorizer = bundle["vectorizer"]
    label_encoder = bundle["label_encoder"]
    consolidation_map = bundle["label_consolidation_map"]

    features = vectorizer.transform([claim_text])

    if hasattr(classifier, "predict_proba"):
        probabilities = classifier.predict_proba(features)[0]
        aggregated_probabilities: dict[str, float] = {}
        for raw_label, probability in zip(label_encoder.classes_, probabilities):
            normalized_tag = _normalize_tag(str(raw_label), consolidation_map)
            aggregated_probabilities[normalized_tag] = aggregated_probabilities.get(
                normalized_tag, 0.0
            ) + float(probability)

        if aggregated_probabilities:
            tag, confidence = max(
                aggregated_probabilities.items(), key=lambda item: item[1]
            )
            return {"tag": tag, "confidence": confidence}

    predicted_label = classifier.predict(features)[0]
    predicted_index = int(predicted_label)
    raw_tag = str(label_encoder.classes_[predicted_index])
    return {"tag": _normalize_tag(raw_tag, consolidation_map), "confidence": None}
