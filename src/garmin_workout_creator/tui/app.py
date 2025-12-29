"""Main Textual TUI application for workout editing"""

from textual.app import App, ComposeResult
from textual.containers import Container, Vertical, ScrollableContainer
from textual.widgets import Header, Footer, Static, Input, Button, Label
from textual.binding import Binding
from textual.screen import Screen
from textual import on
from datetime import date

from garmin_workout_creator.models import Workout
from .widgets.workout_list import WorkoutListWidget


class ReviewScreen(Screen):
    """Screen for reviewing workout steps"""

    CSS = """
    ReviewScreen {
        align: center middle;
    }

    #review-container {
        width: 80%;
        height: auto;
        max-height: 90%;
        border: solid $primary;
        padding: 1 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 1;
    }

    #instructions {
        text-align: center;
        color: $text-muted;
        margin-bottom: 1;
    }

    WorkoutListWidget {
        height: auto;
        max-height: 30;
        margin: 1 0;
    }

    .button-row {
        align: center middle;
        margin-top: 1;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("c", "continue", "Continue", show=True),
        Binding("q", "quit", "Quit", show=True),
    ]

    def __init__(self, workout: Workout):
        super().__init__()
        self.workout = workout

    def compose(self) -> ComposeResult:
        yield Header()

        with ScrollableContainer(id="review-container"):
            yield Label("🏃 Review Your Workout", id="title")
            yield Label("Use ↑↓ to navigate • Press 'c' to continue", id="instructions")
            yield WorkoutListWidget(self.workout)

            # Show workout summary
            total_distance = self.workout.get_total_distance_km()
            total_time = self.workout.get_total_time_minutes()

            summary_parts = [f"Total steps: {self.workout.get_step_count()}"]
            if total_distance:
                summary_parts.append(f"Distance: {total_distance:.1f}km")
            if total_time:
                summary_parts.append(f"Time: {total_time:.0f}min")

            yield Label(" | ".join(summary_parts), id="summary")

            with Container(classes="button-row"):
                yield Button("Continue", variant="primary", id="continue-btn")
                yield Button("Cancel", variant="default", id="cancel-btn")

        yield Footer()

    @on(Button.Pressed, "#continue-btn")
    def on_continue(self):
        self.action_continue()

    @on(Button.Pressed, "#cancel-btn")
    def on_cancel(self):
        self.app.exit(None)

    def action_continue(self):
        self.app.push_screen(MetadataScreen(self.workout))


class MetadataScreen(Screen):
    """Screen for entering workout metadata"""

    CSS = """
    MetadataScreen {
        align: center middle;
    }

    #metadata-container {
        width: 60%;
        height: auto;
        border: solid $primary;
        padding: 2;
    }

    #title {
        text-align: center;
        text-style: bold;
        color: $accent;
        margin-bottom: 2;
    }

    .form-row {
        height: auto;
        margin: 1 0;
    }

    .form-label {
        width: 20;
        content-align: right middle;
        margin-right: 2;
    }

    Input {
        width: 1fr;
    }

    .button-row {
        align: center middle;
        margin-top: 2;
    }

    Button {
        margin: 0 1;
    }
    """

    BINDINGS = [
        Binding("ctrl+s", "save", "Save", show=True),
        Binding("escape", "back", "Back", show=True),
    ]

    def __init__(self, workout: Workout):
        super().__init__()
        self.workout = workout

    def compose(self) -> ComposeResult:
        yield Header()

        with Container(id="metadata-container"):
            yield Label("📝 Workout Details", id="title")

            with Container(classes="form-row"):
                yield Label("Name:", classes="form-label")
                yield Input(
                    value=self.workout.name,
                    placeholder="Enter workout name",
                    id="workout-name"
                )

            with Container(classes="form-row"):
                yield Label("Date:", classes="form-label")
                yield Input(
                    value=str(self.workout.scheduled_date) if self.workout.scheduled_date else "",
                    placeholder="YYYY-MM-DD (optional)",
                    id="workout-date"
                )

            with Container(classes="button-row"):
                yield Button("Save & Finish", variant="success", id="save-btn")
                yield Button("Back", variant="default", id="back-btn")

        yield Footer()

    @on(Button.Pressed, "#save-btn")
    def on_save(self):
        self.action_save()

    @on(Button.Pressed, "#back-btn")
    def on_back(self):
        self.action_back()

    def action_save(self):
        # Update workout with form values
        name_input = self.query_one("#workout-name", Input)
        date_input = self.query_one("#workout-date", Input)

        if name_input.value.strip():
            self.workout.name = name_input.value.strip()

        if date_input.value.strip():
            try:
                self.workout.scheduled_date = date.fromisoformat(date_input.value.strip())
            except ValueError:
                pass

        self.app.exit(self.workout)

    def action_back(self):
        self.app.pop_screen()


class WorkoutEditorApp(App):
    """Interactive TUI for editing workout steps"""

    BINDINGS = [
        Binding("ctrl+q", "quit", "Quit"),
    ]

    def __init__(self, workout: Workout):
        """
        Initialize the workout editor app

        Args:
            workout: The workout to edit
        """
        super().__init__()
        self.workout = workout
        self.title = "Garmin Workout Creator"
        self.sub_title = "Review and edit your workout"

    def on_mount(self) -> None:
        """Push the review screen when app starts"""
        self.push_screen(ReviewScreen(self.workout))
