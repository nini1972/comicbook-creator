# 🎨 ComicBook Creator

An AI-powered comic book generation system using **CrewAI**, **Google Gemini 2.5 Flash**, and multiple LLMs for intelligent multi-agent orchestration.

## ✨ Features

- **6-Agent Workflow**: Story Writer, Visual Director, Orchestrator, Evaluator, Panel Inspector, and Comic Assembler
- **Intelligent Image Generation**: Uses Google Gemini 2.5 Flash Image Preview for high-quality comic panels
- **Character Consistency**: Maintains visual consistency across all panels using reference images
- **Lore Database**: Long-term memory system that tracks characters and story across multiple chapters
- **Automatic Retry & Fallback**: Robust error handling with automatic LLM fallback (Claude → GPT-4o)
- **Quality Validation**: Multi-stage validation ensures all panels meet quality standards
- **Metadata Management**: Centralized story metadata for reliable agent coordination

## 🏗️ Architecture

```
┌─────────────────┐
│  Story Writer   │ → Creates narrative + panels (GPT-4o)
└────────┬────────┘
         ↓
┌─────────────────┐
│Visual Director  │ → Generates 6 images (GPT-4o + Gemini)
└────────┬────────┘
         ↓
┌─────────────────┐
│  Orchestrator   │ → Manages workflow + retries (GPT-4o)
└────────┬────────┘
         ↓
┌─────────────────┐
│   Evaluator     │ → Validates quality (Claude Sonnet 4)
└────────┬────────┘
         ↓
┌─────────────────┐
│Panel Inspector  │ → Checks registry (Claude Sonnet 4)
└────────┬────────┘
         ↓
┌─────────────────┐
│Comic Assembler  │ → Creates final markdown/PDF (Claude Sonnet 4)
└─────────────────┘
```

## 📋 Prerequisites

- **Python** >=3.10 <3.14
- **UV** package manager
- **API Keys**:
  - Google Gemini API (for image generation)
  - OpenAI API (for GPT-4o agents)
  - Anthropic API (for Claude Sonnet 4 agents)

## 🚀 Installation

### 1. Install UV

```bash
pip install uv
```

### 2. Clone and Setup

```bash
cd backend
uv sync
```

### 3. Configure API Keys

Create a `.env` file in the project root:

```env
# Required API Keys
GOOGLE_API_KEY=your_google_gemini_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here
```

See `.env.example` for more details.

## 🎬 Running the Project

### Quick Test Run

Generates a comic with the topic "A brave cat who wants to fly":

```powershell
cd backend
uv run python tests/test_full_run.py
```

Or use the batch file:

```cmd
.\run_full_test.bat
```

### Interactive Run

Prompts you to enter a custom topic:

```powershell
cd backend
uv run python tests/run_crew.py
```

### Run with Web UI

**Terminal 1 - Backend:**

```powershell
cd backend
uv run python api.py
```

**Terminal 2 - Frontend:**

```powershell
cd frontend
npm run dev
```

Then open `http://localhost:3000`

## 📊 Understanding the Workflow

1. **Story Writer** creates the narrative structure:
   - Reads lore database for continuity
   - Creates title, chapter info, and 6 panel descriptions
   - Saves everything to centralized metadata

2. **Visual Director** generates images:
   - Creates character references for consistency
   - Generates 6 panel images using Gemini 2.5 Flash
   - Updates panel registry with filenames

3. **Orchestrator** manages the process:
   - Delegates tasks to agents
   - Monitors generation status
   - Handles retries for failed panels

4. **Evaluator** validates quality:
   - Checks each panel for completeness
   - Verifies image quality and relevance
   - Marks panels as verified or failed

5. **Panel Inspector** audits the registry:
   - Ensures all 6 panels are generated
   - Validates file paths and metadata
   - Reports any missing or invalid panels

6. **Comic Assembler** creates final output:
   - Assembles verified panels into comic layout
   - Generates markdown and optionally PDF
   - Updates lore database with chapter summary

## 📁 Output Structure

```
backend/output/
├── latest_comic.md                  # Final comic markdown
├── panel_registry.yaml              # Panel tracking/status
├── lore_database.yaml               # Story memory across chapters
├── story_metadata_story_*.yaml      # Story details & metadata
├── comic_panels/
│   ├── panel_001_*.png              # Generated panel images
│   ├── panel_002_*.png
│   └── ...
├── character_references/
│   ├── felix_reference.png          # Character consistency images
│   └── character_cache.txt
└── comic_exports/
    └── *.pdf                        # Exported PDFs (if enabled)
```

## 🛡️ Fallback & Error Handling

The system includes automatic fallback mechanisms:

- **LLM Fallback**: If Claude (Anthropic) is overloaded or unavailable, automatically switches to GPT-4o
- **Retry Logic**: Up to 3 retries with exponential backoff for failed operations
- **Panel Regeneration**: Orchestrator can retry failed panel generation
- **Graceful Degradation**: Continues workflow even if some components fail

## 🔧 Configuration

### Agents

Edit `src/visual_comic_crew/config/agents.yaml` to customize:

- Agent roles and goals
- LLM models (GPT-4o, Claude Sonnet 4)
- Tool assignments
- Delegation settings

### Tasks

Edit `src/visual_comic_crew/config/tasks.yaml` to customize:

- Task descriptions
- Expected outputs
- Agent assignments
- Task dependencies

## 🧪 Testing

Run individual test suites:

```powershell
# Test lore database
uv run python tests/test_lore_database.py

# Test orchestrator tools
uv run python tests/test_orchestrator_evaluator_tools.py

# Full workflow test
uv run python tests/test_full_run.py
```

## 🧪 Testing

Run individual test suites:

```powershell
# Test lore database
uv run python tests/test_lore_database.py

# Test orchestrator tools
uv run python tests/test_orchestrator_evaluator_tools.py

# Full workflow test
uv run python tests/test_full_run.py
```

## 🐛 Troubleshooting

### Killing Backend Process

Find and kill the backend process (usually port 8002):

```powershell
# Find Process ID
(Get-NetTCPConnection -LocalPort 8002).OwningProcess

# Kill Process
stop-process -Id <ProcessID> -Force
```

### Killing Frontend Process

```powershell
stop-process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -Force
```

### API Key Issues

If you see "No LLM/Generative API credentials detected":

1. Ensure `.env` file exists in project root
2. Verify key names: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`
3. Check that keys are not empty or None

### Image Generation Failures

If image generation fails:

1. Verify `GOOGLE_API_KEY` is valid
2. Check Gemini API quota and limits
3. Review `backend/output/panel_registry.yaml` for error details

## 📚 Key Technologies

- **[CrewAI](https://crewai.com)**: Multi-agent orchestration framework
- **[Google Gemini 2.5 Flash](https://ai.google.dev/)**: Image generation
- **[OpenAI GPT-4o](https://platform.openai.com/)**: Text generation & reasoning
- **[Anthropic Claude Sonnet 4](https://www.anthropic.com/)**: Validation & quality assurance
- **[UV](https://docs.astral.sh/uv/)**: Fast Python package management

## 📖 Documentation

- Project Documentation: See `/backend/QUICKSTART.md`, `/backend/IMPLEMENTATION_ROADMAP.md`
- CrewAI Docs: <https://docs.crewai.com>
- API Reference: See `backend/api.py` for REST endpoints

## 🤝 Support

For support, questions, or feedback:

- Visit [CrewAI documentation](https://docs.crewai.com)
- Join [CrewAI Discord](https://discord.com/invite/X4JWnZnxPb)
- Check out our [GitHub repository](https://github.com/nini1972/comicbook-creator)

## 📊 Code Quality

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b923bd9fc0bf4e4d8666236c79b2ec2c)](https://app.codacy.com/gh/nini1972/comicbook-creator/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

---

**Built with CrewAI** 🚀 | **Powered by Gemini & GPT-4o** 🤖
