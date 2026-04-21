# ZenAssist — Classification ML de réclamations consommateurs

Projet n°12 du parcours IA — OpenClassrooms, **Phase 3 : déploiement Machine Learning**.

## Contexte

**ZenAssist** est une plateforme de suivi de réclamations qui centralise la gestion des tickets de support pour plus de 200 entreprises. L'objectif est d'automatiser l'étiquetage des réclamations consommateurs (Consumer Financial Protection Bureau — CFPB) afin de les router vers le bon service.

### Historique du projet

| Phase | Objectif | Dépôt |
|-------|----------|-------|
| **Phase 1** | Comparaison de trois approches de classification (LLM zero-shot, ML classique, ModernBERT fine-tuné). Export du meilleur modèle ML via GitHub Actions. | [p12-phase1-zenassist](https://github.com/WillIsback/p12-phase1-zenassist) |
| **Phase 2** | Prototype de l'interface de gestion des réclamations avec classification LLM (Mistral / vLLM). | [p12-phase2-zenassist](https://github.com/WillIsback/p12-phase2-zenassist) |
| **Phase 3** | Remplacement du LLM par le modèle ML scikit-learn pour une montée en charge économiquement viable. Déploiement full-stack : API Python + frontend Next.js. | **Ce dépôt** |

### Résultats Phase 1 (1 000 tickets d'évaluation)

| Métrique | LLM (Qwen3.5) | ML (SGDClassifier) | ModernBERT |
|---|---|---|---|
| Accuracy | 0.820 | **0.828** | 0.787 |
| F1 macro | 0.662 | **0.685** | 0.636 |
| Latence moyenne | ~2 100 ms | **< 1 ms** | ~1 600 ms |

Le modèle ML classique (TF-IDF + SGDClassifier) offre de meilleures performances avec une latence quasi-nulle, ce qui justifie le passage en production.

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                   Frontend (Next.js 15)                     │
│  Page → Inboxes + Claim List + Tag Selector                │
│    ├─ fetchClaims() → GET /api/claims                      │
│    ├─ updateClaimTag() → PUT /api/claims/{id}/tag          │
│    └─ mlAutoTag() [Server Action] → classifyComplaint()    │
└───────────────────┬─────────────────────────┬───────────────┘
                    │                         │
          ┌────────▼────────┐       ┌────────▼──────────┐
          │  Backend FastAPI │       │  PostgreSQL       │
          │  POST /tag       │       │  (Docker Compose) │
          │  scikit-learn    │       │  port 5555        │
          └─────────────────┘       └───────────────────┘
```

**Flux d'auto-tagging** :
1. L'utilisateur clique sur le bouton ⚡ d'une réclamation
2. La Server Action Next.js appelle le backend FastAPI `POST /tag`
3. Le backend vectorise le texte (TF-IDF), prédit avec le classifieur ML et renvoie `{tag, confidence}`
4. Le tag est sauvegardé en base PostgreSQL
5. L'UI affiche un toast avec le tag et le score de confiance

## Tech Stack

| Composant | Technologie |
|-----------|------------|
| Backend API | Python 3.14, FastAPI, scikit-learn |
| Frontend | Next.js 15.4.5, React 19, TypeScript |
| Base de données | PostgreSQL 14 (Docker Compose) |
| Styling | CSS Modules |
| Linting | Ruff (Python), ESLint (TypeScript) |
| CI/CD | GitHub Actions |

## Prérequis

- Python 3.14+ et [uv](https://docs.astral.sh/uv/)
- Node.js 20+
- Docker et Docker Compose

## Installation et démarrage

### 1. Cloner le dépôt

```bash
git clone https://github.com/WillIsback/p12-phase3-zenassist.git
cd p12-phase3-zenassist
```

### 2. Télécharger le modèle ML

Le fichier `best_ml_classifier.pkl` n'est pas versionné dans git. Téléchargez-le depuis les [releases](https://github.com/WillIsback/p12-phase1-zenassist/releases/latest) du dépôt Phase 1 et placez-le dans `backend/model/` :

```bash
mkdir -p backend/model
# Télécharger best_ml_classifier.pkl depuis les releases GitHub Phase 1
# et le placer dans backend/model/
wget https://github.com/WillIsback/p12-phase1-zenassist/releases/download/v0.1.1/best_ml_classifier.pkl

mv best_ml_classifier.pkl backend/model/best_ml_classifier.pkl
```

### 3. Backend (FastAPI)

```bash
cd backend
uv sync
uv run main.py
```

Le backend est disponible sur `http://127.0.0.1:8000`.

### 4. Base de données (PostgreSQL)

```bash
cd frontend
cp .env.example .env
npm run db:start    # Démarre le conteneur PostgreSQL
npm run db:reset    # Crée la table et insère les données initiales
```

### 5. Frontend (Next.js)

```bash
cd frontend
npm install
npm run dev
```

Le frontend est disponible sur `http://localhost:3000`.

## Variables d'environnement

### Backend

| Variable | Défaut | Description |
|---|---|---|
| `APP_HOST` | `127.0.0.1` | Hôte d'écoute |
| `APP_PORT` | `8000` | Port d'écoute |
| `UVICORN_RELOAD` | `false` | Rechargement automatique (développement) |
| `CORS_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | Origines CORS autorisées |

### Frontend

| Variable | Défaut | Description |
|---|---|---|
| `ML_BACKEND_BASE_URL` | `http://127.0.0.1:8000` | URL du backend FastAPI |
| `ML_AUTOTAG_MIN_INTERVAL_MS` | `1000` | Intervalle minimum entre deux auto-tags (ms) |
| `DB_HOST` | `localhost` | Hôte PostgreSQL |
| `DB_PORT` | `5555` | Port PostgreSQL |
| `DB_NAME` | `dev_ia_p12` | Nom de la base |
| `DB_USER` | `postgres` | Utilisateur PostgreSQL |
| `DB_PASSWORD` | `postgres` | Mot de passe PostgreSQL |

## Endpoints API

### `GET /` — Vérification

```json
{ "message": "API est opérationnelle" }
```

### `GET /health` — État de santé

```json
{ "status": "ok", "model_ready": true }
```

### `POST /tag` — Classification d'une réclamation

**Requête** :
```json
{ "user_claim": "I was charged twice on my credit card" }
```

**Réponse** :
```json
{
  "tag": "Credit card or prepaid card",
  "confidence": 0.9927
}
```

## Taxonomie (12 catégories)

| Tag |
|-----|
| Debt collection |
| Consumer Loan |
| Credit card or prepaid card |
| Mortgage |
| Vehicle loan or lease |
| Student loan |
| Payday loan, title loan, or personal loan |
| Checking or savings account |
| Bank account or service |
| Money transfer, virtual currency, or money service |
| Money transfers |
| Other financial services |

## Tests

```bash
# Backend (nécessite le fichier .pkl dans backend/model/)
cd backend
uv run pytest -q tests/test_e2e_pipeline.py
```

## GitHub Actions

| Workflow | Déclencheur | Description |
|----------|-------------|-------------|
| **CI** | Push / PR sur `main` | Lint backend (Ruff) + lint et build frontend (ESLint + Next.js) |
| **Release** | Publication d'une release | Télécharge le modèle ML, exécute les tests, attache les artefacts à la release |

## Arborescence

```text
├── backend/
│   ├── main.py                        # Point d'entrée FastAPI
│   ├── pyproject.toml                 # Dépendances Python (uv)
│   ├── app/
│   │   ├── settings.py                # Configuration runtime
│   │   ├── api/endpoint.py            # Route POST /tag
│   │   └── src/model.py               # Chargement et inférence ML
│   ├── data/mock_data.json            # Données de test E2E
│   ├── model/                         # Répertoire du modèle (.pkl via releases)
│   └── tests/test_e2e_pipeline.py     # Tests end-to-end
├── frontend/
│   ├── package.json                   # Dépendances Node.js
│   ├── docker-compose.yml             # PostgreSQL
│   ├── src/
│   │   ├── app/                       # Next.js App Router
│   │   │   ├── actions/cls.action.ts  # Server Action (auto-tag ML)
│   │   │   └── api/claims/            # API Routes (CRUD claims)
│   │   ├── components/                # Composants UI React
│   │   ├── constants/tags.ts          # Taxonomie des 12 tags
│   │   ├── database/                  # Client PostgreSQL + seed
│   │   └── services/ml_cls.service.ts # Appel backend FastAPI
│   └── public/                        # Assets statiques
├── .github/workflows/                 # CI + Release
├── .gitignore
└── README.md
```

## Auteur

William Derue — [OpenClassrooms](https://openclassrooms.com/) parcours IA, projet 12
