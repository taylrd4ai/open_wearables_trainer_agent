"""Test fixtures for Open Wearables backend."""

import pytest
from unittest.mock import AsyncMock, MagicMock


@pytest.fixture
def sample_user_id() -> str:
    """Return a test user ID."""
    return "550e8400-e29b-41d4-a716-446655440000"


@pytest.fixture
def sample_exercise_entries() -> list:
    """Return valid sample exercise entries for testing."""
    return [
        {"exercise_id": 1, "set_number": 1, "reps": 10, "weight": 135.0, "rpe": 7},
        {"exercise_id": 1, "set_number": 2, "reps": 8, "weight": 155.0, "rpe": 8},
        {"exercise_id": 4, "set_number": 1, "reps": 12, "weight": 95.0, "rpe": 6},
    ]


@pytest.fixture
def mock_biometrics() -> dict:
    """Return mock biometric summary."""
    return {
        "recovery_percent": 75.0,
        "hrv": 60.0,
        "strain_score": 12.0,
        "vo2_max_estimate": 45.0,
        "training_load": 350.0,
        "source_provider": "mock",
    }
