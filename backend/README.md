# Claims Tagger API

API Python qui expose un modèle de classification pour taguer des réclamations clients. Le backend sert le modèle ML en local et est destiné à être consommé par un frontend Next.js lancé sur le port par défaut `3000`.

## Tech Stack

- **Backend**: Python 3.14, FastAPI
- **Modèle**: scikit-learn, modèle sérialisé dans `model/best_ml_classifier.pkl`
- **Tests**: pytest

## Prérequis

- Python 3.14+
- `uv`

## Installation

Depuis le dossier du backend:

```bash
uv sync
```

## Configuration

La configuration runtime est centralisée dans `app/settings.py` et peut être surchargée par variables d'environnement.

### Variables d'environnement

| Variable | Défaut | Description |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | Hôte d'écoute du backend |
| `APP_PORT` | `8000` | Port d'écoute du backend |
| `UVICORN_RELOAD` | `false` | Active le rechargement automatique en développement |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Origines autorisées pour le frontend Next.js |

Exemple:

```bash
export APP_HOST=127.0.0.1
export APP_PORT=8000
export UVICORN_RELOAD=true
export CORS_ORIGINS=http://localhost:3000,http://127.0.0.1:3000
```

## Démarrage

Lancer le serveur en local:

```bash
uv run main.py
```

Le backend est alors disponible sur `http://127.0.0.1:8000` par défaut.

## Endpoints

### `GET /`

Retourne un message simple pour vérifier que l'API est active.

Réponse:

```json
{ "message": "API est opérationnelle" }
```

### `GET /health`

Vérifie que l'API répond et que le modèle est chargé.

Réponse:

```json
{ "status": "ok", "model_ready": true }
```

### `POST /tag`

Classifie une réclamation texte et renvoie un tag métier compatible frontend.

Requête:

```json
{ "user_claim": "I was charged twice on my credit card" }
```

Réponse:

```json
{
	"tag": "Credit card or prepaid card",
	"confidence": 0.9927496423468359
}
```

Contraintes:

- `user_claim` doit être une chaîne non vide.
- `tag` appartient à la taxonomie exposée par l'API.
- `confidence` est soit un flottant, soit `null` si le score n'est pas disponible.

## Taxonomie exposée

Le backend normalise les sorties du modèle vers les tags suivants:

- `Debt collection`
- `Consumer Loan`
- `Credit card or prepaid card`
- `Mortgage`
- `Vehicle loan or lease`
- `Student loan`
- `Payday loan, title loan, or personal loan`
- `Checking or savings account`
- `Bank account or service`
- `Money transfer, virtual currency, or money service`
- `Money transfers`
- `Other financial services`

## Intégration frontend

Le frontend Next.js peut appeler `POST /tag` directement depuis le navigateur, à condition d'être servi depuis `http://localhost:3000` ou `http://127.0.0.1:3000`.

Exemple d'appel fetch:

```ts
const response = await fetch("http://127.0.0.1:8000/tag", {
	method: "POST",
	headers: {
		"Content-Type": "application/json",
	},
	body: JSON.stringify({ user_claim: claim }),
});

const data = await response.json();
```

## Tests

Lancer la suite E2E:

```bash
uv run pytest -q tests/test_e2e_pipeline.py
```

Pour afficher les tags prédits pendant le test:

```bash
uv run pytest -vv tests/test_e2e_pipeline.py
```

## Arborescence

```text
main.py                 # Point d'entrée FastAPI
app/
	api/endpoint.py       # Route /tag
	settings.py           # Configuration runtime
	src/model.py          # Chargement et inférence du modèle
data/mock_data.json     # Données utilisées par le test E2E
model/best_ml_classifier.pkl  # Bundle du modèle entraîné
tests/test_e2e_pipeline.py    # Test end-to-end
```

## Notes techniques

- Le fichier `model/best_ml_classifier.pkl` contient un bundle avec le classifier, le vectorizer, le label encoder et la table de consolidation des labels.
- Le backend charge le modèle au démarrage pour détecter rapidement une absence ou une incompatibilité du fichier.
- Certaines classes du modèle sont consolidées vers la taxonomie métier attendue par le frontend.
