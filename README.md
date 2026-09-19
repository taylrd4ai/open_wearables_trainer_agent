# Open Wearables Trainer Agent

A wearable-driven training coach. It ingests biometric and workout data, generates training
recommendations and trainer messages, and surfaces everything in a web dashboard.

Built around an agent-first workflow: `AGENTS.md` defines the rules coding agents follow when
working in this repo, and `.clinerules` carries Cline-specific behavior.

## Stack

- **Backend** — FastAPI REST API (`backend/app`), Alembic migrations, pytest
- **Frontend** — React + TypeScript + Vite + Tailwind, served with an nginx-based Docker image
- **Orchestration** — Docker Compose (one command brings up the full stack)
- **CI** — GitHub Actions runs backend pytest and frontend typecheck on every push to `main`

## Repository layout

| Path | Purpose |
|---|---|
| `backend/app/` | FastAPI application: API routers (`api/v1/`), models, services, config, database |
| `backend/migrations/` | Alembic database migrations |
| `backend/tests/` | Backend pytest suite |
| `frontend/src/` | React app: routes, page components, hooks |
| `docker-compose.yml` | Full-stack local orchestration |
| `AGENTS.md` | Instructions and guardrails for AI coding agents in this repo |

## Quickstart

Prerequisites: Docker and Docker Compose.

```bash
git clone https://github.com/taylrd4ai/open_wearables_trainer_agent.git
cd open_wearables_trainer_agent
cp frontend/.env.example frontend/.env
docker compose up --build
```

Then open the dashboard at **http://localhost:3001**.

Required environment values are documented in `frontend/.env.example` and `backend/app/config.py`.

## Local development (without Docker)

Backend:

```bash
cd backend
python -m venv .venv && source .venv/bin/activate   # .venv\Scripts\activate on Windows
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload
```

Frontend:

```bash
cd frontend
npm ci
npm run dev
```

## Testing

- Backend: `cd backend && pytest`
- Frontend typecheck: `cd frontend && npx tsc --noEmit`
- Both run automatically in CI (`.github/workflows/ci.yml`)

## Working with coding agents

Read `AGENTS.md` first — it is the canonical contract for agent behavior (structure, test
requirements, definition of done). Keep it updated when conventions change; do not leave stale
copies lying around.

## License

MIT — see [LICENSE](LICENSE).
