"""Demo of the TUI workout editor"""

from garmin_workout_creator.parsers import RegexWorkoutParser
from garmin_workout_creator.tui.app import WorkoutEditorApp


def main():
    """Run the TUI demo"""
    # Parse a sample workout
    parser = RegexWorkoutParser()
    workout = parser.parse(
        "1km warmup @ 5:30, "
        "5x 1km @ 4:30 + 2min rest, "
        "2km @ 165 bpm, "
        "cooldown"
    )

    # Launch the TUI editor
    app = WorkoutEditorApp(workout)
    result = app.run()

    # Display the result
    if result:
        print("\n✅ Workout saved!")
        print(f"Name: {result.name}")
        print(f"Date: {result.scheduled_date}")
        print(f"Steps: {len(result.steps)}")
    else:
        print("\n❌ Cancelled")


if __name__ == "__main__":
    main()
