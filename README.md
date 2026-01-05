# Garmin Workout Creator

A web application for creating Garmin Connect workouts using natural language. Write workouts in plain text like "1km warmup @ 5:30, 3x 1km @ 4:45 + 2min rest" and sync them directly to your Garmin Connect account.

## Features

- **Natural language input**: Describe workouts in plain text, no complex UI needed
- **Dual parsing modes**: AI-powered (Claude/OpenAI) or regex-based parsing
- **Web interface**: Modern, responsive web UI accessible from any browser
- **Direct Garmin sync**: Automatically uploads to Garmin Connect (no manual file imports)
- **Running workouts**: Optimized for running with pace, heart rate, and cadence targets
- **Live preview**: See your parsed workout steps before uploading

## Installation

Requires Python 3.10 or higher.

```bash
# Clone the repository
git clone https://github.com/yourusername/garmin-workout-creator.git
cd garmin-workout-creator

# Install with Poetry
poetry install

# Or install with pip
pip install -e .
```

## Quick Start

```bash
# Start the web server
poetry run python -m uvicorn garmin_workout_creator.main:app --reload

# Or use the shorthand
poetry run python src/garmin_workout_creator/main.py
```

Then open your browser to `http://localhost:8000`

## Usage

### Web Interface

1. **Describe your workout** in the text area using natural language
2. **Preview the parsed steps** to verify they're correct
3. **Fill in workout details** (name, scheduled date, notes)
4. **Enter Garmin credentials** or set them as environment variables
5. **Click "Upload to Garmin Connect"** to sync your workout
6. **Sync your Garmin device** to download the workout

### Garmin Connect Authentication

You can provide credentials in three ways:

1. **Via web form** (enter each time)
2. **Environment variables** (recommended for repeated use):
   ```bash
   export GARMIN_EMAIL="your-email@example.com"
   export GARMIN_PASSWORD="your-password"
   ```
3. **`.env` file** (copy `.env.example` to `.env` and fill in):
   ```bash
   GARMIN_EMAIL=your-email@example.com
   GARMIN_PASSWORD=your-password
   ```

After first login, credentials are saved to `~/.garmin-workout-creator/garth_tokens` and automatically reused.

## Configuration

Copy [.env.example](.env.example) to `.env` and configure:

```bash
# Parser mode: "ai" or "regex"
PARSER_MODE=regex

# AI provider (if using ai mode): "claude" or "openai"
AI_PROVIDER=claude

# API keys (only needed for AI mode)
ANTHROPIC_API_KEY=your-key-here
OPENAI_API_KEY=your-key-here
```

## Workout Syntax

The tool supports flexible natural language descriptions:

- **Distance-based**: `1km warmup @ 5:30` (1km at 5:30/km pace)
- **Time-based**: `5min @ 165 bpm` (5 minutes at 165 heart rate)
- **Intervals**: `3x 1km @ 4:45 + 2min rest` (3 repetitions of 1km interval + 2min recovery)
- **Open duration**: `cooldown` (open cooldown, press lap to end)

## API Documentation

The FastAPI application provides interactive API documentation:

- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

### API Endpoints

- `POST /api/parse` - Parse workout text and return structured data
- `POST /api/upload` - Parse and upload workout to Garmin Connect
- `GET /health` - Health check endpoint

## Development

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=garmin_workout_creator

# Run specific test file
poetry run pytest tests/test_models/test_workout.py -v
```

### Code Quality

```bash
# Format code
poetry run black src/ tests/

# Lint code
poetry run ruff check src/ tests/

# Type checking
poetry run mypy src/
```

### Development Server

```bash
# Run with auto-reload
poetry run uvicorn garmin_workout_creator.main:app --reload --host 0.0.0.0 --port 8000
```

## Project Structure

```
garmin-workout-creator/
├── src/garmin_workout_creator/
│   ├── models/          # Pydantic data models
│   ├── parsers/         # AI and regex parsers
│   ├── garmin/          # Garmin Connect integration
│   ├── static/          # Web frontend (HTML/CSS/JS)
│   └── main.py          # FastAPI application
├── tests/               # Test suite
└── pyproject.toml       # Project configuration
```

## Development Status

**Phase 1: Foundation & Data Models** ✅ Complete
- Pydantic models for workouts, steps, and targets
- Comprehensive validation logic
- 56 unit tests (100% passing)

**Phase 2: Regex Parser** ✅ Complete
- Pattern matching for common workout formats
- Support for distance, time, pace, and heart rate targets
- Flexible input normalization (k→km, mins→min, etc.)
- Interval and repeat parsing (e.g., "3x 1km + 2min rest")
- 28 unit tests (100% passing)
- **Total: 84 tests passing**

**Phase 3: Web Interface** ✅ Complete
- FastAPI backend with REST API
- Modern, responsive web UI
- Real-time workout preview
- Form validation and error handling

**Phase 4: Garmin Connect Integration** ✅ Complete
- OAuth authentication with garth (tokens persisted in ~/.garmin-workout-creator)
- Direct workout upload to Garmin Connect via python-garminconnect
- Workout JSON converter with reverse-engineered format support
- Interactive confirmation prompts
- Environment variable support for credentials

⚠️ **Note**: The Garmin Connect workout JSON format requires reverse engineering. The converter includes placeholder values that must be verified by:
1. Creating test workouts in Garmin Connect
2. Using browser dev tools to capture actual API calls
3. Running `python examples/reverse_engineer_format.py`
4. Updating constants in `src/garmin_workout_creator/garmin/converter.py`

**Coming Soon**:
- AI-powered parser (Claude/OpenAI)
- Verified Garmin JSON format constants
- Template saving/loading
- Multiple sport types (cycling, swimming)

## Examples

See the `examples/` directory for Python scripts demonstrating:
- `simple_workout.py` - Basic workout creation
- `parse_workout.py` - Parsing workouts from text
- `complete_workflow.py` - Full workflow from parsing to upload
- `reverse_engineer_format.py` - Analyzing Garmin JSON format

## License

MIT
