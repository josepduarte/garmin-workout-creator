"""Tests for target models"""

import pytest
from pydantic import ValidationError

from garmin_workout_creator.models.target import (
    TargetType,
    PaceTarget,
    HeartRateTarget,
    CadenceTarget,
)


class TestPaceTarget:
    """Tests for PaceTarget model"""

    def test_valid_pace(self):
        """Test creating a valid pace target"""
        target = PaceTarget(min_seconds_per_km=330)  # 5:30/km
        assert target.min_seconds_per_km == 330
        assert target.max_seconds_per_km is None

    def test_valid_pace_range(self):
        """Test creating a valid pace range"""
        target = PaceTarget(min_seconds_per_km=300, max_seconds_per_km=330)
        assert target.min_seconds_per_km == 300
        assert target.max_seconds_per_km == 330

    def test_invalid_pace_too_fast(self):
        """Test that pace below 1:00/km is rejected"""
        with pytest.raises(ValidationError):
            PaceTarget(min_seconds_per_km=30)

    def test_invalid_pace_too_slow(self):
        """Test that pace above 20:00/km is rejected"""
        with pytest.raises(ValidationError):
            PaceTarget(min_seconds_per_km=1300)

    def test_invalid_pace_range(self):
        """Test that max pace faster than min pace is rejected"""
        with pytest.raises(ValidationError):
            PaceTarget(min_seconds_per_km=330, max_seconds_per_km=300)

    def test_from_pace_string_valid(self):
        """Test parsing valid pace string"""
        target = PaceTarget.from_pace_string("5:30")
        assert target.min_seconds_per_km == 330

        target = PaceTarget.from_pace_string("4:45")
        assert target.min_seconds_per_km == 285

        target = PaceTarget.from_pace_string(" 6:00 ")
        assert target.min_seconds_per_km == 360

    def test_from_pace_string_invalid_format(self):
        """Test parsing invalid pace formats"""
        with pytest.raises(ValueError, match="format 'M:SS'"):
            PaceTarget.from_pace_string("530")

        with pytest.raises(ValueError, match="format 'M:SS'"):
            PaceTarget.from_pace_string("5-30")

        with pytest.raises(ValueError, match="exactly one ':'"):
            PaceTarget.from_pace_string("5:30:00")

    def test_from_pace_string_invalid_values(self):
        """Test parsing pace with invalid values"""
        with pytest.raises(ValueError, match="must be integers"):
            PaceTarget.from_pace_string("5:3a")

        with pytest.raises(ValueError, match="seconds must be < 60"):
            PaceTarget.from_pace_string("5:60")

    def test_to_pace_string(self):
        """Test converting pace to string"""
        target = PaceTarget(min_seconds_per_km=330)
        assert target.to_pace_string() == "5:30"

        target = PaceTarget(min_seconds_per_km=285)
        assert target.to_pace_string() == "4:45"

    def test_to_display_string(self):
        """Test display string formatting"""
        target = PaceTarget(min_seconds_per_km=330)
        assert target.to_display_string() == "5:30/km"

        target = PaceTarget(min_seconds_per_km=300, max_seconds_per_km=330)
        assert target.to_display_string() == "5:00-5:30/km"


class TestHeartRateTarget:
    """Tests for HeartRateTarget model"""

    def test_valid_hr(self):
        """Test creating a valid HR target"""
        target = HeartRateTarget(min_bpm=150)
        assert target.min_bpm == 150
        assert target.max_bpm is None

    def test_valid_hr_range(self):
        """Test creating a valid HR range"""
        target = HeartRateTarget(min_bpm=140, max_bpm=160)
        assert target.min_bpm == 140
        assert target.max_bpm == 160

    def test_invalid_hr_too_low(self):
        """Test that HR below 40 is rejected"""
        with pytest.raises(ValidationError):
            HeartRateTarget(min_bpm=30)

    def test_invalid_hr_too_high(self):
        """Test that HR above 220 is rejected"""
        with pytest.raises(ValidationError):
            HeartRateTarget(min_bpm=250)

    def test_invalid_hr_range(self):
        """Test that max HR lower than min HR is rejected"""
        with pytest.raises(ValidationError):
            HeartRateTarget(min_bpm=160, max_bpm=140)

    def test_to_display_string(self):
        """Test display string formatting"""
        target = HeartRateTarget(min_bpm=150)
        assert target.to_display_string() == "150 bpm"

        target = HeartRateTarget(min_bpm=140, max_bpm=160)
        assert target.to_display_string() == "140-160 bpm"


class TestCadenceTarget:
    """Tests for CadenceTarget model"""

    def test_valid_cadence(self):
        """Test creating a valid cadence target"""
        target = CadenceTarget(min_spm=180)
        assert target.min_spm == 180
        assert target.max_spm is None

    def test_valid_cadence_range(self):
        """Test creating a valid cadence range"""
        target = CadenceTarget(min_spm=170, max_spm=190)
        assert target.min_spm == 170
        assert target.max_spm == 190

    def test_invalid_cadence_range(self):
        """Test that max cadence lower than min is rejected"""
        with pytest.raises(ValidationError):
            CadenceTarget(min_spm=190, max_spm=170)

    def test_to_display_string(self):
        """Test display string formatting"""
        target = CadenceTarget(min_spm=180)
        assert target.to_display_string() == "180 spm"

        target = CadenceTarget(min_spm=170, max_spm=190)
        assert target.to_display_string() == "170-190 spm"
