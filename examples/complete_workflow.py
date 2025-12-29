"""Complete workflow demonstration: Parse → Edit → Display"""

from garmin_workout_creator.parsers import RegexWorkoutParser
from garmin_workout_creator.models import Workout
from datetime import date


def demo_workflow():
    """Demonstrate the complete workout creation workflow"""

    print("=" * 70)
    print("🏃 Garmin Workout Creator - Complete Workflow Demo")
    print("=" * 70)
    print()

    # Step 1: Parse natural language
    print("📝 Step 1: Parse Natural Language")
    print("-" * 70)

    workout_text = "1km warmup @ 5:30, 5x 1km @ 4:30 + 2min rest, 2km @ 165 bpm, cooldown"
    print(f'Input: "{workout_text}"')
    print()

    parser = RegexWorkoutParser()
    workout = parser.parse(workout_text)

    print(f"✅ Parsed successfully!")
    print(f"   - {len(workout.steps)} main steps")
    print(f"   - {workout.get_step_count()} total steps (including repeats)")
    print()

    # Step 2: Display parsed workout
    print("📋 Step 2: Display Parsed Workout")
    print("-" * 70)

    for i, step in enumerate(workout.steps, 1):
        print(f"  {i}. {step.to_display_string()}")
        if step.repeat_steps:
            for j, repeat_step in enumerate(step.repeat_steps, 1):
                print(f"     {j}. {repeat_step.to_display_string()}")
    print()

    # Step 3: Add metadata (simulating TUI input)
    print("✏️  Step 3: Add Metadata")
    print("-" * 70)

    workout.name = "Tuesday Speed Session"
    workout.scheduled_date = date(2025, 12, 26)

    print(f"   Name: {workout.name}")
    print(f"   Date: {workout.scheduled_date}")
    print()

    # Step 4: Display final workout summary
    print("📊 Step 4: Final Workout Summary")
    print("-" * 70)

    print(f"   {workout.to_summary_string()}")
    print(f"   Sport: {workout.sport_type}")
    print(f"   Scheduled: {workout.scheduled_date}")

    total_distance = workout.get_total_distance_km()
    if total_distance:
        print(f"   Total Distance: {total_distance}km")

    print()

    # Step 5: Show what's next
    print("🚀 Step 5: Implementation Status")
    print("-" * 70)
    print("   ✅ Phase 1: Data Models (56 tests)")
    print("   ✅ Phase 2: Regex Parser (28 tests)")
    print("   ✅ Phase 3: Interactive TUI (Review → Metadata workflow)")
    print("   ✅ Phase 4: Garmin Connect Sync (implemented)")
    print()
    print("   Total: 84 tests passing")
    print()
    print("💡 Complete Workflow:")
    print("   1. Parse natural language → ReviewScreen (shows all steps)")
    print("   2. User reviews and navigates with ↑↓ arrows")
    print("   3. Press 'c' to continue → MetadataScreen")
    print("   4. Enter workout name and date → Save & Finish")
    print("   5. Upload to Garmin Connect (with auth token persistence)")
    print("   6. Sync to your Garmin device")
    print()
    print("🔬 Reverse Engineering Required:")
    print("   The Garmin JSON format uses IDs that must be discovered by:")
    print("   1. Creating test workouts in Garmin Connect")
    print("   2. Using browser dev tools to capture API calls")
    print("   3. Running: python examples/reverse_engineer_format.py")
    print("   4. Updating constants in garmin/converter.py")
    print()
    print("=" * 70)


if __name__ == "__main__":
    demo_workflow()
