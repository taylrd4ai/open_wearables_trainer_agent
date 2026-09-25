"""Seed data for the exercise catalog.

Location: app/models/exercise_seed.py

Sourced directly from fitness_coaching_handoff.docx -- Machine Template,
Dumbbell Template, and Home Template sections. "Bench Press" and "Squat"
are included as common aliases pointing at the closest calibrated
equivalents (Chest Press machine / Goblet Box Squat), since plain
barbell versions aren't in the client's current equipment list but
Telegram users will likely type them casually.
"""

from typing import Any, Dict, List

EXERCISE_SEED: List[Dict[str, Any]] = [
    # --- Machine Template ---
    {
        "name": "Leg Press",
        "aliases": ["leg press"],
        "template": "machine",
        "equipment": "leg press machine",
    },
    {
        "name": "Seated Hamstring Curl",
        "aliases": ["hamstring curl", "seated hamstring curl", "leg curl"],
        "template": "machine",
        "equipment": "seated hamstring curl machine",
    },
    {
        "name": "Leg Extension",
        "aliases": ["leg extension", "quad extension"],
        "template": "machine",
        "equipment": "leg extension machine",
    },
    {
        "name": "Chest Press (Machine)",
        "aliases": ["chest press", "bench press", "machine chest press", "bench"],
        "template": "machine",
        "equipment": "chest press machine",
    },
    {
        "name": "Seated Row",
        "aliases": ["seated row", "cable row", "machine row", "row"],
        "template": "machine",
        "equipment": "seated cable/machine row",
    },
    {
        "name": "Lat Pulldown",
        "aliases": ["lat pulldown", "pulldown"],
        "template": "machine",
        "equipment": "lat pulldown machine",
    },
    {
        "name": "Assisted Pull-Up",
        "aliases": ["assisted pull-up", "assisted pullup", "pull up"],
        "template": "machine",
        "equipment": "assisted pull-up machine",
    },
    {
        "name": "Keiser Pallof Press",
        "aliases": ["pallof press", "pallof", "keiser pallof"],
        "template": "machine",
        "equipment": "keiser infinity",
    },
    {
        "name": "Hip Abduction (Machine)",
        "aliases": ["hip abduction", "hip abductor"],
        "template": "machine",
        "equipment": "hip-abduction machine",
    },
    {
        "name": "Single-Leg Calf Raise",
        "aliases": ["calf raise", "single leg calf raise", "single-leg calf raise"],
        "template": "machine",
        "equipment": "bodyweight",
    },
    {
        "name": "Single-Leg Balance",
        "aliases": ["single leg balance", "balance", "single-leg balance"],
        "template": "machine",
        "equipment": "bodyweight",
    },
    {
        "name": "Overhead Press (Dumbbell/Machine)",
        "aliases": ["overhead press", "shoulder press", "db overhead press"],
        "template": "machine",
        "equipment": "dumbbell or machine",
    },
    # --- Dumbbell Template ---
    {
        "name": "Goblet Box Squat",
        "aliases": ["goblet box squat", "box squat", "squat", "goblet squat"],
        "template": "dumbbell",
        "equipment": "dumbbell + box/bench",
    },
    {
        "name": "DB Romanian Deadlift",
        "aliases": ["romanian deadlift", "rdl", "db rdl", "deadlift"],
        "template": "dumbbell",
        "equipment": "dumbbells",
    },
    {
        "name": "DB Bench/Floor Press",
        "aliases": ["db bench press", "floor press", "dumbbell bench press", "db floor press"],
        "template": "dumbbell",
        "equipment": "dumbbells",
    },
    {
        "name": "One-Arm DB Row",
        "aliases": ["one arm row", "db row", "one-arm dumbbell row", "single arm row"],
        "template": "dumbbell",
        "equipment": "dumbbell",
    },
    {
        "name": "Seated DB Overhead Press",
        "aliases": ["seated overhead press", "seated db press"],
        "template": "dumbbell",
        "equipment": "dumbbells",
    },
    {
        "name": "Low Step-Up",
        "aliases": ["step up", "step-up", "low step up"],
        "template": "dumbbell",
        "equipment": "bodyweight + low box",
    },
    {
        "name": "Suitcase Carry",
        "aliases": ["suitcase carry", "farmer carry"],
        "template": "dumbbell",
        "equipment": "dumbbell",
    },
    # --- Home Template ---
    {
        "name": "Chair Squat",
        "aliases": ["chair squat"],
        "template": "home",
        "equipment": "bodyweight + chair",
    },
    {
        "name": "Banded Good Morning",
        "aliases": ["banded good morning", "good morning"],
        "template": "home",
        "equipment": "resistance band",
    },
    {
        "name": "Incline Push-Up",
        "aliases": ["incline push up", "incline push-up", "push up"],
        "template": "home",
        "equipment": "countertop/table",
    },
    {
        "name": "Banded Row",
        "aliases": ["banded row"],
        "template": "home",
        "equipment": "resistance band",
    },
    {
        "name": "Banded Lateral Walk",
        "aliases": ["lateral walk", "banded lateral walk", "monster walk"],
        "template": "home",
        "equipment": "resistance band",
    },
    {
        "name": "Banded Hamstring Curl",
        "aliases": ["banded hamstring curl"],
        "template": "home",
        "equipment": "resistance band",
    },
    {
        "name": "Banded Ankle Eversion",
        "aliases": ["ankle eversion", "banded ankle eversion"],
        "template": "home",
        "equipment": "resistance band",
    },
    {
        "name": "Pallof Press (Band)",
        "aliases": ["banded pallof", "pallof press band"],
        "template": "home",
        "equipment": "resistance band",
    },
]
