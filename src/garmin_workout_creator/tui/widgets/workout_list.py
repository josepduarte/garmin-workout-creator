"""Workout list widget for displaying and navigating workout steps"""

from textual.widgets import Static
from textual.reactive import reactive
from textual.message import Message
from rich.text import Text
from rich.table import Table

from garmin_workout_creator.models import Workout, StepType


class WorkoutListWidget(Static):
    """Widget to display workout steps with navigation"""

    selected_index: reactive[int] = reactive(0)

    def __init__(self, workout: Workout, **kwargs):
        """
        Initialize the workout list widget

        Args:
            workout: The workout to display
        """
        super().__init__(**kwargs)
        self.workout = workout
        self.can_focus = True

    def on_mount(self) -> None:
        """Called when widget is mounted"""
        self.update_display()

    def watch_selected_index(self, old_value: int, new_value: int) -> None:
        """React to selected index changes"""
        self.update_display()

    def update_display(self) -> None:
        """Update the display of workout steps"""
        # Create a table for the steps
        table = Table(
            show_header=True,
            header_style="bold magenta",
            border_style="blue",
            expand=True,
        )

        table.add_column("#", style="dim", width=4)
        table.add_column("Step", style="cyan", ratio=3)
        table.add_column("Duration", style="green", ratio=2)
        table.add_column("Target", style="yellow", ratio=2)

        # Flatten steps (handle repeats)
        display_steps = self._flatten_steps()

        for i, (step, indent_level) in enumerate(display_steps):
            # Highlight selected row
            row_style = "bold reverse" if i == self.selected_index else ""

            # Format step number with indent
            step_num = "  " * indent_level + f"{i + 1}."

            # Get step type and details
            step_type = step.step_type.value.capitalize()
            if step.step_type == StepType.REPEAT:
                step_type = f"Repeat {step.repeat_count}x"

            # Format duration
            if step.duration_type.value == "open":
                duration = "Open"
            elif step.duration_value:
                duration = f"{step.duration_value}{step.duration_unit}"
            else:
                duration = "-"

            # Format target
            if step.target_type.value == "open":
                target = "No target"
            elif step.pace_target:
                target = step.pace_target.to_display_string()
            elif step.hr_target:
                target = step.hr_target.to_display_string()
            elif step.cadence_target:
                target = step.cadence_target.to_display_string()
            else:
                target = "-"

            table.add_row(
                step_num,
                step_type,
                duration,
                target,
                style=row_style
            )

        # Update the widget content
        self.update(table)

    def _flatten_steps(self) -> list[tuple]:
        """
        Flatten the workout steps including nested repeat steps

        Returns:
            List of (step, indent_level) tuples
        """
        result = []

        for step in self.workout.steps:
            if step.step_type == StepType.REPEAT and step.repeat_steps:
                # Add the repeat step itself
                result.append((step, 0))
                # Add nested steps with indent
                for repeat_step in step.repeat_steps:
                    result.append((repeat_step, 1))
            else:
                result.append((step, 0))

        return result

    def action_cursor_down(self) -> None:
        """Move cursor down"""
        max_index = len(self._flatten_steps()) - 1
        if self.selected_index < max_index:
            self.selected_index += 1

    def action_cursor_up(self) -> None:
        """Move cursor up"""
        if self.selected_index > 0:
            self.selected_index -= 1

    def action_select(self) -> None:
        """Select/edit the current step"""
        # TODO: Implement step editing
        self.post_message(self.StepSelected(self.selected_index))

    def key_down(self) -> None:
        """Handle down arrow key"""
        self.action_cursor_down()

    def key_up(self) -> None:
        """Handle up arrow key"""
        self.action_cursor_up()

    def key_enter(self) -> None:
        """Handle enter key"""
        self.action_select()

    class StepSelected(Message):
        """Message sent when a step is selected"""

        def __init__(self, index: int) -> None:
            super().__init__()
            self.index = index
