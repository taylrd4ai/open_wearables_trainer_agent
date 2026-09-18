"""Tests for biometric services."""

import pytest

from app.services.biometric_services import (
    get_biometric_summary,
    _generate_mock_summary,
)


class TestMockFallback:
    """Test mock data generation when no providers are configured."""

    def test_mock_summary_structure(self, sample_user_id: str) -> None:
        summary = _generate_mock_summary(sample_user_id)
        assert summary["user_id"] == sample_user_id
        assert summary["is_mock"] is True
        assert summary["source_provider"] == "mock"
        assert "recovery_percent" in summary
        assert "hrv" in summary
        assert "strain_score" in summary

    @pytest.mark.asyncio
    async def test_get_summary_returns_mock_without_keys(
        self, sample_user_id: str
    ) -> None:
        """When no API keys are set, should return mock data."""
        result = await get_biometric_summary(sample_user_id)
        assert result["is_mock"] is True
        assert result["user_id"] == sample_user_id


class TestSummaryCalculations:
    """Test biometric summary value ranges."""

    def test_mock_values_in_range(self, sample_user_id: str) -> None:
        summary = _generate_mock_summary(sample_user_id)
        assert 0 <= summary["recovery_percent"] <= 100
        assert 30 <= summary["hrv"] <= 200
        assert summary["strain_score"] > 0

    @pytest.mark.asyncio
    async def test_summary_has_all_keys(self, sample_user_id: str) -> None:
        result = await get_biometric_summary(sample_user_id)
        expected_keys = {
            "user_id", "recovery_percent", "hrv", "strain_score",
            "vo2_max_estimate", "training_load", "source_provider", "is_mock",
        }
        assert expected_keys.issubset(set(result.keys()))
