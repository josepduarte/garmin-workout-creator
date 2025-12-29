"""
Helper script for reverse engineering Garmin Connect workout JSON format

This script helps you discover the actual stepTypeId, targetTypeId, and other
field values used by Garmin Connect by:

1. Uploading a test workout to Garmin Connect
2. Downloading it back to see the actual JSON format
3. Comparing the output to update the converter constants

Usage:
    python examples/reverse_engineer_format.py

Requirements:
    - Valid Garmin Connect credentials
    - At least one workout manually created in Garmin Connect for reference
"""

import json
import os
from garmin_workout_creator.garmin import GarminAuth, GarminClient
from garmin_workout_creator.parsers import RegexWorkoutParser


def main():
    print("=" * 70)
    print("🔬 Garmin Connect JSON Format Reverse Engineering Tool")
    print("=" * 70)
    print()

    # Step 1: Authenticate
    print("Step 1: Authentication")
    print("-" * 70)

    email = input("Garmin Connect email: ")
    password = input("Garmin Connect password: ")

    auth = GarminAuth()
    client = GarminClient(auth)

    try:
        client.ensure_connected(email, password)
        print("✅ Authenticated successfully")
        print()
    except Exception as e:
        print(f"❌ Authentication failed: {e}")
        return

    # Step 2: Create a test workout
    print("Step 2: Create Test Workout")
    print("-" * 70)
    print("Creating a simple test workout with common step types...")
    print()

    parser = RegexWorkoutParser()
    test_workout = parser.parse(
        "1km warmup @ 5:30, "
        "3x 1km @ 4:30 + 2min rest, "
        "2km @ 165 bpm, "
        "cooldown"
    )
    test_workout.name = "TEST - Format Discovery"

    print(f"Test workout: {test_workout.to_summary_string()}")
    print()

    # Step 3: Upload the workout
    print("Step 3: Upload Workout")
    print("-" * 70)

    try:
        upload_response = client.upload_workout(test_workout)
        print("✅ Workout uploaded!")
        print()
        print("Upload response:")
        print(json.dumps(upload_response, indent=2))
        print()

        workout_id = upload_response.get('workoutId')
        if not workout_id:
            print("⚠️  Could not extract workout ID from response")
            workout_id = input("Please enter the workout ID manually (from Garmin Connect): ")

    except Exception as e:
        print(f"❌ Upload failed: {e}")
        print()
        print("This is expected - the JSON format constants may need adjustment.")
        print()
        print("📋 Next steps:")
        print("1. Create a simple workout manually in Garmin Connect web UI:")
        print("   - 1km warmup @ 5:30/km pace")
        print("   - 1km interval @ 4:30/km pace")
        print("   - 2min recovery (no target)")
        print("   - Cooldown (open)")
        print()
        print("2. Use browser dev tools (F12) to:")
        print("   - Go to Network tab")
        print("   - Find the workout API call")
        print("   - Copy the JSON request/response")
        print()
        print("3. Compare with our generated JSON:")
        from garmin_workout_creator.garmin import WorkoutConverter
        converter = WorkoutConverter()
        our_json = converter.convert(test_workout)
        print()
        print("Our generated JSON:")
        print(json.dumps(our_json, indent=2))
        print()
        print("4. Update the constants in:")
        print("   src/garmin_workout_creator/garmin/converter.py")
        return

    # Step 4: Download the workout
    print("Step 4: Download Workout Back")
    print("-" * 70)

    try:
        workout_data = client.download_workout(workout_id)
        print("✅ Workout downloaded!")
        print()

        # Save to file for analysis
        output_file = "garmin_workout_actual.json"
        with open(output_file, 'w') as f:
            json.dumps(workout_data, f, indent=2)

        print(f"💾 Actual Garmin JSON saved to: {output_file}")
        print()
        print("Actual Garmin Connect JSON:")
        print(json.dumps(workout_data, indent=2))
        print()

    except Exception as e:
        print(f"⚠️  Download failed: {e}")
        print()
        print("The workout was uploaded but couldn't be downloaded.")
        print("You can manually export it from Garmin Connect:")
        print("1. Go to Garmin Connect > Training > Workouts")
        print(f"2. Find workout: {test_workout.name}")
        print("3. Use browser extensions to export JSON")

    # Step 5: Compare
    print()
    print("Step 5: Compare and Update")
    print("-" * 70)
    print()
    print("Compare the actual Garmin JSON with our generated JSON:")
    print()

    from garmin_workout_creator.garmin import WorkoutConverter
    converter = WorkoutConverter()
    our_json = converter.convert(test_workout)

    output_file_ours = "garmin_workout_ours.json"
    with open(output_file_ours, 'w') as f:
        json.dump(our_json, f, indent=2)

    print(f"💾 Our generated JSON saved to: {output_file_ours}")
    print()
    print("Our generated JSON:")
    print(json.dumps(our_json, indent=2))
    print()
    print("=" * 70)
    print()
    print("📋 Next Steps:")
    print("1. Compare both JSON files")
    print("2. Look for differences in:")
    print("   - stepTypeId values")
    print("   - targetTypeId / workoutTargetTypeId values")
    print("   - conditionTypeId values (duration)")
    print("   - Field structure and naming")
    print("3. Update src/garmin_workout_creator/garmin/converter.py with correct values")
    print("4. Re-run this script to verify")
    print()


if __name__ == "__main__":
    main()
