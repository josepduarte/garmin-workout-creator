"""Tests for regex-based workout parser"""

import pytest
from garmin_workout_creator.parsers.regex_parser import RegexWorkoutParser
from garmin_workout_creator.models import StepType, DurationType, TargetType


class TestRegexWorkoutParser:
    """Tests for RegexWorkoutParser"""

    def setup_method(self):
        """Set up test fixtures"""
        self.parser = RegexWorkoutParser()

    def test_simple_warmup_with_pace(self):
        """Test parsing simple warmup with pace target"""
        workout = self.parser.parse("1km warmup @ 5:30")

        assert len(workout.steps) == 1
        step = workout.steps[0]
        assert step.step_type == StepType.WARMUP
        assert step.duration_type == DurationType.DISTANCE
        assert step.duration_value == 1
        assert step.duration_unit == "km"
        assert step.target_type == TargetType.PACE
        assert step.pace_target.min_seconds_per_km == 330

    def test_warmup_target_first(self):
        """Test parsing warmup with target-first format"""
        workout = self.parser.parse("warmup 1km @ 5:30")

        assert len(workout.steps) == 1
        step = workout.steps[0]
        assert step.step_type == StepType.WARMUP
        assert step.duration_value == 1

    def test_time_based_step(self):
        """Test parsing time-based step"""
        workout = self.parser.parse("10min warmup")

        assert len(workout.steps) == 1
        step = workout.steps[0]
        assert step.duration_type == DurationType.TIME
        assert step.duration_value == 10
        assert step.duration_unit == "min"

    def test_heart_rate_target(self):
        """Test parsing heart rate target"""
        workout = self.parser.parse("5min @ 165 bpm")

        assert len(workout.steps) == 1
        step = workout.steps[0]
        assert step.target_type == TargetType.HEART_RATE
        assert step.hr_target.min_bpm == 165

    def test_cooldown(self):
        """Test parsing cooldown"""
        workout = self.parser.parse("1km cooldown")

        assert len(workout.steps) == 1
        step = workout.steps[0]
        assert step.step_type == StepType.COOLDOWN

    def test_open_cooldown(self):
        """Test parsing open duration cooldown"""
        workout = self.parser.parse("cooldown")

        assert len(workout.steps) == 1
        step = workout.steps[0]
        assert step.step_type == StepType.COOLDOWN
        assert step.duration_type == DurationType.OPEN
        assert step.target_type == TargetType.OPEN

    def test_simple_interval(self):
        """Test parsing simple interval pattern"""
        workout = self.parser.parse("3x 1km @ 4:45")

        assert len(workout.steps) == 1
        repeat = workout.steps[0]
        assert repeat.step_type == StepType.REPEAT
        assert repeat.repeat_count == 3
        assert len(repeat.repeat_steps) == 1

        interval = repeat.repeat_steps[0]
        assert interval.step_type == StepType.INTERVAL
        assert interval.duration_value == 1
        assert interval.duration_unit == "km"
        assert interval.pace_target.min_seconds_per_km == 285

    def test_interval_with_recovery(self):
        """Test parsing interval with recovery"""
        workout = self.parser.parse("3x 1km @ 4:45 + 2min rest")

        assert len(workout.steps) == 1
        repeat = workout.steps[0]
        assert repeat.repeat_count == 3
        assert len(repeat.repeat_steps) == 2

        interval = repeat.repeat_steps[0]
        assert interval.step_type == StepType.INTERVAL
        assert interval.duration_value == 1

        recovery = repeat.repeat_steps[1]
        assert recovery.step_type == StepType.RECOVERY
        assert recovery.duration_value == 2
        assert recovery.duration_unit == "min"

    def test_multiple_steps(self):
        """Test parsing multiple steps separated by comma"""
        workout = self.parser.parse("1km warmup @ 5:30, 3x 1km @ 4:45 + 2min rest, 1km cooldown")

        assert len(workout.steps) == 3
        assert workout.steps[0].step_type == StepType.WARMUP
        assert workout.steps[1].step_type == StepType.REPEAT
        assert workout.steps[2].step_type == StepType.COOLDOWN

    def test_normalization_k_to_km(self):
        """Test that 'k' is normalized to 'km'"""
        workout = self.parser.parse("1k warmup")

        assert workout.steps[0].duration_unit == "km"

    def test_normalization_mins_to_min(self):
        """Test that 'mins' is normalized to 'min'"""
        workout = self.parser.parse("10mins warmup")

        assert workout.steps[0].duration_unit == "min"

    def test_case_insensitive(self):
        """Test that parsing is case insensitive"""
        workout = self.parser.parse("1KM WARMUP @ 5:30")

        assert len(workout.steps) == 1
        assert workout.steps[0].step_type == StepType.WARMUP

    def test_various_separators(self):
        """Test that various separators work"""
        workout = self.parser.parse("1km warmup; 5km run; 1km cooldown")

        assert len(workout.steps) == 3

    def test_decimal_distance(self):
        """Test parsing decimal distance values"""
        workout = self.parser.parse("1.5km warmup")

        assert workout.steps[0].duration_value == 1.5

    def test_recovery_step(self):
        """Test parsing recovery step"""
        workout = self.parser.parse("2min recovery")

        assert len(workout.steps) == 1
        assert workout.steps[0].step_type == StepType.RECOVERY

    def test_empty_input(self):
        """Test that empty input raises error"""
        with pytest.raises(ValueError, match="cannot be empty"):
            self.parser.parse("")

    def test_unparseable_input(self):
        """Test that unparseable input raises error"""
        with pytest.raises(ValueError):
            self.parser.parse("gobbledygook nonsense")

    def test_can_parse_valid_input(self):
        """Test can_parse returns True for valid input"""
        assert self.parser.can_parse("1km warmup @ 5:30")
        assert self.parser.can_parse("3x 1km + 2min rest")
        assert self.parser.can_parse("cooldown")

    def test_can_parse_invalid_input(self):
        """Test can_parse returns False for invalid input"""
        assert not self.parser.can_parse("")
        assert not self.parser.can_parse("gobbledygook")

    def test_pace_without_target(self):
        """Test parsing step without pace target"""
        workout = self.parser.parse("1km warmup")

        assert workout.steps[0].target_type == TargetType.OPEN
        assert workout.steps[0].pace_target is None

    def test_complex_workout(self):
        """Test parsing a complete complex workout"""
        workout = self.parser.parse(
            "1km warmup @ 5:30, "
            "5x 1km @ 4:30 + 2min rest, "
            "2km @ 165 bpm, "
            "cooldown"
        )

        assert len(workout.steps) == 4
        assert workout.steps[0].step_type == StepType.WARMUP
        assert workout.steps[1].step_type == StepType.REPEAT
        assert workout.steps[1].repeat_count == 5
        assert workout.steps[2].target_type == TargetType.HEART_RATE
        assert workout.steps[3].duration_type == DurationType.OPEN

    def test_warmup_abbreviation(self):
        """Test that 'wu' is recognized as warmup"""
        workout = self.parser.parse("1km wu")

        assert workout.steps[0].step_type == StepType.WARMUP

    def test_cooldown_abbreviation(self):
        """Test that 'cd' is recognized as cooldown"""
        workout = self.parser.parse("1km cd")

        assert workout.steps[0].step_type == StepType.COOLDOWN

    def test_interval_keywords(self):
        """Test various interval keywords"""
        for keyword in ["interval", "work", "hard", "fast", "tempo"]:
            workout = self.parser.parse(f"1km {keyword}")
            assert workout.steps[0].step_type == StepType.INTERVAL

    def test_recovery_keywords(self):
        """Test various recovery keywords"""
        for keyword in ["recovery", "rest", "easy", "jog"]:
            workout = self.parser.parse(f"2min {keyword}")
            assert workout.steps[0].step_type == StepType.RECOVERY

    def test_multiple_intervals(self):
        """Test parsing multiple interval sets"""
        workout = self.parser.parse("3x 1km @ 4:30 + 2min, 5x 400m @ 4:00 + 90sec rest")

        assert len(workout.steps) == 2
        assert workout.steps[0].repeat_count == 3
        assert workout.steps[1].repeat_count == 5

    def test_meters_unit(self):
        """Test parsing meters as unit"""
        workout = self.parser.parse("400m interval @ 4:00")

        assert workout.steps[0].duration_value == 400
        assert workout.steps[0].duration_unit == "m"

    def test_seconds_unit(self):
        """Test parsing seconds as unit"""
        workout = self.parser.parse("90sec rest")

        assert workout.steps[0].duration_value == 90
        assert workout.steps[0].duration_unit == "sec"
