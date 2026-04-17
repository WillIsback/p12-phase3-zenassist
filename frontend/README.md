# Claims Management System

## 🏗️ Tech Stack

- **Frontend**: Next.js 15.4.5 with React 19
- **Backend intégration**: Next.js Server Actions + API Routes, connectées au backend ML FastAPI
- **Database**: PostgreSQL with Docker
- **Language**: TypeScript
- **Styling**: CSS Modules

## ⚙️ Configuration

Copier le fichier d'exemple et le remplir :

```bash
cp .env.example .env
```

### Variables d'environnement

| Variable | Requis | Description |
| --- | --- | --- |
| `ML_BACKEND_BASE_URL` | Non | URL de base du backend FastAPI de classification (défaut: `http://127.0.0.1:8000`) |
| `ML_AUTOTAG_MIN_INTERVAL_MS` | Non | Intervalle minimum entre deux auto-tags côté Server Action (défaut: `1000`) |
| `DB_HOST` | Non | Hôte PostgreSQL (défaut: `localhost`) |
| `DB_PORT` | Non | Port PostgreSQL (défaut: `5555`) |
| `DB_NAME` | Non | Nom de la base (défaut: `dev_ia_p12`) |
| `DB_USER` | Non | Utilisateur PostgreSQL (défaut: `postgres`) |
| `DB_PASSWORD` | Non | Mot de passe PostgreSQL (défaut: `postgres`) |

### Flux d'inférence

Le frontend n'appelle plus de provider LLM directement. L'auto-tagging passe par la Server Action Next.js, qui appelle le backend Python FastAPI sur `POST /tag`.

Réponse attendue du backend:

```json
{
    "tag": "Credit card or prepaid card",
    "confidence": 0.99
}
```

Le `tag` est persisté en base PostgreSQL, puis l'UI affiche un toast enrichi avec la confiance lorsque disponible.

## 🚀 Quick Start

### Prerequisites

- Node.js
- Docker and Docker Compose

### 1. Clone and Install

```bash
npm install
```

### 2. Configuration

```bash
cp .env.example .env
# Éditer .env avec vos valeurs
```

### 3. Database Setup

```bash
# Start PostgreSQL in Docker
npm run db:start

# Seed with sample data
npm run db:reset
```

### 4. Start Development

```bash
npm run dev
```

## 📁 Project Structure

```text
src/
├── app/                   # Next.js App Router
│   ├── actions/           # Server Actions (classification via backend FastAPI)
│   └── api/               # API endpoints
├── components/            # UI components
├── constants/             # Taxonomie des tags
├── services/              # Services d'intégration backend
│   └── llm_cls.service.ts # Appel du backend FastAPI POST /tag
└── database/              # Database related code
    ├── client.ts          # PostgreSQL connection
    ├── queries.ts         # Database queries
    ├── seed.ts            # Database seeding
    └── seed-data.json     # Sample data
```

## 🛠️ Available Scripts

| Command            | Description                             |
|--------------------|-----------------------------------------|
| `npm run dev`      | Start development server with Turbopack |
| `npm run db:start` | Start PostgreSQL container              |
| `npm run db:stop`  | Stop PostgreSQL container               |
| `npm run db:reset` | Reset and seed database                 |
