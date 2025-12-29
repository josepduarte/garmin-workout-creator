"""Workout step models"""

from enum import Enum
from typing import Optional, List
from pydantic import BaseModel, Field, field_validator, model_validator

from .target import TargetType, PaceTarget, HeartRateTarget, CadenceTarget


class StepType(str, Enum):
    """Type of workout step"""
    WARMUP = "warmup"
    INTERVAL = "interval"
    RECOVERY = "recovery"
    COOLDOWN = "cooldown"
    REPEAT = "repeat"


class DurationType(str, Enum):
    """How the duration of a step is measured"""
    DISTANCE = "distance"
    TIME = "time"
    OPEN = "open"  # Until lap button pressed


class WorkoutStep(BaseModel):
    """Individual workout step"""

    step_type: StepType = Field(..., description="Type of workout step")

    # Duration fields
    duration_type: DurationType = Field(..., description="How duration is measured")
    duration_value: Optional[float] = Field(
        None,
        gt=0,
        description="Duration value (distance in meters, time in seconds)"
    )
    duration_unit: Optional[str] = Field(
        None,
        description="Human-readable unit (km, m, min, sec)"
    )

    # Target fields
    target_type: TargetType = Field(..., description="Type of target for this step")
    pace_target: Optional[PaceTarget] = Field(None, description="Pace target if applicable")
    hr_target: Optional[HeartRateTarget] = Field(None, description="Heart rate target if applicable")
    cadence_target: Optional[CadenceTarget] = Field(None, description="Cadence target if applicable")

    # Optional description
    description: Optional[str] = Field(None, description="Human-readable description")

    # Repeat step fields
    repeat_count: Optional[int] = Field(
        None,
        ge=1,
        le=99,
        description="Number of repetitions (only for repeat steps)"
    )
    repeat_steps: Optional[List['WorkoutStep']] = Field(
        None,
        description="Steps to repeat (only for repeat steps)"
    )

    @model_validator(mode='after')
    def validate_duration_value(self) -> 'WorkoutStep':
        """Ensure duration_value is provided when duration_type is not OPEN"""
        if self.duration_type != DurationType.OPEN and self.duration_value is None:
            raise ValueError("duration_value is required when duration_type is not OPEN")
        if self.duration_type == DurationType.OPEN and self.duration_value is not None:
            raise ValueError("duration_value must be None when duration_type is OPEN")
        return self

    @model_validator(mode='after')
    def validate_target_consistency(self) -> 'WorkoutStep':
        """Ensure exactly one target is set based on target_type"""
        targets_set = sum([
            self.pace_target is not None,
            self.hr_target is not None,
            self.cadence_target is not None
        ])

        if self.target_type == TargetType.OPEN:
            if targets_set > 0:
                raise ValueError("No target should be set when target_type is OPEN")
        elif self.target_type == TargetType.PACE:
            if self.pace_target is None:
                raise ValueError("pace_target is required when target_type is PACE")
            if targets_set > 1:
                raise ValueError("Only pace_target should be set when target_type is PACE")
        elif self.target_type == TargetType.HEART_RATE:
            if self.hr_target is None:
                raise ValueError("hr_target is required when target_type is HEART_RATE")
            if targets_set > 1:
                raise ValueError("Only hr_target should be set when target_type is HEART_RATE")
        elif self.target_type == TargetType.CADENCE:
            if self.cadence_target is None:
                raise ValueError("cadence_target is required when target_type is CADENCE")
            if targets_set > 1:
                raise ValueError("Only cadence_target should be set when target_type is CADENCE")

        return self

    @model_validator(mode='after')
    def validate_repeat_fields(self) -> 'WorkoutStep':
        """Ensure repeat fields are consistent with step type"""
        if self.step_type == StepType.REPEAT:
            if self.repeat_count is None:
                raise ValueError("repeat_count is required for REPEAT steps")
            if not self.repeat_steps or len(self.repeat_steps) == 0:
                raise ValueError("repeat_steps is required and must not be empty for REPEAT steps")
        else:
            if self.repeat_count is not None:
                raise ValueError("repeat_count should only be set for REPEAT steps")
            if self.repeat_steps is not None:
                raise ValueError("repeat_steps should only be set for REPEAT steps")

        return self

    def get_duration_in_meters(self) -> Optional[float]:
        """Get duration in meters (for distance-based steps)"""
        if self.duration_type != DurationType.DISTANCE or self.duration_value is None:
            return None

        # Convert to meters based on unit
        if self.duration_unit in ['km', 'k', 'kilometers']:
            return self.duration_value * 1000
        elif self.duration_unit in ['m', 'meters', 'metre']:
            return self.duration_value
        elif self.duration_unit in ['mi', 'mile', 'miles']:
            return self.duration_value * 1609.34
        else:
            # Assume already in meters
            return self.duration_value

    def get_duration_in_seconds(self) -> Optional[float]:
        """Get duration in seconds (for time-based steps)"""
        if self.duration_type != DurationType.TIME or self.duration_value is None:
            return None

        # Convert to seconds based on unit
        if self.duration_unit in ['min', 'minute', 'minutes']:
            return self.duration_value * 60
        elif self.duration_unit in ['sec', 'second', 'seconds', 's']:
            return self.duration_value
        elif self.duration_unit in ['hr', 'hour', 'hours', 'h']:
            return self.duration_value * 3600
        else:
            # Assume already in seconds
            return self.duration_value

    def to_display_string(self) -> str:
        """
        Format step for TUI display

        Returns:
            Human-readable string representation

        Examples:
            >>> step = WorkoutStep(
            ...     step_type=StepType.WARMUP,
            ...     duration_type=DurationType.DISTANCE,
            ...     duration_value=1,
            ...     duration_unit="km",
            ...     target_type=TargetType.PACE,
            ...     pace_target=PaceTarget.from_pace_string("5:30")
            ... )
            >>> step.to_display_string()
            'Warmup: 1.0km @ 5:30/km'
        """
        if self.step_type == StepType.REPEAT:
            return f"Repeat {self.repeat_count}x"

        # Start with step type
        result = self.step_type.value.capitalize()

        # Add duration
        if self.duration_type == DurationType.OPEN:
            result += ": open"
        elif self.duration_value is not None and self.duration_unit:
            # Format as integer if it's a whole number
            if self.duration_value == int(self.duration_value):
                result += f": {int(self.duration_value)}{self.duration_unit}"
            else:
                result += f": {self.duration_value}{self.duration_unit}"

        # Add target
        if self.target_type == TargetType.PACE and self.pace_target:
            result += f" @ {self.pace_target.to_display_string()}"
        elif self.target_type == TargetType.HEART_RATE and self.hr_target:
            result += f" @ {self.hr_target.to_display_string()}"
        elif self.target_type == TargetType.CADENCE and self.cadence_target:
            result += f" @ {self.cadence_target.to_display_string()}"

        return result
