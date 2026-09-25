"""
Seed script: populates the exercises table from the full exercise catalog
defined in fitness_coaching_handoff.docx (Machine, Dumbbell, and Home
templates). Safe to re-run — uses INSERT ... ON CONFLICT DO NOTHING so
existing rows are never overwritten.

Usage:
    cd backend
    python -m app.scripts.seed_exercises

    Or run once at startup by calling seed_exercises() from your Alembic
    env.py or a FastAPI lifespan event (after table creation).
"""

import asyncio
import logging

from sqlalchemy import text

from app.database import get_session
from app.models.exercise import Exercise

logger = logging.getLogger("seed_exercises")

# ---------------------------------------------------------------------------
# Full exercise catalog sourced from fitness_coaching_handoff.docx.
# Each entry: (name, aliases, template, equipment)
# ---------------------------------------------------------------------------

EXERCISES = [
    # --- Machine template ---
    (
        "Leg Press",
        ["leg press machine", "leg press"],
        "machine",
        "leg press machine",
    ),
    (
        "Seated Hamstring Curl",
        ["hamstring curl", "seated leg curl", "leg curl machine"],
        "machine",
        "seated hamstring curl machine",
    ),
    (
        "Leg Extension",
        ["leg extension machine", "quad extension"],
        "machine",
        "leg extension machine",
    ),
    (
        "Chest Press Machine",
        ["chest press", "machine chest press", "seated chest press"],
        "machine",
        "chest press machine",
    ),
    (
        "Seated Row",
        ["cable row", "machine row", "seated cable row", "seated machine row"],
        "machine",
        "cable/row machine",
    ),
    (
        "Lat Pulldown",
        ["lat pull down", "cable pulldown", "assisted pull-up", "assisted pullup"],
        "machine",
        "lat pulldown machine",
    ),
    (
        "Keiser Pallof Press",
        ["pallof press", "keiser pallof", "cable pallof press"],
        "machine",
        "Keiser Infinity / cable",
    ),
    (
        "Hip Abduction Machine",
        ["hip abduction", "abduction machine", "seated hip abduction"],
        "machine",
        "hip abduction machine",
    ),
    (
        "Single-Leg Calf Raise",
        ["calf raise", "single leg calf raise", "standing calf raise"],
        "machine",
        "bodyweight / step",
    ),
    (
        "Single-Leg Balance",
        ["single leg balance", "balance hold", "single leg stand"],
        "machine",
        "bodyweight",
    ),

    # --- Dumbbell template ---
    (
        "Goblet Box Squat",
        ["goblet squat", "box squat", "goblet box squat"],
        "dumbbell",
        "dumbbell / box or bench",
    ),
    (
        "DB Romanian Deadlift",
        ["romanian deadlift", "rdl", "db rdl", "dumbbell rdl", "dumbbell romanian deadlift"],
        "dumbbell",
        "dumbbells",
    ),
    (
        "DB Bench Press",
        ["dumbbell bench press", "db floor press", "dumbbell floor press", "db bench or floor press"],
        "dumbbell",
        "dumbbells / bench or floor",
    ),
    (
        "One-Arm DB Row",
        ["one arm row", "single arm row", "dumbbell row", "db row"],
        "dumbbell",
        "dumbbell",
    ),
    (
        "Seated DB Overhead Press",
        ["overhead press", "db overhead press", "dumbbell overhead press", "shoulder press"],
        "dumbbell",
        "dumbbells",
    ),
    (
        "Low Step-Up",
        ["step up", "stepup", "low stepup", "dumbbell step up"],
        "dumbbell",
        "bodyweight / low step",
    ),
    (
        "Suitcase Carry",
        ["suitcase carry", "db carry", "farmer carry", "dumbbell carry"],
        "dumbbell",
        "dumbbell",
    ),

    # --- Home template ---
    (
        "Chair Squat",
        ["chair squat", "sit to stand", "assisted squat"],
        "home",
        "bodyweight / chair",
    ),
    (
        "Banded Good Morning",
        ["good morning", "banded good morning", "band good morning"],
        "home",
        "resistance band",
    ),
    (
        "Incline Push-Up",
        ["incline pushup", "push up", "pushup", "counter push up"],
        "home",
        "bodyweight / counter or table",
    ),
    (
        "Banded Row",
        ["band row", "banded row", "resistance band row"],
        "home",
        "resistance band",
    ),
    (
        "Banded Lateral Walk",
        ["lateral walk", "banded lateral walk", "monster walk", "band walk"],
        "home",
        "resistance band",
    ),
    (
        "Banded Hamstring Curl",
        ["banded hamstring curl", "band leg curl", "resistance band hamstring curl"],
        "home",
        "resistance band",
    ),
    (
        "Banded Ankle Eversion",
        ["ankle eversion", "banded ankle eversion", "band ankle"],
        "home",
        "resistance band",
    ),
    (
        "Pallof Press",
        ["pallof", "pallof press", "band pallof press", "anti-rotation press"],
        "home",
        "resistance band / cable",
    ),
]


async def seed_exercises() -> None:
    """Insert all exercises, skipping any that already exist by name."""
    async with get_session() as session:
        inserted = 0
        skipped = 0
        for name, aliases, template, equipment in EXERCISES:
            existing = await session.execute(
                text("SELECT id FROM exercises WHERE name = :name"),
                {"name": name},
            )
            if existing.scalar_one_or_none() is not None:
                skipped += 1
                continue

            row = Exercise(
                name=name,
                aliases=aliases,
                template=template,
                equipment=equipment,
            )
            session.add(row)
            inserted += 1

        logger.info("seed_exercises: inserted=%d skipped=%d", inserted, skipped)
        print(f"seed_exercises: inserted={inserted} skipped={skipped}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    asyncio.run(seed_exercises())
