"""Example: Parsing a natural language workout description"""

from garmin_workout_creator.parsers import RegexWorkoutParser


def parse_and_display(description: str):
    """Parse a workout description and display the results"""
    print(f"\nInput: \"{description}\"")
    print("=" * 70)

    parser = RegexWorkoutParser()

    try:
        workout = parser.parse(description)

        # Display summary
        print(f"\nWorkout: {workout.name}")
        print(f"Sport: {workout.sport_type}")
        print(f"Steps: {len(workout.steps)}")

        # Display each step
        print("\nParsed Steps:")
        for i, step in enumerate(workout.steps, 1):
            print(f"  {i}. {step.to_display_string()}")

            # Show nested repeat steps
            if step.repeat_steps:
                for j, repeat_step in enumerate(step.repeat_steps, 1):
                    print(f"     {j}. {repeat_step.to_display_string()}")

        # Display totals
        total_distance = workout.get_total_distance_km()
        if total_distance:
            print(f"\nTotal Distance: {total_distance}km")

        total_time = workout.get_total_time_minutes()
        if total_time:
            print(f"Total Time: {total_time:.0f} minutes")

    except ValueError as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    # Example 1: Simple warmup with pace
    parse_and_display("1km warmup @ 5:30")

    # Example 2: Interval workout with recovery
    parse_and_display("3x 1km @ 4:45 + 2min rest")

    # Example 3: Heart rate based run
    parse_and_display("5min @ 165 bpm")

    # Example 4: Complete interval workout
    parse_and_display(
        "1km warmup @ 5:30, "
        "5x 1km @ 4:30 + 2min rest, "
        "2km @ 165 bpm, "
        "cooldown"
    )

    # Example 5: Time-based workout
    parse_and_display("10min warmup, 20min @ 165 bpm, 5min cooldown")

    # Example 6: Using abbreviations
    parse_and_display("1k wu @ 5:30, 3x 1k @ 4:45 + 90sec rest, 1k cd")
