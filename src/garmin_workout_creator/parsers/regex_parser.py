"""Regex-based workout parser"""

import re
from typing import List, Optional, Tuple
from .base import WorkoutParser
from garmin_workout_creator.models import (
    Workout,
    WorkoutStep,
    StepType,
    DurationType,
    TargetType,
    PaceTarget,
    HeartRateTarget,
)


class RegexWorkoutParser(WorkoutParser):
    """Parse workout descriptions using regex patterns"""

    # Step type keywords
    WARMUP_KEYWORDS = r'(?:warmup|warm\s*up|wu)'
    COOLDOWN_KEYWORDS = r'(?:cooldown|cool\s*down|cd)'
    INTERVAL_KEYWORDS = r'(?:interval|int|work|hard|fast|tempo|run)'
    RECOVERY_KEYWORDS = r'(?:recovery|recover|rest|easy|jog)'

    # Unit patterns
    DISTANCE_UNITS = r'(?:km|k|kilometers?|mi|miles?|m|meters?)'
    TIME_UNITS = r'(?:min|minutes?|sec|seconds?|s|hr|hours?|h)'

    # Pace pattern (M:SS or MM:SS)
    PACE_PATTERN = r'(\d{1,2}):(\d{2})'

    # Heart rate pattern (number + bpm)
    HR_PATTERN = r'(\d{2,3})\s*(?:bpm|beats?)'

    def __init__(self):
        """Initialize the regex parser"""
        self._compile_patterns()

    def _compile_patterns(self):
        """Compile regex patterns for reuse"""
        # Simple step: "1km warmup @ 5:30"
        self.simple_step_pattern = re.compile(
            rf'(\d+(?:\.\d+)?)\s*({self.DISTANCE_UNITS}|{self.TIME_UNITS})\s+'
            rf'({self.WARMUP_KEYWORDS}|{self.COOLDOWN_KEYWORDS}|{self.INTERVAL_KEYWORDS}|{self.RECOVERY_KEYWORDS})'
            rf'(?:\s+@\s+(.+?))?$',
            re.IGNORECASE
        )

        # Step with target first: "warmup 1km @ 5:30"
        self.target_first_pattern = re.compile(
            rf'({self.WARMUP_KEYWORDS}|{self.COOLDOWN_KEYWORDS}|{self.INTERVAL_KEYWORDS}|{self.RECOVERY_KEYWORDS})\s+'
            rf'(\d+(?:\.\d+)?)\s*({self.DISTANCE_UNITS}|{self.TIME_UNITS})'
            rf'(?:\s+@\s+(.+?))?$',
            re.IGNORECASE
        )

        # Duration only with target: "5min @ 165 bpm" or "2km @ 4:45"
        self.duration_only_pattern = re.compile(
            rf'^(\d+(?:\.\d+)?)\s*({self.DISTANCE_UNITS}|{self.TIME_UNITS})'
            rf'(?:\s+@\s+(.+?))?$',
            re.IGNORECASE
        )

        # Interval pattern: "3x 1km @ 4:45 + 2min rest"
        self.interval_pattern = re.compile(
            rf'(\d+)\s*x\s+'  # Repeat count
            rf'(\d+(?:\.\d+)?)\s*({self.DISTANCE_UNITS}|{self.TIME_UNITS})'  # Work duration
            rf'(?:\s+@\s+([^\+]+?))?'  # Optional target (non-greedy, stop at +)
            rf'(?:\s*\+\s*(\d+(?:\.\d+)?)\s*({self.TIME_UNITS}|{self.DISTANCE_UNITS})\s*(?:rest|recovery|rec|jog|easy)?)?$',  # Optional recovery
            re.IGNORECASE
        )

        # Just step type (open duration): "cooldown", "warmup"
        self.open_step_pattern = re.compile(
            rf'^({self.WARMUP_KEYWORDS}|{self.COOLDOWN_KEYWORDS}|{self.INTERVAL_KEYWORDS}|{self.RECOVERY_KEYWORDS})$',
            re.IGNORECASE
        )

    def can_parse(self, text: str) -> bool:
        """Check if text can be parsed by regex parser"""
        if not text or not text.strip():
            return False

        # Normalize and check if any pattern matches
        normalized = self._normalize_text(text)
        parts = self._split_workout(normalized)

        for part in parts:
            if not self._can_parse_part(part):
                return False

        return True

    def parse(self, text: str) -> Workout:
        """
        Parse workout description into Workout object

        Args:
            text: Workout description like "1km warmup @ 5:30, 3x 1km @ 4:45 + 2min rest"

        Returns:
            Workout object with parsed steps

        Raises:
            ValueError: If text cannot be parsed
        """
        if not text or not text.strip():
            raise ValueError("Workout description cannot be empty")

        # Normalize the input
        normalized = self._normalize_text(text)

        # Split into individual steps
        parts = self._split_workout(normalized)

        if not parts:
            raise ValueError("No workout steps found in description")

        # Parse each part
        steps: List[WorkoutStep] = []
        for i, part in enumerate(parts):
            try:
                step = self._parse_step(part, i)
                steps.append(step)
            except ValueError as e:
                raise ValueError(f"Error parsing step '{part}': {e}")

        # Create workout
        workout = Workout(
            name="Untitled Workout",
            sport_type="running",
            steps=steps
        )

        return workout

    def _normalize_text(self, text: str) -> str:
        """Normalize input text for consistent parsing"""
        # Convert to lowercase
        text = text.lower().strip()

        # Standardize separators: comma, semicolon, newline → comma
        text = re.sub(r'[;,\n]+', ',', text)

        # Standardize units - be careful with 'k' (single letter matching)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*k\b', r'\1km', text)  # "1k" → "1km"
        text = re.sub(r'\bkms\b', 'km', text)
        text = re.sub(r'\bkilometers?\b', 'km', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*mins?\b', r'\1min', text)  # "10mins" → "10min"
        text = re.sub(r'\bminutes?\b', 'min', text)
        text = re.sub(r'(\d+(?:\.\d+)?)\s*secs?\b', r'\1sec', text)  # "90secs" → "90sec"
        text = re.sub(r'\bseconds?\b', 'sec', text)
        text = re.sub(r'\bhours?\b', 'hr', text)

        # Standardize @ symbol (remove extra spaces)
        text = re.sub(r'\s+@\s+', ' @ ', text)

        # Standardize + for intervals
        text = re.sub(r'\s*\+\s*', ' + ', text)

        return text

    def _split_workout(self, text: str) -> List[str]:
        """Split workout description into individual step descriptions"""
        # Split by comma
        parts = [p.strip() for p in text.split(',') if p.strip()]
        return parts

    def _can_parse_part(self, part: str) -> bool:
        """Check if a single part can be parsed"""
        # Try all patterns
        if self.interval_pattern.match(part):
            return True
        if self.simple_step_pattern.match(part):
            return True
        if self.target_first_pattern.match(part):
            return True
        if self.duration_only_pattern.match(part):
            return True
        if self.open_step_pattern.match(part):
            return True
        return False

    def _parse_step(self, part: str, index: int) -> WorkoutStep:
        """Parse a single step description"""
        # Try interval pattern first (most specific)
        match = self.interval_pattern.match(part)
        if match:
            return self._parse_interval_step(match)

        # Try simple step pattern
        match = self.simple_step_pattern.match(part)
        if match:
            return self._parse_simple_step(match)

        # Try target-first pattern
        match = self.target_first_pattern.match(part)
        if match:
            return self._parse_target_first_step(match)

        # Try duration-only pattern
        match = self.duration_only_pattern.match(part)
        if match:
            return self._parse_duration_only_step(match)

        # Try open step pattern
        match = self.open_step_pattern.match(part)
        if match:
            return self._parse_open_step(match)

        raise ValueError(f"Cannot parse step: '{part}'")

    def _parse_interval_step(self, match: re.Match) -> WorkoutStep:
        """Parse interval pattern like '3x 1km @ 4:45 + 2min rest'"""
        repeat_count = int(match.group(1))
        work_value = float(match.group(2))
        work_unit = match.group(3)
        target_str = match.group(4)  # May be None
        recovery_value = match.group(5)  # May be None
        recovery_unit = match.group(6)  # May be None

        # Create work step (interval)
        duration_type, duration_value = self._parse_duration(work_value, work_unit)
        target_type, pace_target, hr_target = self._parse_target(target_str)

        work_step = WorkoutStep(
            step_type=StepType.INTERVAL,
            duration_type=duration_type,
            duration_value=duration_value,
            duration_unit=work_unit,
            target_type=target_type,
            pace_target=pace_target,
            hr_target=hr_target
        )

        # Create recovery step if specified
        repeat_steps = [work_step]
        if recovery_value:
            recovery_duration_type, recovery_duration_value = self._parse_duration(
                float(recovery_value), recovery_unit
            )
            recovery_step = WorkoutStep(
                step_type=StepType.RECOVERY,
                duration_type=recovery_duration_type,
                duration_value=recovery_duration_value,
                duration_unit=recovery_unit,
                target_type=TargetType.OPEN
            )
            repeat_steps.append(recovery_step)

        # Create repeat step
        repeat_step = WorkoutStep(
            step_type=StepType.REPEAT,
            duration_type=DurationType.OPEN,
            target_type=TargetType.OPEN,
            repeat_count=repeat_count,
            repeat_steps=repeat_steps
        )

        return repeat_step

    def _parse_simple_step(self, match: re.Match) -> WorkoutStep:
        """Parse simple pattern like '1km warmup @ 5:30'"""
        value = float(match.group(1))
        unit = match.group(2)
        step_type_str = match.group(3)
        target_str = match.group(4)  # May be None

        step_type = self._infer_step_type(step_type_str)
        duration_type, duration_value = self._parse_duration(value, unit)
        target_type, pace_target, hr_target = self._parse_target(target_str)

        return WorkoutStep(
            step_type=step_type,
            duration_type=duration_type,
            duration_value=duration_value,
            duration_unit=unit,
            target_type=target_type,
            pace_target=pace_target,
            hr_target=hr_target
        )

    def _parse_target_first_step(self, match: re.Match) -> WorkoutStep:
        """Parse target-first pattern like 'warmup 1km @ 5:30'"""
        step_type_str = match.group(1)
        value = float(match.group(2))
        unit = match.group(3)
        target_str = match.group(4)  # May be None

        step_type = self._infer_step_type(step_type_str)
        duration_type, duration_value = self._parse_duration(value, unit)
        target_type, pace_target, hr_target = self._parse_target(target_str)

        return WorkoutStep(
            step_type=step_type,
            duration_type=duration_type,
            duration_value=duration_value,
            duration_unit=unit,
            target_type=target_type,
            pace_target=pace_target,
            hr_target=hr_target
        )

    def _parse_open_step(self, match: re.Match) -> WorkoutStep:
        """Parse open step like 'cooldown'"""
        step_type_str = match.group(1)
        step_type = self._infer_step_type(step_type_str)

        return WorkoutStep(
            step_type=step_type,
            duration_type=DurationType.OPEN,
            target_type=TargetType.OPEN
        )

    def _parse_duration_only_step(self, match: re.Match) -> WorkoutStep:
        """Parse duration-only pattern like '5min @ 165 bpm' or '2km @ 4:45'"""
        value = float(match.group(1))
        unit = match.group(2)
        target_str = match.group(3)  # May be None

        # Infer step type as interval (generic workout step)
        step_type = StepType.INTERVAL
        duration_type, duration_value = self._parse_duration(value, unit)
        target_type, pace_target, hr_target = self._parse_target(target_str)

        return WorkoutStep(
            step_type=step_type,
            duration_type=duration_type,
            duration_value=duration_value,
            duration_unit=unit,
            target_type=target_type,
            pace_target=pace_target,
            hr_target=hr_target
        )

    def _infer_step_type(self, text: str) -> StepType:
        """Infer step type from text"""
        text = text.lower()

        if re.search(self.WARMUP_KEYWORDS, text, re.IGNORECASE):
            return StepType.WARMUP
        elif re.search(self.COOLDOWN_KEYWORDS, text, re.IGNORECASE):
            return StepType.COOLDOWN
        elif re.search(self.RECOVERY_KEYWORDS, text, re.IGNORECASE):
            return StepType.RECOVERY
        elif re.search(self.INTERVAL_KEYWORDS, text, re.IGNORECASE):
            return StepType.INTERVAL
        else:
            # Default to interval if unclear
            return StepType.INTERVAL

    def _parse_duration(self, value: float, unit: str) -> Tuple[DurationType, float]:
        """Parse duration value and unit into DurationType and normalized value"""
        unit = unit.lower()

        # Distance-based
        if unit in ['km', 'k', 'kilometers', 'kilometer']:
            return DurationType.DISTANCE, value
        elif unit in ['m', 'meters', 'meter']:
            return DurationType.DISTANCE, value
        elif unit in ['mi', 'mile', 'miles']:
            return DurationType.DISTANCE, value

        # Time-based
        elif unit in ['min', 'minute', 'minutes']:
            return DurationType.TIME, value
        elif unit in ['sec', 'second', 'seconds', 's']:
            return DurationType.TIME, value
        elif unit in ['hr', 'hour', 'hours', 'h']:
            return DurationType.TIME, value

        else:
            raise ValueError(f"Unknown duration unit: {unit}")

    def _parse_target(
        self, target_str: Optional[str]
    ) -> Tuple[TargetType, Optional[PaceTarget], Optional[HeartRateTarget]]:
        """
        Parse target string into target type and values

        Returns:
            Tuple of (TargetType, PaceTarget or None, HeartRateTarget or None)
        """
        if not target_str:
            return TargetType.OPEN, None, None

        target_str = target_str.strip()

        # Check for heart rate (number + bpm)
        hr_match = re.search(self.HR_PATTERN, target_str, re.IGNORECASE)
        if hr_match:
            bpm = int(hr_match.group(1))
            hr_target = HeartRateTarget(min_bpm=bpm)
            return TargetType.HEART_RATE, None, hr_target

        # Check for pace (M:SS format)
        pace_match = re.search(self.PACE_PATTERN, target_str)
        if pace_match:
            pace_target = PaceTarget.from_pace_string(f"{pace_match.group(1)}:{pace_match.group(2)}")
            return TargetType.PACE, pace_target, None

        # If nothing matches, treat as open
        return TargetType.OPEN, None, None
