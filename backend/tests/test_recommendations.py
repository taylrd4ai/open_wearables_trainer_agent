"""Tests for recommendation engine."""

import pytest

from app.services.recommendation_engine import (
    TrainingObjective,
    safe_objective,
    generate_recommendation,
)


class TestTrainingObjectiveEnum:
    """Test enum safety and parsing."""

    def test_valid_objectives(self) -> None:
        assert TrainingObjective("strength") == TrainingObjective.STRENGTH
        assert TrainingObjective("hypertrophy") == TrainingObjective.HYPERTROPHY
        assert TrainingObjective("endurance") == TrainingObjective.ENDURANCE
        assert TrainingObjective("power") == TrainingObjective.POWER

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            TrainingObjective("invalid_goal")

    def test_safe_objective_valid(self) -> None:
        assert safe_objective("strength") == TrainingObjective.STRENGTH

    def test_safe_objective_case_insensitive(self) -> None:
        assert safe_objective("  HYPERTROPHY  ") == TrainingObjective.HYPERTROPHY

    def test_safe_objective_invalid_defaults_hypertrophy(self) -> None:
        assert safe_objective("nonsense") == TrainingObjective.HYPERTROPHY

    def test_safe_objective_none_defaults(self) -> None:
        assert safe_objective(None) == TrainingObjective.HYPERTROPHY


class TestRecommendationPipeline:
    """Test the 5-layer generation pipeline."""

    def test_generate_strength(self) -> None:
        result = generate_recommendation("strength", "chest")
        assert result["objective"] == "strength"
        assert len(result["exercises"]) > 0
        for ex in result["exercises"]:
            assert ex["intensity_pct"] >= 85

    def test_generate_hypertrophy(self) -> None:
        result = generate_recommendation("hypertrophy", "back")
        assert result["objective"] == "hypertrophy"
        assert len(result["exercises"]) > 0

    def test_generate_endurance(self) -> None:
        result = generate_recommendation("endurance", "legs")
        assert result["objective"] == "endurance"
        for ex in result["exercises"]:
            assert ex["reps"] >= 15

    def test_generate_power(self) -> None:
        result = generate_recommendation("power", "full_body")
        assert result["objective"] == "power"

    def test_biometric_low_recovery_reduces_volume(
        self, mock_biometrics: dict
    ) -> None:
        mock_biometrics["recovery_percent"] = 30.0
        normal = generate_recommendation("hypertrophy", "chest")
        reduced = generate_recommendation(
            "hypertrophy", "chest", biometrics=mock_biometrics
        )
        normal_sets = sum(e["sets"] for e in normal["exercises"])
        reduced_sets = sum(e["sets"] for e in reduced["exercises"])
        assert reduced_sets <= normal_sets

    def test_progression_increases_intensity(self) -> None:
        base = generate_recommendation("strength", "chest", history_volume=0)
        progressed = generate_recommendation(
            "strength", "chest", history_volume=5000
        )
        base_intensity = base["exercises"][0]["intensity_pct"]
        prog_intensity = progressed["exercises"][0]["intensity_pct"]
        assert prog_intensity >= base_intensity

    def test_invalid_objective_still_generates(self) -> None:
        result = generate_recommendation("totally_wrong", "chest")
        assert result["objective"] == "hypertrophy"
        assert len(result["exercises"]) > 0
