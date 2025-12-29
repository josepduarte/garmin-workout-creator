# Garmin Workout Creator

A Python CLI tool for creating Garmin Connect workouts using natural language. Write workouts in plain text like "1km warmup @ 5:30, 3x 1km @ 4:45 + 2min rest" and sync them directly to your Garmin Connect account.

## Features

- **Natural language input**: Describe workouts in plain text, no complex UI needed
- **Dual parsing modes**: AI-powered (Claude/OpenAI) or regex-based parsing
- **Interactive TUI**: Edit workouts with arrow keys in a terminal interface
- **Direct Garmin sync**: Automatically uploads to Garmin Connect (no manual file imports)
- **Running workouts**: Optimized for running with pace, heart rate, and cadence targets

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
# Run the CLI tool
garmin-workout

# Enter your workout description when prompted
Enter workout: 1km warmup @ 5:30, 3x 1km @ 4:45 + 2min rest, 1km cooldown

# Edit in the interactive TUI, then sync to Garmin Connect
```

## Usage

### Basic Usage

```bash
# Interactive mode
garmin-workout

# With workout description
garmin-workout -w "1km warmup @ 5:30, 5x 1km @ 4:30 + 2min rest, cooldown"

# Skip Garmin Connect sync
garmin-workout -w "..." --no-sync
```

### Garmin Connect Authentication

First-time setup:

```bash
# Provide credentials via prompts (recommended)
garmin-workout -w "..."
# You'll be prompted for email/password on first run

# Or via environment variables
export GARMIN_EMAIL="your-email@example.com"
export GARMIN_PASSWORD="your-password"
garmin-workout -w "..."

# Or via command-line options
garmin-workout -w "..." -e your-email@example.com -p your-password
```

After first login, credentials are saved to `~/.garmin-workout-creator/garth_tokens` and automatically reused.

### Complete Workflow Example

```bash
# 1. Create workout
garmin-workout -w "1km warmup @ 5:30, 5x 1km @ 4:30 + 2min rest, 2km @ 165 bpm, cooldown"

# 2. Review parsed steps in TUI (use ↑↓ to navigate)
# 3. Press 'c' to continue to metadata screen
# 4. Enter workout name and scheduled date
# 5. Press 'Save & Finish'
# 6. Confirm upload to Garmin Connect (Y/n)
# 7. Sync your Garmin device to download the workout
```

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

**Phase 3: Interactive TUI** ✅ Complete
- Textual-based terminal interface
- Arrow key navigation for workout steps
- Metadata form (workout name, scheduled date)
- Clean, terminal-native UI
- Full parser + TUI integration

**Phase 4: Garmin Connect Integration** ✅ Complete
- OAuth authentication with garth (tokens persisted in ~/.garmin-workout-creator)
- Direct workout upload to Garmin Connect via python-garminconnect
- Workout JSON converter with reverse-engineered format support
- Interactive confirmation prompts
- `--no-sync` flag to skip upload
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

## Testing

```bash
# Run all tests
poetry run pytest

# Run with coverage
poetry run pytest --cov=garmin_workout_creator

# Run specific test file
poetry run pytest tests/test_models/test_workout.py -v
```

## Project Structure

```
garmin-workout-creator/
├── src/garmin_workout_creator/
│   ├── models/          # Pydantic data models ✅
│   ├── parsers/         # AI and regex parsers
│   ├── tui/            # Textual UI components
│   ├── garmin/         # Garmin Connect integration
│   └── utils/          # Utilities
├── tests/              # Test suite ✅
└── pyproject.toml      # Project configuration ✅
```

## License

MIT
