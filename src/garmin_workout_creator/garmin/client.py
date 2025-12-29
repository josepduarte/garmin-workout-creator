"""Garmin Connect API client for workout operations"""

from typing import Any, Dict, Optional
from garminconnect import Garmin
from .auth import GarminAuth
from .converter import WorkoutConverter
from garmin_workout_creator.models import Workout


class GarminClient:
    """Client for uploading workouts to Garmin Connect"""

    def __init__(self, auth: Optional[GarminAuth] = None):
        """
        Initialize Garmin client

        Args:
            auth: GarminAuth instance (creates new one if not provided)
        """
        self.auth = auth or GarminAuth()
        self.converter = WorkoutConverter()
        self._garmin = None

    def ensure_connected(self, email: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Ensure connection to Garmin Connect

        Args:
            email: Garmin Connect email (optional if tokens exist)
            password: Garmin Connect password (optional if tokens exist)
        """
        # Ensure authentication
        self.auth.ensure_authenticated(email, password)

        # Create Garmin client instance
        if self._garmin is None:
            self._garmin = Garmin()

    def upload_workout(self, workout: Workout) -> Dict[str, Any]:
        """
        Upload a workout to Garmin Connect

        Args:
            workout: The Workout object to upload

        Returns:
            Response from Garmin Connect API containing workout ID and details

        Raises:
            Exception: If upload fails
        """
        # Ensure we're connected
        if self._garmin is None:
            raise Exception("Not connected to Garmin Connect. Call ensure_connected() first.")

        # Convert workout to Garmin JSON format
        workout_json = self.converter.convert(workout)

        try:
            # Upload the workout
            response = self._garmin.upload_workout(workout_json)
            return response
        except Exception as e:
            raise Exception(f"Failed to upload workout to Garmin Connect: {e}")

    def download_workout(self, workout_id: int) -> Dict[str, Any]:
        """
        Download a workout from Garmin Connect (for reverse engineering)

        Args:
            workout_id: The ID of the workout to download

        Returns:
            Workout JSON from Garmin Connect

        Raises:
            Exception: If download fails
        """
        if self._garmin is None:
            raise Exception("Not connected to Garmin Connect. Call ensure_connected() first.")

        try:
            # Note: This is a placeholder - actual method name may differ
            # Use this to reverse engineer the JSON format
            response = self._garmin.get_workout(workout_id)
            return response
        except Exception as e:
            raise Exception(f"Failed to download workout from Garmin Connect: {e}")

    def list_workouts(self, start: int = 0, limit: int = 10) -> Dict[str, Any]:
        """
        List workouts from Garmin Connect

        Args:
            start: Starting index
            limit: Number of workouts to retrieve

        Returns:
            List of workouts

        Raises:
            Exception: If list operation fails
        """
        if self._garmin is None:
            raise Exception("Not connected to Garmin Connect. Call ensure_connected() first.")

        try:
            response = self._garmin.get_workouts(start, limit)
            return response
        except Exception as e:
            raise Exception(f"Failed to list workouts from Garmin Connect: {e}")
