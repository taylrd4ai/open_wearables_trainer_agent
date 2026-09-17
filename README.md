# Open Wearables / Trainer Agent

Fitness wearable integration and training management system.

## Features

- **Heart rate zone training** — real-time HR monitoring with zone alerts
- **Workout tracking** — automatic rep counting and exercise detection
- **Recovery metrics** — HRV, resting heart rate, sleep quality analysis
- **Multi-device support** — Garmin, Fitbit, Polar, and generic BLE HRM

## Project Structure

```
open_wearables_trainer_agent/
├── src/
│   ├── wearables/       # Device API integrations
│   └── training/        # Workout logic and algorithms
├── tests/               # Unit and integration tests
├── .agents/             # AI agent configurations
├── .clinerules          # Cline-specific rules
└── AGENTS.md            # Project context for AI assistants
```

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Configure wearable credentials in `.env`:
   ```bash
   cp .env.example .env
   # Edit .env with your API keys
   ```

3. Run tests:
   ```bash
   pytest tests/
   ```

## Shared Layer

This project uses the shared Hermes layer at `../shared/` for:
- Agent modes (coding, audit, review)
- Telegram bridge integration
- Common utilities

Pin to version 1.0.0 (see `AGENTS.md`).

## Development

- **Coding mode** — implement new wearable integrations
- **Audit mode** — security review of device APIs
- **Review mode** — code quality and test coverage

## License

Private — internal use only.
