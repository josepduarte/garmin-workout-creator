"""Tests for workout models"""

import pytest
from datetime import date
from pydantic import ValidationError

from garmin_workout_creator.models.workout import Workout
from garmin_workout_creator.models.step import StepType, DurationType, WorkoutStep
from garmin_workout_creator.models.target import TargetType, PaceTarget


class TestWorkout:
    """Tests for Workout model"""

    def test_valid_simple_workout(self):
        """Test creating a valid simple workout"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.COOLDOWN,
                duration_type=DurationType.TIME,
                duration_value=5,
                duration_unit="min",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Easy Run", steps=steps)
        assert workout.name == "Easy Run"
        assert workout.sport_type == "running"
        assert len(workout.steps) == 2

    def test_workout_with_date(self):
        """Test creating workout with scheduled date"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(
            name="Tuesday Run",
            steps=steps,
            scheduled_date=date(2025, 12, 26)
        )
        assert workout.scheduled_date == date(2025, 12, 26)

    def test_workout_with_notes(self):
        """Test creating workout with notes"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(
            name="Easy Run",
            steps=steps,
            notes="Focus on form and breathing"
        )
        assert workout.notes == "Focus on form and breathing"

    def test_workout_without_steps(self):
        """Test that workout must have at least one step"""
        with pytest.raises(ValidationError, match="must have at least one step"):
            Workout(name="Empty Workout", steps=[])

    def test_default_workout_name(self):
        """Test default workout name"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(steps=steps)
        assert workout.name == "Untitled Workout"

    def test_sport_type_normalization(self):
        """Test that sport type is normalized to lowercase"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Run", steps=steps, sport_type="RUNNING")
        assert workout.sport_type == "running"

    def test_get_total_distance_km_simple(self):
        """Test calculating total distance for simple workout"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.DISTANCE,
                duration_value=5,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.COOLDOWN,
                duration_type=DurationType.DISTANCE,
                duration_value=1000,
                duration_unit="m",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Distance Workout", steps=steps)
        assert workout.get_total_distance_km() == 7.0  # 1km + 5km + 1km

    def test_get_total_distance_km_with_repeat(self):
        """Test calculating total distance with repeat steps"""
        interval_step = WorkoutStep(
            step_type=StepType.INTERVAL,
            duration_type=DurationType.DISTANCE,
            duration_value=1,
            duration_unit="km",
            target_type=TargetType.PACE,
            pace_target=PaceTarget(min_seconds_per_km=285)
        )
        recovery_step = WorkoutStep(
            step_type=StepType.RECOVERY,
            duration_type=DurationType.DISTANCE,
            duration_value=500,
            duration_unit="m",
            target_type=TargetType.OPEN
        )
        repeat_step = WorkoutStep(
            step_type=StepType.REPEAT,
            duration_type=DurationType.OPEN,
            target_type=TargetType.OPEN,
            repeat_count=3,
            repeat_steps=[interval_step, recovery_step]
        )

        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            repeat_step,
            WorkoutStep(
                step_type=StepType.COOLDOWN,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Interval Workout", steps=steps)
        # 1km warmup + 3 * (1km + 0.5km) + 1km cooldown = 6.5km
        assert workout.get_total_distance_km() == 6.5

    def test_get_total_distance_km_mixed_durations(self):
        """Test that distance calculation returns None for mixed durations"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.TIME,
                duration_value=5,
                duration_unit="min",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Mixed Workout", steps=steps)
        assert workout.get_total_distance_km() is None

    def test_get_total_time_minutes_simple(self):
        """Test calculating total time for simple workout"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.TIME,
                duration_value=10,
                duration_unit="min",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.TIME,
                duration_value=20,
                duration_unit="min",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.COOLDOWN,
                duration_type=DurationType.TIME,
                duration_value=300,
                duration_unit="sec",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Time Workout", steps=steps)
        assert workout.get_total_time_minutes() == 35.0  # 10min + 20min + 5min

    def test_get_total_time_minutes_with_repeat(self):
        """Test calculating total time with repeat steps"""
        interval_step = WorkoutStep(
            step_type=StepType.INTERVAL,
            duration_type=DurationType.TIME,
            duration_value=4,
            duration_unit="min",
            target_type=TargetType.OPEN
        )
        recovery_step = WorkoutStep(
            step_type=StepType.RECOVERY,
            duration_type=DurationType.TIME,
            duration_value=2,
            duration_unit="min",
            target_type=TargetType.OPEN
        )
        repeat_step = WorkoutStep(
            step_type=StepType.REPEAT,
            duration_type=DurationType.OPEN,
            target_type=TargetType.OPEN,
            repeat_count=4,
            repeat_steps=[interval_step, recovery_step]
        )

        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.TIME,
                duration_value=10,
                duration_unit="min",
                target_type=TargetType.OPEN
            ),
            repeat_step,
            WorkoutStep(
                step_type=StepType.COOLDOWN,
                duration_type=DurationType.TIME,
                duration_value=5,
                duration_unit="min",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Time Intervals", steps=steps)
        # 10min warmup + 4 * (4min + 2min) + 5min cooldown = 39min
        assert workout.get_total_time_minutes() == 39.0

    def test_get_step_count_simple(self):
        """Test counting steps in simple workout"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.DISTANCE,
                duration_value=5,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.COOLDOWN,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Simple Run", steps=steps)
        assert workout.get_step_count() == 3

    def test_get_step_count_with_repeat(self):
        """Test counting steps with repeats"""
        interval_step = WorkoutStep(
            step_type=StepType.INTERVAL,
            duration_type=DurationType.DISTANCE,
            duration_value=1,
            duration_unit="km",
            target_type=TargetType.OPEN
        )
        recovery_step = WorkoutStep(
            step_type=StepType.RECOVERY,
            duration_type=DurationType.TIME,
            duration_value=2,
            duration_unit="min",
            target_type=TargetType.OPEN
        )
        repeat_step = WorkoutStep(
            step_type=StepType.REPEAT,
            duration_type=DurationType.OPEN,
            target_type=TargetType.OPEN,
            repeat_count=5,
            repeat_steps=[interval_step, recovery_step]
        )

        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            repeat_step,
            WorkoutStep(
                step_type=StepType.COOLDOWN,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Interval Run", steps=steps)
        # 1 warmup + (2 steps * 5 repeats) + 1 cooldown = 12 steps
        assert workout.get_step_count() == 12

    def test_to_summary_string_distance_workout(self):
        """Test summary string for distance-based workout"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.DISTANCE,
                duration_value=5,
                duration_unit="km",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.COOLDOWN,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="Easy 7k", steps=steps)
        summary = workout.to_summary_string()
        assert "Easy 7k" in summary
        assert "3 steps" in summary
        assert "7.0km" in summary

    def test_to_summary_string_time_workout(self):
        """Test summary string for time-based workout"""
        steps = [
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.TIME,
                duration_value=10,
                duration_unit="min",
                target_type=TargetType.OPEN
            ),
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.TIME,
                duration_value=20,
                duration_unit="min",
                target_type=TargetType.OPEN
            )
        ]

        workout = Workout(name="30 min run", steps=steps)
        summary = workout.to_summary_string()
        assert "30 min run" in summary
        assert "2 steps" in summary
        assert "30min" in summary
