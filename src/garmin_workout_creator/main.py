"""FastAPI web application for Garmin Workout Creator"""

from datetime import date
from typing import Optional
from fastapi import FastAPI, HTTPException, status
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
import os

from garmin_workout_creator.parsers.regex_parser import RegexWorkoutParser
from garmin_workout_creator.garmin.client import GarminClient
from garmin_workout_creator.models import Workout

app = FastAPI(title="Garmin Workout Creator", version="0.1.0")

# Initialize parser and client
parser = RegexWorkoutParser()
garmin_client = GarminClient()

# Serve static files
static_dir = os.path.join(os.path.dirname(__file__), "static")
os.makedirs(static_dir, exist_ok=True)
app.mount("/static", StaticFiles(directory=static_dir), name="static")


# Request/Response models
class ParseRequest(BaseModel):
    text: str = Field(..., description="Natural language workout description")


class WorkoutMetadata(BaseModel):
    name: str = Field(default="Untitled Workout", description="Workout name")
    scheduled_date: Optional[date] = Field(None, description="Scheduled date")
    notes: Optional[str] = Field(None, description="Additional notes")


class UploadRequest(BaseModel):
    workout_text: str = Field(..., description="Workout description")
    metadata: WorkoutMetadata = Field(..., description="Workout metadata")
    garmin_email: Optional[str] = Field(None, description="Garmin Connect email")
    garmin_password: Optional[str] = Field(None, description="Garmin Connect password")


class ParseResponse(BaseModel):
    success: bool
    workout: Optional[dict] = None
    error: Optional[str] = None


class UploadResponse(BaseModel):
    success: bool
    workout_id: Optional[str] = None
    message: str
    error: Optional[str] = None


@app.get("/")
async def root():
    """Serve the main HTML page"""
    index_file = os.path.join(static_dir, "index.html")
    if os.path.exists(index_file):
        return FileResponse(index_file)
    return {"message": "Garmin Workout Creator API", "docs": "/docs"}


@app.post("/api/parse", response_model=ParseResponse)
async def parse_workout(request: ParseRequest):
    """
    Parse a natural language workout description

    Returns the parsed workout structure with steps
    """
    try:
        workout = parser.parse(request.text)
        return ParseResponse(
            success=True,
            workout=workout.model_dump(mode='json')
        )
    except ValueError as e:
        return ParseResponse(
            success=False,
            error=str(e)
        )
    except Exception as e:
        return ParseResponse(
            success=False,
            error=f"Unexpected error: {str(e)}"
        )


@app.post("/api/upload", response_model=UploadResponse)
async def upload_workout(request: UploadRequest):
    """
    Parse workout text and upload to Garmin Connect

    Requires Garmin credentials (via request or environment variables)
    """
    try:
        # Parse the workout
        workout = parser.parse(request.workout_text)

        # Apply metadata
        workout.name = request.metadata.name
        workout.scheduled_date = request.metadata.scheduled_date
        workout.notes = request.metadata.notes

        # Connect to Garmin
        try:
            garmin_client.ensure_connected(
                email=request.garmin_email,
                password=request.garmin_password
            )
        except Exception as e:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail=f"Garmin authentication failed: {str(e)}"
            )

        # Upload the workout
        result = garmin_client.upload_workout(workout)

        return UploadResponse(
            success=True,
            workout_id=str(result.get("workoutId", "")),
            message="Workout uploaded successfully to Garmin Connect!"
        )

    except ValueError as e:
        return UploadResponse(
            success=False,
            message="Failed to parse workout",
            error=str(e)
        )
    except HTTPException:
        raise
    except Exception as e:
        return UploadResponse(
            success=False,
            message="Failed to upload workout",
            error=str(e)
        )


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "garmin-workout-creator"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
