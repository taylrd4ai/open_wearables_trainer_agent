# Open Wearables / Trainer Agent

This project integrates with fitness wearables and training systems.

## Project Scope
- Heart rate zone training
- Workout tracking and rep counting
- Recovery metrics
- Wearable device integration (HRM, GPS, etc.)

## Agent Mode
- `coding_mode` — for implementing new wearable integrations
- `audit_mode` — for security review of device APIs
- `review_mode` — for code review of fitness algorithms

## Shared Layer
This project uses the shared layer at `../shared/` (Hermes shared layer).
Pin to version 1.0.0 or update as needed.

## Setup
1. Add shared layer as git submodule or PYTHONPATH reference
2. Configure wearable device credentials in `.env`
3. Run `hermes chat --resume <session>` to start

## Current Status
- Initial project scaffold created
- Shared layer version 1.0.0
