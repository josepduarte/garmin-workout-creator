"""Convert workout model to Garmin Connect JSON format"""

from typing import Any, Dict, List, Optional
from garmin_workout_creator.models import Workout, WorkoutStep, StepType, DurationType, TargetType


class WorkoutConverter:
    """
    Convert Workout objects to Garmin Connect JSON format

    NOTE: The exact values for stepTypeId, targetTypeId, durationTypeId, etc.
    must be reverse-engineered from actual Garmin Connect workouts.

    To find these values:
    1. Create a test workout in Garmin Connect with your desired step types
    2. Export the workout to JSON (using browser extension or API)
    3. Update the constants below with the actual values

    References:
    - https://github.com/cyberjunky/python-garminconnect
    - https://github.com/sydspost/Garmin-Connect-Workout-and-Schedule-creator
    """

    # Sport type IDs (reverse engineered - these are estimates)
    SPORT_TYPE_RUNNING = 1
    SPORT_TYPE_CYCLING = 2
    SPORT_TYPE_SWIMMING = 3

    # Step type IDs (TODO: Verify these values with actual Garmin exports)
    # Based on common patterns in reverse-engineered code
    STEP_TYPE_WARMUP = 1
    STEP_TYPE_COOLDOWN = 2
    STEP_TYPE_INTERVAL = 3
    STEP_TYPE_RECOVERY = 4
    STEP_TYPE_REST = 5
    STEP_TYPE_REPEAT = 6

    # Duration type IDs (TODO: Verify these values)
    DURATION_TYPE_DISTANCE = 1  # meters
    DURATION_TYPE_TIME = 2      # seconds
    DURATION_TYPE_OPEN = 3      # user press lap button

    # Target type IDs (TODO: Verify these values)
    TARGET_TYPE_OPEN = 0
    TARGET_TYPE_PACE = 1
    TARGET_TYPE_HEART_RATE = 2
    TARGET_TYPE_CADENCE = 3
    TARGET_TYPE_POWER = 4

    # Zone calculation types
    ZONE_CALC_TYPE_CUSTOM = 1
    ZONE_CALC_TYPE_PERCENT_HRR = 2
    ZONE_CALC_TYPE_PERCENT_MAX_HR = 3

    def __init__(self):
        """Initialize the workout converter"""
        self.step_type_map = {
            StepType.WARMUP: self.STEP_TYPE_WARMUP,
            StepType.COOLDOWN: self.STEP_TYPE_COOLDOWN,
            StepType.INTERVAL: self.STEP_TYPE_INTERVAL,
            StepType.RECOVERY: self.STEP_TYPE_RECOVERY,
            StepType.REST: self.STEP_TYPE_REST,
            StepType.REPEAT: self.STEP_TYPE_REPEAT,
        }

    def convert(self, workout: Workout) -> Dict[str, Any]:
        """
        Convert a Workout object to Garmin Connect JSON format

        Args:
            workout: The workout to convert

        Returns:
            Dictionary in Garmin Connect JSON format
        """
        garmin_workout = {
            "workoutName": workout.name,
            "description": workout.notes or "",
            "sportType": {"sportTypeId": self._get_sport_type_id(workout.sport_type)},
            "workoutSegments": [
                {
                    "segmentOrder": 1,
                    "sportType": {"sportTypeId": self._get_sport_type_id(workout.sport_type)},
                    "workoutSteps": self._convert_steps(workout.steps),
                }
            ],
        }

        # Add scheduled date if present
        if workout.scheduled_date:
            garmin_workout["scheduledDate"] = workout.scheduled_date.isoformat()

        return garmin_workout

    def _get_sport_type_id(self, sport_type: str) -> int:
        """Map sport type string to Garmin sport type ID"""
        sport_map = {
            "running": self.SPORT_TYPE_RUNNING,
            "cycling": self.SPORT_TYPE_CYCLING,
            "swimming": self.SPORT_TYPE_SWIMMING,
        }
        return sport_map.get(sport_type.lower(), self.SPORT_TYPE_RUNNING)

    def _convert_steps(self, steps: List[WorkoutStep]) -> List[Dict[str, Any]]:
        """Convert list of WorkoutStep objects to Garmin step format"""
        garmin_steps = []
        step_order = 1

        for step in steps:
            if step.step_type == StepType.REPEAT:
                # Handle repeat steps
                repeat_step = self._convert_repeat_step(step, step_order)
                garmin_steps.append(repeat_step)
                step_order += 1
            else:
                # Handle regular steps
                garmin_step = self._convert_single_step(step, step_order)
                garmin_steps.append(garmin_step)
                step_order += 1

        return garmin_steps

    def _convert_single_step(self, step: WorkoutStep, step_order: int) -> Dict[str, Any]:
        """Convert a single WorkoutStep to Garmin format"""
        garmin_step = {
            "type": "ExecutableStepDTO",
            "stepId": None,
            "stepOrder": step_order,
            "childStepId": None,
            "description": None,
            "stepType": {"stepTypeId": self.step_type_map.get(step.step_type, self.STEP_TYPE_INTERVAL)},
        }

        # Add duration
        duration = self._convert_duration(step)
        garmin_step.update(duration)

        # Add target
        target = self._convert_target(step)
        garmin_step.update(target)

        return garmin_step

    def _convert_repeat_step(self, step: WorkoutStep, step_order: int) -> Dict[str, Any]:
        """Convert a repeat step with nested steps"""
        # Create the repeat parent
        repeat_step = {
            "type": "RepeatGroupDTO",
            "stepId": None,
            "stepOrder": step_order,
            "numberOfIterations": step.repeat_count or 1,
            "smartRepeat": False,
            "childStepId": 1,  # Points to first child
            "workoutSteps": [],
        }

        # Convert child steps
        child_order = 1
        for child_step in (step.repeat_steps or []):
            child_garmin = self._convert_single_step(child_step, child_order)
            repeat_step["workoutSteps"].append(child_garmin)
            child_order += 1

        return repeat_step

    def _convert_duration(self, step: WorkoutStep) -> Dict[str, Any]:
        """Convert step duration to Garmin format"""
        if step.duration_type == DurationType.OPEN:
            return {
                "endCondition": {"conditionTypeId": self.DURATION_TYPE_OPEN},
                "endConditionValue": None,
            }
        elif step.duration_type == DurationType.DISTANCE:
            # Convert to meters
            distance_meters = step.get_duration_in_meters()
            return {
                "endCondition": {"conditionTypeId": self.DURATION_TYPE_DISTANCE},
                "endConditionValue": distance_meters,
                "preferredEndConditionUnit": {"unitId": 3},  # meters
            }
        elif step.duration_type == DurationType.TIME:
            # Convert to seconds
            time_seconds = step.get_duration_in_seconds()
            return {
                "endCondition": {"conditionTypeId": self.DURATION_TYPE_TIME},
                "endConditionValue": time_seconds,
                "preferredEndConditionUnit": {"unitId": 27},  # seconds
            }
        else:
            # Default to open
            return {
                "endCondition": {"conditionTypeId": self.DURATION_TYPE_OPEN},
                "endConditionValue": None,
            }

    def _convert_target(self, step: WorkoutStep) -> Dict[str, Any]:
        """Convert step target to Garmin format"""
        if step.target_type == TargetType.OPEN:
            return {
                "targetType": {"workoutTargetTypeId": self.TARGET_TYPE_OPEN},
                "targetValueOne": None,
                "targetValueTwo": None,
            }
        elif step.target_type == TargetType.PACE and step.pace_target:
            # Pace in meters per second
            # Convert from min/km to m/s: 1 km/min = 16.67 m/s
            # pace in sec/km -> speed in m/s = 1000 / pace_seconds
            min_pace_ms = 1000.0 / step.pace_target.max_seconds_per_km if step.pace_target.max_seconds_per_km else None
            max_pace_ms = 1000.0 / step.pace_target.min_seconds_per_km  # Note: inverted for pace->speed

            return {
                "targetType": {"workoutTargetTypeId": self.TARGET_TYPE_PACE},
                "targetValueOne": max_pace_ms,  # min speed
                "targetValueTwo": min_pace_ms,  # max speed (can be None for single target)
                "zoneNumber": None,
            }
        elif step.target_type == TargetType.HEART_RATE and step.hr_target:
            return {
                "targetType": {"workoutTargetTypeId": self.TARGET_TYPE_HEART_RATE},
                "targetValueOne": step.hr_target.min_bpm,
                "targetValueTwo": step.hr_target.max_bpm,
                "zoneNumber": None,
            }
        elif step.target_type == TargetType.CADENCE and step.cadence_target:
            return {
                "targetType": {"workoutTargetTypeId": self.TARGET_TYPE_CADENCE},
                "targetValueOne": step.cadence_target.min_spm,
                "targetValueTwo": step.cadence_target.max_spm,
                "zoneNumber": None,
            }
        else:
            # Default to open target
            return {
                "targetType": {"workoutTargetTypeId": self.TARGET_TYPE_OPEN},
                "targetValueOne": None,
                "targetValueTwo": None,
            }
