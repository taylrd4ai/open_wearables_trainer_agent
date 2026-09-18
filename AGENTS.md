# AGENTS.md — Open Wearables Trainer Agent

## Purpose
Local-first training platform that merges wearable data ingestion (heart rate,
GPS, sleep, recovery) with an AI-powered personal trainer agent. Ingests from
multiple providers (Whoop, Garmin, Oura, Polar, Apple Health, Fitbit, Suunto,
Ultrahuman, SensorBio, Strava), generates adaptive workout plans, logs
sessions, and delivers coaching through a React dashboard, FastAPI backend,
and Telegram bot interface.

Current phase: all 12 implementation tickets (T1–T12) complete. Codebase
audited, CRLF fixed across 621 Python files, 6 high-priority audit issues
resolved. Next milestone: production deployment.

"Done" for this phase: one wearable source streaming real biometric data
through the full pipeline (ingest → normalize → store → recommend → log →
display).

## Tech Stack
- Language(s): Python 3.11+ (backend), TypeScript/React (frontend)
- Frameworks/libraries:
  - Backend: FastAPI, SQLAlchemy, Alembic, Pydantic v2, aiohttp, uvicorn,
    numpy/pandas, pytest, celery (optional task queue)
  - Frontend: React, TanStack Router, Tailwind CSS, Vite, vitest
  - AI/ML: LangChain, LangGraph, Ollama (local LLM), pydantic-ai
  - Integrations: python-telegram-bot, garminconnect, bleak (BLE)
- Data storage: PostgreSQL (production), SQLite (dev/training.db), local JSON
  for config and exercise catalogs
- Execution environment: local machine (Windows 11); Docker optional
- Repo: local at
  `C:\Users\taylo\Desktop\taylrd4ai\open_wearables_trainer_agent\open_wearables_trainer_agent`
  (GitHub TBD)
- Research tool: available for wearable API docs, BLE protocol specs, and
  training-plan literature — wire in when needed

## Architecture
```
Wearable device (BLE HRM / Garmin / Whoop / Oura / Polar / Apple / Fitbit)
   ↓ (SDK, OAuth, or BLE)
backend/app/services/providers/     ← device adapters, one module per source
   ↓ (normalized biometric events)
backend/app/services/biometric/     ← get_biometric_summary(), provider detection
   ↓
backend/app/services/               ← core logic layer
  workout_planner_v2.py             ← generate_workout_v2() with T1-T4 integration
  recommendation_engine.py          ← 5-layer pipeline, TrainingObjective enum
  workout_logging_service.py        ← ExerciseEntry pydantic schema, POST /api/workout/complete
  location_equipment_service.py     ← LOCATIONS dict, 7 substitutions
  reminders.py                      ← pre/post workout messages, 4 persona modes
   ↓
trainer/coach_app/                  ← AI coach UI (merged from trainer_agent project)
  athlete_profile.json              ← user preferences, objectives, calibration
  data_model.py                     ← profile schema
  config.py                         ← coach configuration, OPEN_WEARABLES_BASE URL
  coach_ui.html                     ← HTML/CUI frontend
   ↓
PostgreSQL (training.db)            ← sessions, metrics, plans, users, connections
   ↓
FastAPI (port 8000)                 ← REST API + /docs Swagger UI
   ↓
React Frontend (port 3000)          ← DashboardPage, WorkoutHistory, BiometricCards
   ↓
Telegram Bridge (shared layer)      ← surface for Eric to query and adjust via Kestrel
```

### Ticket Map (T1–T12)
| Ticket | Component | Deliverable |
|--------|-----------|-------------|
| T1 | Biometric API | Whoop/Garmin clients, `get_summary()`, 5 metrics |
| T2 | User Preferences | Literal types, defaults.yaml, 4 objectives + 3 persona modes |
| T3 | Location/Equipment | LOCATIONS dict, 7 substitutions, workout type selection |
| T4 | Baseline Testing | exercise_calibration.json, 10 exercises × 4 objectives |
| T5 | Plan Generator MVP | Core MVP with basic flow |
| T5v2 | Plan Generator Enhanced | `generate_workout_v2()` — all T1–T4 integrations |
| T6 | Workout Logging | `POST /api/workout/complete`, DB models, progression flags |
| T7 | Recommendations | `generate_recommendation()` — 5-layer pipeline |
| T8 | Trainer Personality | Pre/post messages, 4 persona modes |
| T9 | Frontend Display | 4 React/TSX components consuming T1–T8 |
| T10 | Dashboard & History | DashboardPage, summary stats, biometrics, trainer messages |
| T11 | Testing Tools | test_harness, validate_data, api_test_client |
| T12 | Documentation | ARCHITECTURE.md, API_SPEC.md, QUICKSTART.md |

### Audit Fixes Applied
1. **Exercise catalog consolidated** — canonical 20-exercise source, no duplicates
2. **Biometric services created** — `get_biometric_summary()` with provider detection
3. **Enum validation safety** — try/except with graceful default on TrainingObjective
4. **Progression logic unified** — single shared `_check_progression()` function
5. **ExerciseEntry pydantic schema** — reps/weight/RPE validation on workout logging
6. **CRLF conversion** — 621 Python files converted to LF line endings

## Conventions
- Code style: PEP8, type hints on all public functions, ruff for lint/format
- Branching: feature branches off `main`, no direct commits to `main`
- Testing: pytest; unit tests for all data transforms, integration tests
  per device adapter (mock external APIs). T11 harness covers T6/T7/T8/T1/T5v2
- Commit messages: imperative, one-line summary
- All wearable API integrations must use async/await patterns
- Heart rate data validated before storage (range 30–220 bpm)
- GPS coordinates truncated to 4 decimal places (~11 m precision)
- Workout sessions must have start/end timestamps
- No secrets in code — all credentials in `.env` (git-ignored)
- System degrades gracefully: mock mode with synthetic data if no API keys

## Permissions and Autonomy
Inherits the reversibility rule from SOUL.md. Restated here for this
project explicitly:

**Do without asking:**
- Read/analyze any file in this repo
- Draft code, docs, or config changes locally (uncommitted)
- Run tests, linters, or local builds
- Create/update project-local skills for recurring tasks in this repo

**Never do without explicit approval:**
- `git commit`, `git push`, or opening/merging a PR
- Deploying or publishing any artifact
- Any external API call that creates, modifies, or deletes data outside this
  local/sandbox environment
- Deleting files that aren't trivially regenerable

**Security review gate:** before proposing any commit, deploy, or external
call that touches authentication or user data, run a quick self-check for
the obvious failure modes (injection, auth bypass, unvalidated input,
exposed secrets) and note what you checked.

## Known Gotchas
1. **BLE on Windows** — `bleak` library works but requires Bluetooth to be
   on and the device in pairing mode. Windows BLE stack is flaky with
   concurrent connections; one device at a time during dev.
2. **Garmin Connect** — `garminconnect` library uses unofficial API; may
   break on Garmin's auth changes. Pin the version.
3. **No live data yet** — device adapters are stubs until real API keys are
   configured. First real integration should target BLE HRM (no credentials,
   simplest path). System operates in mock mode without keys.
4. **Shared layer** — `../shared/` contains Hermes modes and Telegram
   bridge. Pin to VERSION 1.0.0. Don't edit shared/ from this project.
   Telegram bridge lives at root level as a common element across projects.
5. **.env credentials** — device API keys go in `.env` (git-ignored).
   Never hardcode. `.env.example` has the template. Production needs:
   `WHOOP_CLIENT_ID`, `WHOOP_CLIENT_SECRET`, `GARMIN_CLIENT_ID`,
   `GARMIN_CLIENT_SECRET`, `SECRET_KEY`, `MASTER_KEY`, `DATABASE_URL`.
6. **HERMES_HOME** — gateway must start with
   `HERMES_HOME=C:\Users\taylo\AppData\Local\hermes\profiles\chief-of-staff`
   or the Telegram bot falls back to generic identity instead of Kestrel.
7. **Trainer Agent merge** — `trainer/` directory contains the merged coach
   app from the standalone trainer_agent project. Coach calls the Open
   Wearables backend via `OPEN_WEARABLES_BASE` URL for biometric summaries
   and workout recommendations.
8. **CORS** — `cors_origins: list[AnyHttpUrl] = []` in `config.py`. Must be
   set for production domain or frontend can't reach backend.
9. **Database migrations** — Alembic configured in `backend/migrations/`.
   Run `alembic upgrade head` after any schema change.
10. **Python version mismatch** — python3=3.14.6, python=3.11.16,
    pip points to 3.11. Use `uv` or explicit venv paths to avoid conflicts.

## Skills
Check the local skills directory for this project before solving a
recurring problem from scratch — reuse or update an existing skill rather
than reinventing it. New non-trivial procedures discovered during work
should be saved as a skill, not just left in chat history.

Relevant existing skills:
- `telegram-hermes-setup` — Kestrel gateway configuration on Windows
- `systematic-debugging` — 4-phase root cause debugging
- `test-driven-development` — RED-GREEN-REFACTOR enforcement

## Project Boundaries
- **Open Wearables Trainer** (this project): fitness platform, biometric
  ingestion, workout planning, AI coaching, React dashboard
- **Token Economy** (separate project at `../../token_economy_project/`):
  kids' chore/point tracking for Lucas and Aidan. No child-related data
  belongs in this project.
- **Telegram Bridge** (shared layer at `../shared/`): common infrastructure
  used by both projects. Lives at root level, not inside either project.

## Status Log

### 2026-09-17
- Template updated with full design context from AGENTS.md and audit work.
- All 12 tickets (T1–T12) verified complete.
- 6 high-priority audit fixes applied and validated.
- CRLF conversion done (621 Python files).
- Trainer agent merged into project as `trainer/` directory.
- Telegram bridge designated as shared root-level component.
- Production readiness guide created (env, DB, Docker, monitoring).
- Next step: production `.env` with real credentials, PostgreSQL setup,
  pytest verification, Docker build test.

### 2026-09-12
- Project directory created under taylrd4ai layout. Shared layer referenced
  at ../shared/. Initial AGENTS.md stub written.
