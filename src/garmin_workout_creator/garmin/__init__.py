"""Garmin Connect integration module"""

from .auth import GarminAuth
from .client import GarminClient
from .converter import WorkoutConverter

__all__ = ["GarminAuth", "GarminClient", "WorkoutConverter"]
