"""Tests for workout logging service."""

import pytest
from pydantic import ValidationError
from uuid import uuid4

from app.services.workout_logging_service import (
    ExerciseEntrySchema,
    WorkoutLogRequest,
    log_workout,
    calculate_total_volume,
    calculate_average_rpe,
)


class TestExerciseEntryValidation:
    """Test Pydantic validation on ExerciseEntrySchema."""

    def test_valid_entry(self) -> None:
        entry = ExerciseEntrySchema(
            exercise_id=1, set_number=1, reps=10, weight=135.0, rpe=7
        )
        assert entry.reps == 10
        assert entry.weight == 135.0
        assert entry.rpe == 7

    def test_reps_too_low(self) -> None:
        with pytest.raises(ValidationError):
            ExerciseEntrySchema(exercise_id=1, set_number=1, reps=0, weight=100.0)

    def test_reps_too_high(self) -> None:
        with pytest.raises(ValidationError):
            ExerciseEntrySchema(exercise_id=1, set_number=1, reps=101, weight=100.0)

    def test_weight_negative(self) -> None:
        with pytest.raises(ValidationError):
            ExerciseEntrySchema(exercise_id=1, set_number=1, reps=5, weight=-1.0)

    def test_weight_too_high(self) -> None:
        with pytest.raises(ValidationError):
            ExerciseEntrySchema(exercise_id=1, set_number=1, reps=5, weight=2001.0)

    def test_rpe_out_of_range(self) -> None:
        with pytest.raises(ValidationError):
            ExerciseEntrySchema(
                exercise_id=1, set_number=1, reps=5, weight=100.0, rpe=11
            )

    def test_rpe_none_allowed(self) -> None:
        entry = ExerciseEntrySchema(
            exercise_id=1, set_number=1, reps=5, weight=100.0, rpe=None
        )
        assert entry.rpe is None

    def test_zero_weight_allowed(self) -> None:
        entry = ExerciseEntrySchema(
            exercise_id=1, set_number=1, reps=20, weight=0.0
        )
        assert entry.weight == 0.0


class TestWorkoutLogging:
    """Test workout log flow."""

    def test_calculate_total_volume(self, sample_exercise_entries: list) -> None:
        entries = [ExerciseEntrySchema(**e) for e in sample_exercise_entries]
        volume = calculate_total_volume(entries)
        expected = (10 * 135.0) + (8 * 155.0) + (12 * 95.0)
        assert volume == expected

    def test_calculate_average_rpe(self, sample_exercise_entries: list) -> None:
        entries = [ExerciseEntrySchema(**e) for e in sample_exercise_entries]
        avg = calculate_average_rpe(entries)
        assert avg == pytest.approx(7.0)

    def test_log_workout_success(self, sample_exercise_entries: list) -> None:
        uid = uuid4()
        entries = [ExerciseEntrySchema(**e) for e in sample_exercise_entries]
        request = WorkoutLogRequest(
            user_id=uid, location="gym", exercises=entries
        )
        result = log_workout(request)
        assert result["user_id"] == str(uid)
        assert result["location"] == "gym"
        assert result["exercise_count"] == 3
        assert result["total_volume"] > 0

    def test_log_workout_empty_exercises_fails(self) -> None:
        uid = uuid4()
        with pytest.raises(ValidationError):
            WorkoutLogRequest(user_id=uid, exercises=[])
