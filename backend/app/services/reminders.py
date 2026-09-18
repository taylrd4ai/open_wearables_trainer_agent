"""Workout reminder messages with persona modes."""

from typing import Dict

PERSONA_MESSAGES: Dict[str, Dict[str, str]] = {
    "hard_ass": {
        "pre_workout": "Stop making excuses. Get your gear and show up.",
        "post_workout": "Done. But you left reps on the table. Next time push harder.",
    },
    "encouraging": {
        "pre_workout": "You are going to crush it today! Every step counts!",
        "post_workout": "Amazing work! Your body is thanking you right now!",
    },
    "balanced": {
        "pre_workout": "Time to train. Focus on form and progressive overload.",
        "post_workout": "Solid session logged. Recover well and hydrate.",
    },
    "standard": {
        "pre_workout": "Reminder: You have a workout scheduled.",
        "post_workout": "Workout complete. Log your session to track progress.",
    },
}


def get_pre_workout_message(persona: str = "standard") -> str:
    """Return pre-workout reminder message for the given persona."""
    valid = PERSONA_MESSAGES.get(persona, PERSONA_MESSAGES["standard"])
    return valid["pre_workout"]


def get_post_workout_message(persona: str = "standard") -> str:
    """Return post-workout reminder message for the given persona."""
    valid = PERSONA_MESSAGES.get(persona, PERSONA_MESSAGES["standard"])
    return valid["post_workout"]
