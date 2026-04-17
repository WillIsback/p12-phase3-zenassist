from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

from app.api.endpoint import router as tag_router
from app.src.model import model_loader
from app.settings import settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    model_loader()
    yield


app = FastAPI(title="Claim Tagger API", version="0.1.0", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(tag_router)


@app.get("/")
def root():
    return {"message": "API est opérationnelle"}


@app.get(
    "/health",
    responses={
        503: {"description": "Le modèle n'est pas disponible."},
    },
)
def health() -> dict[str, bool | str]:
    try:
        model_loader()
    except FileNotFoundError as exc:
        raise HTTPException(status_code=503, detail="Modèle introuvable") from exc
    except Exception as exc:
        raise HTTPException(
            status_code=503, detail=f"Modèle indisponible: {exc}"
        ) from exc

    return {"status": "ok", "model_ready": True}


def main() -> None:
    uvicorn.run(
        "main:app",
        host=settings.app_host,
        port=settings.app_port,
        reload=settings.uvicorn_reload,
    )


if __name__ == "__main__":
    main()
