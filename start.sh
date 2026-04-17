#!/usr/bin/env bash
set -euo pipefail

ROOT="$(cd "$(dirname "$0")" && pwd)"
BACKEND_DIR="$ROOT/backend"
FRONTEND_DIR="$ROOT/frontend"

# ── Colors ──────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
NC='\033[0m'

# ── PIDs to track ──────────────────────────────────────
BACKEND_PID=""
FRONTEND_PID=""

cleanup() {
  echo -e "\n${YELLOW}Shutting down...${NC}"
  [[ -n "$BACKEND_PID" ]]  && kill "$BACKEND_PID"  2>/dev/null && echo -e "${CYAN}[backend]${NC}  stopped"
  [[ -n "$FRONTEND_PID" ]] && kill "$FRONTEND_PID" 2>/dev/null && echo -e "${CYAN}[frontend]${NC} stopped"
  wait 2>/dev/null
  echo -e "${GREEN}Done.${NC}"
}
trap cleanup EXIT INT TERM

# ── Pre-flight checks ──────────────────────────────────
if ! command -v uv &>/dev/null; then
  echo -e "${RED}Error: uv is not installed. https://docs.astral.sh/uv/${NC}" && exit 1
fi
if ! command -v node &>/dev/null; then
  echo -e "${RED}Error: node is not installed.${NC}" && exit 1
fi
if [[ ! -f "$BACKEND_DIR/model/best_ml_classifier.pkl" ]]; then
  echo -e "${YELLOW}Warning: model/best_ml_classifier.pkl not found.${NC}"
  echo -e "${YELLOW}Download it from https://github.com/WillIsback/p12-phase1-zenassist/releases/latest${NC}"
  echo -e "${YELLOW}and place it in backend/model/.${NC}"
fi

# ── Backend (FastAPI / uvicorn) ─────────────────────────
echo -e "${CYAN}[backend]${NC}  Starting FastAPI on http://127.0.0.1:8000 ..."
(cd "$BACKEND_DIR" && uv run main.py) &
BACKEND_PID=$!

# ── Frontend (Next.js) ─────────────────────────────────
echo -e "${CYAN}[frontend]${NC} Starting Next.js on http://localhost:3000 ..."
(cd "$FRONTEND_DIR" && npm run dev) &
FRONTEND_PID=$!

# ── Wait for either process to exit ────────────────────
wait -n 2>/dev/null || true
