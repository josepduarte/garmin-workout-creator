"""Metadata form for workout name and date"""

from datetime import date
from textual.widgets import Static, Input, Label
from textual.containers import Horizontal, Vertical
from garmin_workout_creator.models import Workout


class MetadataForm(Vertical):
    """Form for editing workout metadata (name, date)"""

    def __init__(self, workout: Workout, **kwargs):
        super().__init__(**kwargs)
        self.workout = workout

    def compose(self):
        """Compose the form layout"""
        with Horizontal():
            yield Label("Workout Name:", classes="form-label")
            yield Input(
                value=self.workout.name,
                placeholder="Enter workout name",
                id="workout-name"
            )

        with Horizontal():
            yield Label("Scheduled Date:", classes="form-label")
            yield Input(
                value=str(self.workout.scheduled_date) if self.workout.scheduled_date else "",
                placeholder="YYYY-MM-DD (optional)",
                id="workout-date"
            )

    def update_workout(self, workout: Workout) -> None:
        """Update workout with form values"""
        name_input = self.query_one("#workout-name", Input)
        date_input = self.query_one("#workout-date", Input)

        # Update name
        if name_input.value.strip():
            workout.name = name_input.value.strip()

        # Update date if provided
        if date_input.value.strip():
            try:
                workout.scheduled_date = date.fromisoformat(date_input.value.strip())
            except ValueError:
                # Invalid date format, skip
                pass
