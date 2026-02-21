# 🎨 ComicBook Creator

An AI-powered comic book generation system powered by **CrewAI**, featuring intelligent multi-agent orchestration with **Google Gemini 2.5 Flash** for image generation and multiple LLMs for story creation and quality assurance.

[![Codacy Badge](https://app.codacy.com/project/badge/Grade/b923bd9fc0bf4e4d8666236c79b2ec2c)](https://app.codacy.com/gh/nini1972/comicbook-creator/dashboard?utm_source=gh&utm_medium=referral&utm_content=&utm_campaign=Badge_grade)

## ✨ What is ComicBook Creator?

ComicBook Creator is a sophisticated AI system that automatically generates complete comic books from simple text prompts. It uses a multi-agent architecture where specialized AI agents collaborate to create, validate, and assemble professional-quality comic panels.

**Key Features:**

- 🤖 **6 AI Agents** working in concert (Story Writer, Visual Director, Orchestrator, Evaluator, Inspector, Assembler)
- 🎨 **High-Quality Images** generated with Google Gemini 2.5 Flash Image Preview
- 🧠 **Long-Term Memory** via Lore Database for multi-chapter story continuity
- 🔄 **Automatic Retry & Fallback** for robust error handling
- ✅ **Multi-Stage Validation** ensuring quality output
- 🌐 **Web Interface** for easy interaction

## 🏗️ Project Structure

```
comicbook-creator/
├── backend/              # Python CrewAI backend
│   ├── src/             # Source code
│   │   ├── image_generator/      # Gemini image generation
│   │   ├── utils/                # Utilities & helpers
│   │   └── visual_comic_crew/    # Main CrewAI implementation
│   ├── tests/           # Test suite
│   ├── output/          # Generated comics & metadata
│   └── api.py           # FastAPI server
│
├── frontend/            # Next.js React frontend
│   ├── src/
│   │   ├── app/        # Next.js app router
│   │   └── components/ # React components
│   └── public/         # Static assets
│
├── .env                 # API keys configuration
└── run_full_test.bat    # Quick test runner
```

## 🚀 Quick Start

### 1. Prerequisites

- **Python** >=3.10 <3.14
- **Node.js** >=18
- **UV** package manager (`pip install uv`)
- **API Keys**: Google Gemini, OpenAI, Anthropic

### 2. Setup API Keys

Create a `.env` file in the project root:

```env
GOOGLE_API_KEY=your_google_gemini_api_key
OPENAI_API_KEY=your_openai_api_key
ANTHROPIC_API_KEY=your_anthropic_api_key
```

### 3. Install Dependencies

**Backend:**

```powershell
cd backend
uv sync
```

**Frontend:**

```powershell
cd frontend
npm install
```

### 4. Run the Application

**Option A: Command Line (Quick Test)**

```powershell
.\run_full_test.bat
```

**Option B: Command Line (Interactive)**

```powershell
cd backend
uv run python tests/run_crew.py
```

**Option C: Web Interface**

Terminal 1:

```powershell
cd backend
uv run python api.py
```

Terminal 2:

```powershell
cd frontend
npm run dev
```

Then open `http://localhost:3000`

## 🎬 How It Works

1. **Story Writer** creates a narrative with 6 panel descriptions
2. **Visual Director** generates images for each panel using Gemini
3. **Orchestrator** manages workflow and handles retries
4. **Evaluator** validates quality of each generated panel
5. **Panel Inspector** ensures all panels meet requirements
6. **Comic Assembler** creates final markdown/PDF output

The system maintains character consistency across panels, stores story memory in a lore database for multi-chapter continuity, and automatically handles errors with intelligent fallback mechanisms.

## 📊 Output

Generated comics are saved to `backend/output/`:

```
output/
├── latest_comic.md              # Final comic
├── panel_registry.yaml          # Panel tracking
├── lore_database.yaml           # Story memory
├── comic_panels/                # Generated images
└── comic_exports/               # PDFs (optional)
```

## 🛠️ Technologies

**Backend:**

- [CrewAI](https://crewai.com) - Multi-agent framework
- [Google Gemini 2.5 Flash](https://ai.google.dev/) - Image generation
- [OpenAI GPT-4o](https://platform.openai.com/) - Story & reasoning
- [Anthropic Claude Sonnet 4](https://www.anthropic.com/) - Validation
- [FastAPI](https://fastapi.tiangolo.com/) - REST API
- [UV](https://docs.astral.sh/uv/) - Package management

**Frontend:**

- [Next.js 15](https://nextjs.org/) - React framework
- [TypeScript](https://www.typescriptlang.org/)
- [Tailwind CSS](https://tailwindcss.com/)

## 📚 Documentation

- **Backend Setup**: See [backend/README.md](backend/README.md)
- **Quick Start Guide**: See [backend/QUICKSTART.md](backend/QUICKSTART.md)
- **Implementation Details**: See [backend/IMPLEMENTATION_ROADMAP.md](backend/IMPLEMENTATION_ROADMAP.md)
- **Frontend Setup**: See [frontend/README.md](frontend/README.md)

## 🧪 Testing

Run the test suite:

```powershell
cd backend

# Test lore database
uv run python tests/test_lore_database.py

# Test orchestrator workflow
uv run python tests/test_orchestrator_evaluator_tools.py

# Full end-to-end test
uv run python tests/test_full_run.py
```

## 🐛 Troubleshooting

**API Key Issues:**

- Ensure all three API keys are in `.env` file
- Verify key names: `GOOGLE_API_KEY`, `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`

**Port Conflicts:**

```powershell
# Kill backend (port 8002)
stop-process -Id (Get-NetTCPConnection -LocalPort 8002).OwningProcess -Force

# Kill frontend (port 3000)
stop-process -Id (Get-NetTCPConnection -LocalPort 3000).OwningProcess -Force
```

**Image Generation Failures:**

- Check Google Gemini API quota
- Verify `GOOGLE_API_KEY` is valid
- Review `backend/output/panel_registry.yaml` for errors

## 🤝 Contributing

This is a personal project built with CrewAI. Feel free to fork and adapt for your own use!

## 📄 License

See LICENSE file for details.

## 🌟 Acknowledgments

Built with:

- [CrewAI](https://crewai.com) for multi-agent orchestration
- [Google Gemini](https://ai.google.dev/) for image generation
- [OpenAI](https://openai.com) & [Anthropic](https://anthropic.com) for language models

---

**Made with ❤️ using AI Agents** | **Powered by Gemini & GPT-4o** 🤖
