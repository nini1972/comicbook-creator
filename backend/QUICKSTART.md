# ComicBook Creator - Quick Start Guide

## ✅ Installation Complete

Your dependencies are already installed (139 packages including CrewAI).

## 🚀 How to Run Your Project

You don't need `crewai install` or `crewai run` commands. Instead, use UV scripts:

### 1️⃣ Make sure you have your API keys in `.env` file

```bash
cd ..
# Edit .env file with your API keys (use .env.example as template)
```

### 2️⃣ Run the comic creator

```bash
# From the backend directory:
uv run run_crew
```

## Available Commands

All commands should be run from the `backend/` directory:

- **`uv run run_crew`** - Run the comic creation crew (main command)
- **`uv run train`** - Train the crew
- **`uv run replay`** - Replay a previous run
- **`uv run test`** - Run tests

## Running the API Server

To start the FastAPI backend server:

```bash
uv run uvicorn server:app --reload --port 8002
```

Or:

```bash
uv run python server.py
```

## Installing Dependencies

### Option 1: Using UV (Recommended)

```bash
uv sync
```

### Option 2: Using pip with requirements.txt

```bash
pip install -r requirements.txt
```

Or install just the main dependencies:

```bash
pip install -r requirements-main.txt
```

## Troubleshooting

- **Dependencies not found?** Run `uv sync` from the backend directory
- **Need to add packages?** Edit `pyproject.toml` then run `uv sync` (or regenerate requirements.txt with `uv export --format requirements-txt --no-hashes --output-file requirements.txt`)
- **Python version issues?** This project requires Python >=3.10, <3.14
- **pywin32 errors?** Run: `.venv\Scripts\python.exe .venv\Lib\site-packages\win32\scripts\pywin32_postinstall.py -install`

## Project Structure

- `src/visual_comic_crew/` - Main crew implementation
- `src/visual_comic_crew/config/` - Agent and task configurations
- `src/visual_comic_crew/tools/` - Custom tools for the crew
- `output/` - Generated comics will be saved here
