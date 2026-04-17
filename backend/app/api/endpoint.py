from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.src.model import get_tag

ALLOWED_TAGS = [
    "Debt collection",
    "Consumer Loan",
    "Credit card or prepaid card",
    "Mortgage",
    "Vehicle loan or lease",
    "Student loan",
    "Payday loan, title loan, or personal loan",
    "Checking or savings account",
    "Bank account or service",
    "Money transfer, virtual currency, or money service",
    "Money transfers",
    "Other financial services",
]

router = APIRouter(tags=["tagging"])


class Claim(BaseModel):
    user_claim: str = Field(..., min_length=1)


class TagResponse(BaseModel):
    tag: str
    confidence: float | None = None


@router.post(
    "/tag",
    response_model=TagResponse,
    responses={
        422: {"description": "Texte de réclamation invalide."},
        500: {
            "description": "Erreur interne lors de l'inférence ou du chargement du modèle."
        },
    },
)
def create_item(claim: Claim):
    try:
        result = get_tag(claim.user_claim)
    except FileNotFoundError:
        raise HTTPException(
            status_code=500,
            detail="Fichier modele introuvable: model/best_ml_classifier.pkl",
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc))
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Erreur inference: {exc}")

    if result["tag"] not in ALLOWED_TAGS:
        raise HTTPException(
            status_code=500,
            detail=f"Tag predit non reconnu par l API: {result['tag']}",
        )
    return TagResponse(tag=result["tag"], confidence=result["confidence"])
