"""Base parser interface for workout parsers"""

from abc import ABC, abstractmethod
from garmin_workout_creator.models import Workout


class WorkoutParser(ABC):
    """Abstract base class for workout parsers"""

    @abstractmethod
    def parse(self, text: str) -> Workout:
        """
        Parse workout description text into a Workout object

        Args:
            text: Natural language workout description

        Returns:
            Workout object with parsed steps

        Raises:
            ValueError: If the text cannot be parsed
        """
        pass

    @abstractmethod
    def can_parse(self, text: str) -> bool:
        """
        Check if this parser can handle the given text

        Args:
            text: Natural language workout description

        Returns:
            True if parser can handle this text, False otherwise
        """
        pass
