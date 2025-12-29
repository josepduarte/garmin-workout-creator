"""CLI entry point for Garmin Workout Creator"""

import os
import click
from garmin_workout_creator.parsers import RegexWorkoutParser
from garmin_workout_creator.tui.app import WorkoutEditorApp
from garmin_workout_creator.garmin import GarminAuth, GarminClient


@click.command()
@click.version_option(version="0.1.0")
@click.option(
    '--workout',
    '-w',
    help='Workout description (e.g., "1km warmup @ 5:30, 3x 1km @ 4:45 + 2min rest")'
)
@click.option(
    '--no-sync',
    is_flag=True,
    help='Skip Garmin Connect sync (only create workout locally)'
)
@click.option(
    '--email',
    '-e',
    help='Garmin Connect email (only needed for first login)',
    envvar='GARMIN_EMAIL'
)
@click.option(
    '--password',
    '-p',
    help='Garmin Connect password (only needed for first login)',
    envvar='GARMIN_PASSWORD'
)
def main(workout: str = None, no_sync: bool = False, email: str = None, password: str = None) -> None:
    """
    Garmin Workout Creator - Create workouts with natural language

    A CLI tool for creating Garmin Connect workouts using natural language.
    Write workouts in plain text and sync them directly to your Garmin account.
    """
    click.echo("🏃 Garmin Workout Creator v0.1.0")
    click.echo()

    # Get workout description
    if not workout:
        click.echo("Enter your workout description:")
        click.echo("Example: 1km warmup @ 5:30, 3x 1km @ 4:45 + 2min rest, cooldown")
        click.echo()
        workout = click.prompt("Workout", default="")

    if not workout.strip():
        click.echo("❌ No workout description provided")
        return

    # Parse the workout
    parser = RegexWorkoutParser()
    try:
        parsed_workout = parser.parse(workout)
        click.echo(f"✅ Parsed {len(parsed_workout.steps)} steps")
        click.echo()

        # Launch TUI editor
        click.echo("Opening workout editor...")
        app = WorkoutEditorApp(parsed_workout)
        result = app.run()

        # Display results
        if result:
            click.echo()
            click.echo("✅ Workout configured!")
            click.echo(f"   Name: {result.name}")
            if result.scheduled_date:
                click.echo(f"   Date: {result.scheduled_date}")
            click.echo(f"   Steps: {result.get_step_count()}")
            click.echo()

            # Sync to Garmin Connect
            if not no_sync:
                if click.confirm("Upload workout to Garmin Connect?", default=True):
                    try:
                        click.echo("🔄 Connecting to Garmin Connect...")

                        # Initialize client
                        auth = GarminAuth()
                        client = GarminClient(auth)

                        # Handle authentication
                        try:
                            client.ensure_connected(email, password)
                        except Exception as auth_error:
                            if "No saved authentication tokens" in str(auth_error):
                                click.echo()
                                click.echo("⚠️  First time setup - Garmin Connect credentials required")
                                click.echo()
                                if not email:
                                    email = click.prompt("Garmin Connect email")
                                if not password:
                                    password = click.prompt("Garmin Connect password", hide_input=True)
                                client.ensure_connected(email, password)
                                click.echo("✅ Credentials saved for future use")
                            else:
                                raise

                        # Upload workout
                        click.echo("📤 Uploading workout...")
                        response = client.upload_workout(result)

                        click.echo()
                        click.echo("✅ Workout uploaded to Garmin Connect!")
                        if isinstance(response, dict) and 'workoutId' in response:
                            click.echo(f"   Workout ID: {response['workoutId']}")
                        click.echo()
                        click.echo("💡 Tip: Sync your Garmin device to download the workout")

                    except Exception as e:
                        click.echo()
                        click.echo(f"❌ Failed to upload workout: {e}")
                        click.echo()
                        click.echo("💡 Workout was created locally but not uploaded.")
                        click.echo("   You can try uploading manually or run again with --no-sync")
                else:
                    click.echo("⏭️  Skipped Garmin Connect sync")
            else:
                click.echo("⏭️  Garmin Connect sync disabled (--no-sync)")
        else:
            click.echo()
            click.echo("❌ Cancelled")

    except ValueError as e:
        click.echo(f"❌ Error parsing workout: {e}")
        click.echo()
        click.echo("Supported formats:")
        click.echo("  - Distance: 1km warmup @ 5:30")
        click.echo("  - Time: 10min @ 165 bpm")
        click.echo("  - Intervals: 3x 1km @ 4:45 + 2min rest")


if __name__ == "__main__":
    main()
