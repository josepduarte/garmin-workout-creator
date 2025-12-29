"""Target types for workout steps (pace, heart rate, etc.)"""

from enum import Enum
from typing import Optional
from pydantic import BaseModel, Field, field_validator


class TargetType(str, Enum):
    """Type of target for a workout step"""
    PACE = "pace"
    HEART_RATE = "heart_rate"
    CADENCE = "cadence"
    OPEN = "open"  # No target


class PaceTarget(BaseModel):
    """Pace target in seconds per kilometer"""

    min_seconds_per_km: int = Field(
        ...,
        ge=60,  # Minimum 1:00/km (very fast)
        le=1200,  # Maximum 20:00/km (very slow)
        description="Minimum pace in seconds per kilometer"
    )
    max_seconds_per_km: Optional[int] = Field(
        None,
        ge=60,
        le=1200,
        description="Maximum pace in seconds per kilometer (for pace ranges)"
    )

    @field_validator('max_seconds_per_km')
    @classmethod
    def validate_pace_range(cls, v: Optional[int], info) -> Optional[int]:
        """Ensure max pace is slower than min pace"""
        if v is not None:
            min_pace = info.data.get('min_seconds_per_km')
            if min_pace and v < min_pace:
                raise ValueError("max_seconds_per_km must be >= min_seconds_per_km")
        return v

    @classmethod
    def from_pace_string(cls, pace: str) -> "PaceTarget":
        """
        Parse pace string like '5:30' into PaceTarget

        Args:
            pace: String in format 'M:SS' or 'MM:SS'

        Returns:
            PaceTarget instance

        Examples:
            >>> PaceTarget.from_pace_string("5:30")
            PaceTarget(min_seconds_per_km=330, max_seconds_per_km=None)
            >>> PaceTarget.from_pace_string("4:45")
            PaceTarget(min_seconds_per_km=285, max_seconds_per_km=None)
        """
        pace = pace.strip()
        if ':' not in pace:
            raise ValueError(f"Pace must be in format 'M:SS' or 'MM:SS', got: {pace}")

        parts = pace.split(':')
        if len(parts) != 2:
            raise ValueError(f"Pace must have exactly one ':', got: {pace}")

        try:
            minutes = int(parts[0])
            seconds = int(parts[1])
        except ValueError:
            raise ValueError(f"Pace minutes and seconds must be integers, got: {pace}")

        if seconds >= 60:
            raise ValueError(f"Pace seconds must be < 60, got: {seconds}")

        total_seconds = minutes * 60 + seconds
        return cls(min_seconds_per_km=total_seconds)

    def to_pace_string(self) -> str:
        """
        Convert to pace string format

        Returns:
            Pace string in format 'M:SS'

        Examples:
            >>> target = PaceTarget(min_seconds_per_km=330)
            >>> target.to_pace_string()
            '5:30'
        """
        minutes = self.min_seconds_per_km // 60
        seconds = self.min_seconds_per_km % 60
        return f"{minutes}:{seconds:02d}"

    def to_display_string(self) -> str:
        """Get display string for TUI"""
        if self.max_seconds_per_km:
            max_min = self.max_seconds_per_km // 60
            max_sec = self.max_seconds_per_km % 60
            return f"{self.to_pace_string()}-{max_min}:{max_sec:02d}/km"
        return f"{self.to_pace_string()}/km"


class HeartRateTarget(BaseModel):
    """Heart rate target in beats per minute"""

    min_bpm: int = Field(
        ...,
        ge=40,  # Very low resting HR
        le=220,  # Theoretical max HR
        description="Minimum heart rate in BPM"
    )
    max_bpm: Optional[int] = Field(
        None,
        ge=40,
        le=220,
        description="Maximum heart rate in BPM (for HR zones)"
    )

    @field_validator('max_bpm')
    @classmethod
    def validate_hr_range(cls, v: Optional[int], info) -> Optional[int]:
        """Ensure max HR is higher than min HR"""
        if v is not None:
            min_hr = info.data.get('min_bpm')
            if min_hr and v < min_hr:
                raise ValueError("max_bpm must be >= min_bpm")
        return v

    def to_display_string(self) -> str:
        """Get display string for TUI"""
        if self.max_bpm:
            return f"{self.min_bpm}-{self.max_bpm} bpm"
        return f"{self.min_bpm} bpm"


class CadenceTarget(BaseModel):
    """Cadence target in steps per minute"""

    min_spm: int = Field(
        ...,
        ge=60,  # Very slow cadence
        le=220,  # Very fast cadence
        description="Minimum cadence in steps per minute"
    )
    max_spm: Optional[int] = Field(
        None,
        ge=60,
        le=220,
        description="Maximum cadence in steps per minute"
    )

    @field_validator('max_spm')
    @classmethod
    def validate_cadence_range(cls, v: Optional[int], info) -> Optional[int]:
        """Ensure max cadence is higher than min cadence"""
        if v is not None:
            min_cadence = info.data.get('min_spm')
            if min_cadence and v < min_cadence:
                raise ValueError("max_spm must be >= min_spm")
        return v

    def to_display_string(self) -> str:
        """Get display string for TUI"""
        if self.max_spm:
            return f"{self.min_spm}-{self.max_spm} spm"
        return f"{self.min_spm} spm"
