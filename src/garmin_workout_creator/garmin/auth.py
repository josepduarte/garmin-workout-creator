"""Garmin Connect authentication using garth library"""

import os
from pathlib import Path
from typing import Optional
import garth


class GarminAuth:
    """Handle Garmin Connect authentication with token persistence"""

    DEFAULT_TOKEN_DIR = Path.home() / ".garmin-workout-creator"

    def __init__(self, token_dir: Optional[Path] = None):
        """
        Initialize Garmin authentication

        Args:
            token_dir: Directory to store authentication tokens (default: ~/.garmin-workout-creator)
        """
        self.token_dir = token_dir or self.DEFAULT_TOKEN_DIR
        self.token_dir.mkdir(parents=True, exist_ok=True)
        self.token_file = self.token_dir / "garth_tokens"
        self._authenticated = False

    def login(self, email: str, password: str) -> None:
        """
        Login to Garmin Connect with email and password

        Args:
            email: Garmin Connect email
            password: Garmin Connect password

        Raises:
            Exception: If login fails
        """
        try:
            garth.login(email, password)
            garth.save(str(self.token_file))
            self._authenticated = True
        except Exception as e:
            raise Exception(f"Failed to login to Garmin Connect: {e}")

    def resume(self) -> bool:
        """
        Resume authentication from saved tokens

        Returns:
            True if tokens were loaded successfully, False otherwise
        """
        if not self.token_file.exists():
            return False

        try:
            garth.resume(str(self.token_file))
            self._authenticated = True
            return True
        except Exception:
            return False

    def is_authenticated(self) -> bool:
        """Check if currently authenticated"""
        return self._authenticated

    def logout(self) -> None:
        """Logout and remove stored tokens"""
        if self.token_file.exists():
            self.token_file.unlink()
        self._authenticated = False

    def ensure_authenticated(self, email: Optional[str] = None, password: Optional[str] = None) -> None:
        """
        Ensure authentication, prompting for credentials if needed

        Args:
            email: Optional email (if not provided, will try to resume)
            password: Optional password (if not provided, will try to resume)

        Raises:
            Exception: If authentication fails and no credentials provided
        """
        # Try to resume from saved tokens
        if self.resume():
            return

        # If no saved tokens, require credentials
        if not email or not password:
            raise Exception(
                "No saved authentication tokens found. Please provide email and password for first login."
            )

        self.login(email, password)
