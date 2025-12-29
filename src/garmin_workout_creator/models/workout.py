"""Workout model representing a complete workout"""

from datetime import date
from typing import List, Optional
from pydantic import BaseModel, Field, field_validator

from .step import WorkoutStep, StepType


class Workout(BaseModel):
    """Complete workout with steps and metadata"""

    name: str = Field(
        default="Untitled Workout",
        min_length=1,
        max_length=100,
        description="Workout name"
    )
    sport_type: str = Field(
        default="running",
        description="Sport type (running, cycling, swimming, etc.)"
    )
    steps: List[WorkoutStep] = Field(..., description="List of workout steps")
    scheduled_date: Optional[date] = Field(None, description="Date when workout is scheduled")
    notes: Optional[str] = Field(None, max_length=500, description="Additional notes")

    @field_validator('steps')
    @classmethod
    def validate_steps(cls, v: List[WorkoutStep]) -> List[WorkoutStep]:
        """Ensure workout has at least one step"""
        if not v or len(v) == 0:
            raise ValueError("Workout must have at least one step")
        return v

    @field_validator('sport_type')
    @classmethod
    def validate_sport_type(cls, v: str) -> str:
        """Validate and normalize sport type"""
        valid_sports = {
            'running', 'cycling', 'swimming', 'walking', 'hiking',
            'strength', 'cardio', 'other'
        }
        v_lower = v.lower()
        if v_lower not in valid_sports:
            # For MVP, we'll accept it but warn
            pass
        return v_lower

    def get_total_distance_km(self) -> Optional[float]:
        """
        Calculate total workout distance in kilometers

        Returns:
            Total distance in km, or None if not all steps are distance-based
        """
        total_meters = 0.0
        for step in self.steps:
            if step.step_type == StepType.REPEAT and step.repeat_steps:
                # Calculate distance for repeated steps
                repeat_distance = 0.0
                for repeat_step in step.repeat_steps:
                    step_meters = repeat_step.get_duration_in_meters()
                    if step_meters is None:
                        return None  # Can't calculate total if any step is not distance-based
                    repeat_distance += step_meters
                total_meters += repeat_distance * (step.repeat_count or 1)
            else:
                step_meters = step.get_duration_in_meters()
                if step_meters is None:
                    return None
                total_meters += step_meters

        return total_meters / 1000  # Convert to kilometers

    def get_total_time_minutes(self) -> Optional[float]:
        """
        Calculate total workout time in minutes

        Returns:
            Total time in minutes, or None if not all steps are time-based
        """
        total_seconds = 0.0
        for step in self.steps:
            if step.step_type == StepType.REPEAT and step.repeat_steps:
                # Calculate time for repeated steps
                repeat_time = 0.0
                for repeat_step in step.repeat_steps:
                    step_seconds = repeat_step.get_duration_in_seconds()
                    if step_seconds is None:
                        return None  # Can't calculate total if any step is not time-based
                    repeat_time += step_seconds
                total_seconds += repeat_time * (step.repeat_count or 1)
            else:
                step_seconds = step.get_duration_in_seconds()
                if step_seconds is None:
                    return None
                total_seconds += step_seconds

        return total_seconds / 60  # Convert to minutes

    def get_step_count(self) -> int:
        """
        Get total number of steps (flattened, accounting for repeats)

        Returns:
            Total number of individual steps
        """
        count = 0
        for step in self.steps:
            if step.step_type == StepType.REPEAT and step.repeat_steps:
                # Count each repeated step
                count += len(step.repeat_steps) * (step.repeat_count or 1)
            else:
                count += 1
        return count

    def to_summary_string(self) -> str:
        """
        Generate a summary string for the workout

        Returns:
            Human-readable summary

        Examples:
            >>> workout = Workout(
            ...     name="Morning Run",
            ...     steps=[...]
            ... )
            >>> workout.to_summary_string()
            'Morning Run: 5 steps, 10.0km'
        """
        parts = [self.name]

        # Add step count
        step_count = self.get_step_count()
        parts.append(f"{step_count} step{'s' if step_count != 1 else ''}")

        # Add distance or time if available
        distance = self.get_total_distance_km()
        if distance is not None:
            parts.append(f"{distance:.1f}km")
        else:
            time = self.get_total_time_minutes()
            if time is not None:
                parts.append(f"{time:.0f}min")

        return ": ".join([parts[0], ", ".join(parts[1:])])
