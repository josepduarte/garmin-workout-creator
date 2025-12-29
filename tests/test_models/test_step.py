"""Tests for workout step models"""

import pytest
from pydantic import ValidationError

from garmin_workout_creator.models.step import StepType, DurationType, WorkoutStep
from garmin_workout_creator.models.target import TargetType, PaceTarget, HeartRateTarget


class TestWorkoutStep:
    """Tests for WorkoutStep model"""

    def test_valid_warmup_step(self):
        """Test creating a valid warmup step"""
        step = WorkoutStep(
            step_type=StepType.WARMUP,
            duration_type=DurationType.DISTANCE,
            duration_value=1000,
            duration_unit="m",
            target_type=TargetType.PACE,
            pace_target=PaceTarget(min_seconds_per_km=330)
        )
        assert step.step_type == StepType.WARMUP
        assert step.duration_value == 1000
        assert step.pace_target.min_seconds_per_km == 330

    def test_valid_interval_step_with_hr(self):
        """Test creating an interval step with heart rate target"""
        step = WorkoutStep(
            step_type=StepType.INTERVAL,
            duration_type=DurationType.TIME,
            duration_value=5,
            duration_unit="min",
            target_type=TargetType.HEART_RATE,
            hr_target=HeartRateTarget(min_bpm=160, max_bpm=175)
        )
        assert step.step_type == StepType.INTERVAL
        assert step.hr_target.min_bpm == 160

    def test_valid_open_step(self):
        """Test creating a step with open duration"""
        step = WorkoutStep(
            step_type=StepType.COOLDOWN,
            duration_type=DurationType.OPEN,
            target_type=TargetType.OPEN
        )
        assert step.duration_type == DurationType.OPEN
        assert step.target_type == TargetType.OPEN

    def test_valid_repeat_step(self):
        """Test creating a valid repeat step"""
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
            duration_type=DurationType.TIME,
            duration_value=2,
            duration_unit="min",
            target_type=TargetType.OPEN
        )

        repeat = WorkoutStep(
            step_type=StepType.REPEAT,
            duration_type=DurationType.OPEN,  # Repeats don't have their own duration
            target_type=TargetType.OPEN,
            repeat_count=5,
            repeat_steps=[interval_step, recovery_step]
        )

        assert repeat.repeat_count == 5
        assert len(repeat.repeat_steps) == 2

    def test_missing_duration_value(self):
        """Test that duration_value is required for non-OPEN durations"""
        with pytest.raises(ValidationError, match="duration_value is required"):
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.DISTANCE,
                target_type=TargetType.OPEN
            )

    def test_duration_value_with_open_duration(self):
        """Test that duration_value must be None for OPEN duration"""
        with pytest.raises(ValidationError, match="must be None when duration_type is OPEN"):
            WorkoutStep(
                step_type=StepType.WARMUP,
                duration_type=DurationType.OPEN,
                duration_value=1000,
                target_type=TargetType.OPEN
            )

    def test_missing_pace_target(self):
        """Test that pace_target is required when target_type is PACE"""
        with pytest.raises(ValidationError, match="pace_target is required"):
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.PACE
            )

    def test_missing_hr_target(self):
        """Test that hr_target is required when target_type is HEART_RATE"""
        with pytest.raises(ValidationError, match="hr_target is required"):
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.TIME,
                duration_value=5,
                duration_unit="min",
                target_type=TargetType.HEART_RATE
            )

    def test_multiple_targets_set(self):
        """Test that only one target can be set"""
        with pytest.raises(ValidationError, match="Only pace_target should be set"):
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.PACE,
                pace_target=PaceTarget(min_seconds_per_km=285),
                hr_target=HeartRateTarget(min_bpm=160)
            )

    def test_target_set_for_open_target_type(self):
        """Test that no targets should be set for OPEN target_type"""
        with pytest.raises(ValidationError, match="No target should be set"):
            WorkoutStep(
                step_type=StepType.RECOVERY,
                duration_type=DurationType.TIME,
                duration_value=2,
                duration_unit="min",
                target_type=TargetType.OPEN,
                pace_target=PaceTarget(min_seconds_per_km=360)
            )

    def test_repeat_without_count(self):
        """Test that repeat_count is required for REPEAT steps"""
        with pytest.raises(ValidationError, match="repeat_count is required"):
            WorkoutStep(
                step_type=StepType.REPEAT,
                duration_type=DurationType.OPEN,
                target_type=TargetType.OPEN,
                repeat_steps=[
                    WorkoutStep(
                        step_type=StepType.INTERVAL,
                        duration_type=DurationType.DISTANCE,
                        duration_value=1,
                        duration_unit="km",
                        target_type=TargetType.OPEN
                    )
                ]
            )

    def test_repeat_without_steps(self):
        """Test that repeat_steps is required for REPEAT steps"""
        with pytest.raises(ValidationError, match="repeat_steps is required"):
            WorkoutStep(
                step_type=StepType.REPEAT,
                duration_type=DurationType.OPEN,
                target_type=TargetType.OPEN,
                repeat_count=5
            )

    def test_repeat_count_on_non_repeat(self):
        """Test that repeat_count should only be on REPEAT steps"""
        with pytest.raises(ValidationError, match="should only be set for REPEAT"):
            WorkoutStep(
                step_type=StepType.INTERVAL,
                duration_type=DurationType.DISTANCE,
                duration_value=1,
                duration_unit="km",
                target_type=TargetType.OPEN,
                repeat_count=5
            )

    def test_get_duration_in_meters(self):
        """Test converting distance to meters"""
        step = WorkoutStep(
            step_type=StepType.WARMUP,
            duration_type=DurationType.DISTANCE,
            duration_value=1,
            duration_unit="km",
            target_type=TargetType.OPEN
        )
        assert step.get_duration_in_meters() == 1000

        step = WorkoutStep(
            step_type=StepType.WARMUP,
            duration_type=DurationType.DISTANCE,
            duration_value=500,
            duration_unit="m",
            target_type=TargetType.OPEN
        )
        assert step.get_duration_in_meters() == 500

    def test_get_duration_in_meters_time_based(self):
        """Test that time-based steps return None for distance"""
        step = WorkoutStep(
            step_type=StepType.INTERVAL,
            duration_type=DurationType.TIME,
            duration_value=5,
            duration_unit="min",
            target_type=TargetType.OPEN
        )
        assert step.get_duration_in_meters() is None

    def test_get_duration_in_seconds(self):
        """Test converting time to seconds"""
        step = WorkoutStep(
            step_type=StepType.INTERVAL,
            duration_type=DurationType.TIME,
            duration_value=5,
            duration_unit="min",
            target_type=TargetType.OPEN
        )
        assert step.get_duration_in_seconds() == 300

        step = WorkoutStep(
            step_type=StepType.RECOVERY,
            duration_type=DurationType.TIME,
            duration_value=120,
            duration_unit="sec",
            target_type=TargetType.OPEN
        )
        assert step.get_duration_in_seconds() == 120

    def test_get_duration_in_seconds_distance_based(self):
        """Test that distance-based steps return None for time"""
        step = WorkoutStep(
            step_type=StepType.WARMUP,
            duration_type=DurationType.DISTANCE,
            duration_value=1,
            duration_unit="km",
            target_type=TargetType.OPEN
        )
        assert step.get_duration_in_seconds() is None

    def test_to_display_string_warmup(self):
        """Test display string for warmup step"""
        step = WorkoutStep(
            step_type=StepType.WARMUP,
            duration_type=DurationType.DISTANCE,
            duration_value=1,
            duration_unit="km",
            target_type=TargetType.PACE,
            pace_target=PaceTarget(min_seconds_per_km=330)
        )
        assert step.to_display_string() == "Warmup: 1km @ 5:30/km"

    def test_to_display_string_interval_with_hr(self):
        """Test display string for interval with HR target"""
        step = WorkoutStep(
            step_type=StepType.INTERVAL,
            duration_type=DurationType.TIME,
            duration_value=5,
            duration_unit="min",
            target_type=TargetType.HEART_RATE,
            hr_target=HeartRateTarget(min_bpm=165)
        )
        assert step.to_display_string() == "Interval: 5min @ 165 bpm"

    def test_to_display_string_repeat(self):
        """Test display string for repeat step"""
        step = WorkoutStep(
            step_type=StepType.REPEAT,
            duration_type=DurationType.OPEN,
            target_type=TargetType.OPEN,
            repeat_count=3,
            repeat_steps=[
                WorkoutStep(
                    step_type=StepType.INTERVAL,
                    duration_type=DurationType.DISTANCE,
                    duration_value=1,
                    duration_unit="km",
                    target_type=TargetType.OPEN
                )
            ]
        )
        assert step.to_display_string() == "Repeat 3x"

    def test_to_display_string_open(self):
        """Test display string for open duration step"""
        step = WorkoutStep(
            step_type=StepType.COOLDOWN,
            duration_type=DurationType.OPEN,
            target_type=TargetType.OPEN
        )
        assert step.to_display_string() == "Cooldown: open"
