"""Example: Creating a simple workout programmatically"""

from datetime import date
from garmin_workout_creator.models import (
    Workout,
    WorkoutStep,
    StepType,
    DurationType,
    TargetType,
    PaceTarget,
    HeartRateTarget,
)


def create_interval_workout():
    """Create a sample interval workout"""

    # Create warmup step
    warmup = WorkoutStep(
        step_type=StepType.WARMUP,
        duration_type=DurationType.DISTANCE,
        duration_value=1,
        duration_unit="km",
        target_type=TargetType.PACE,
        pace_target=PaceTarget.from_pace_string("5:30")
    )

    # Create interval step
    interval = WorkoutStep(
        step_type=StepType.INTERVAL,
        duration_type=DurationType.DISTANCE,
        duration_value=1,
        duration_unit="km",
        target_type=TargetType.PACE,
        pace_target=PaceTarget.from_pace_string("4:30")
    )

    # Create recovery step
    recovery = WorkoutStep(
        step_type=StepType.RECOVERY,
        duration_type=DurationType.TIME,
        duration_value=2,
        duration_unit="min",
        target_type=TargetType.OPEN
    )

    # Create repeat step (5x intervals with recovery)
    repeat = WorkoutStep(
        step_type=StepType.REPEAT,
        duration_type=DurationType.OPEN,
        target_type=TargetType.OPEN,
        repeat_count=5,
        repeat_steps=[interval, recovery]
    )

    # Create cooldown step
    cooldown = WorkoutStep(
        step_type=StepType.COOLDOWN,
        duration_type=DurationType.DISTANCE,
        duration_value=1,
        duration_unit="km",
        target_type=TargetType.OPEN
    )

    # Create the complete workout
    workout = Workout(
        name="Tuesday Speed Session",
        sport_type="running",
        steps=[warmup, repeat, cooldown],
        scheduled_date=date(2025, 12, 26),
        notes="Focus on maintaining consistent pace during intervals"
    )

    return workout


if __name__ == "__main__":
    # Create the workout
    workout = create_interval_workout()

    # Display workout summary
    print(f"\n{workout.to_summary_string()}")
    print(f"Scheduled: {workout.scheduled_date}")
    print(f"\nWorkout Steps:")

    for i, step in enumerate(workout.steps, 1):
        print(f"  {i}. {step.to_display_string()}")

        # Show repeat steps if applicable
        if step.step_type == StepType.REPEAT and step.repeat_steps:
            for j, repeat_step in enumerate(step.repeat_steps, 1):
                print(f"     {j}. {repeat_step.to_display_string()}")

    # Display totals
    total_distance = workout.get_total_distance_km()
    if total_distance:
        print(f"\nTotal Distance: {total_distance}km")

    print(f"Notes: {workout.notes}")
