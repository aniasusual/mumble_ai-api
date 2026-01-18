# Mumble AI - Voice-First AI Language Tutor

A voice-first AI language tutor that mimics a real human tutor/language coach. The system provides specialized practice in writing, pronunciation, reading, speaking, and vocabulary through dedicated sub-agents that provide real-time feedback and comprehensive session tracking.

## Features

- **Voice-first interaction** with optional text fallback
- **Specialized coaching agents** for pronunciation, writing, reading, and speaking
- **Real-time feedback** using Speechace API for pronunciation and LanguageTool for grammar
- **Complete session transparency** with full history and audio playback
- **Adaptive learning** that tracks weak areas and provides targeted practice
- **Multi-language support** (starting with English)

## Tech Stack

- **Backend**: FastAPI (Python)
- **Agent Framework**: AGNO (multi-agent orchestration)
- **Database**: MongoDB Atlas
- **LLM**: Google Gemini 2.0 Flash
- **Package Manager**: Poetry

## Prerequisites

Before setting up the project, ensure you have the following installed:

- **Python 3.11+** - [Download Python](https://www.python.org/downloads/)
- **Poetry** - [Install Poetry](https://python-poetry.org/docs/#installation)
  ```bash
  # On macOS/Linux
  curl -sSL https://install.python-poetry.org | python3 -

  # On Windows (PowerShell)
  (Invoke-WebRequest -Uri https://install.python-poetry.org -UseBasicParsing).Content | py -
  ```
- **MongoDB Atlas Account** - [Sign up for MongoDB Atlas](https://www.mongodb.com/cloud/atlas/register)

## Local Setup

### 1. Clone the Repository

```bash
git clone <repository-url>
cd mumble_ai-api
```

### 2. Install Dependencies

Poetry will create a virtual environment and install all dependencies from `pyproject.toml`:

```bash
poetry install
```

This will install all required packages including:
- FastAPI
- AGNO
- Motor (async MongoDB driver)
- python-dotenv
- uvicorn

### 3. Set Up Environment Variables

Create a `.env` file in the project root directory:

```bash
cp .env.example .env  # If you have an example file
# OR create .env manually
```

Add the following environment variables to `.env`:

```env
# MongoDB Configuration
MONGODB_URL=mongodb+srv://<username>:<password>@<cluster>.mongodb.net/?appName=<appname>
MONGODB_DATABASE=mumble_ai

# Frontend Configuration
FRONTEND_URL=http://localhost:5173

# Google API Key (for Gemini)
GOOGLE_API_KEY=your_google_api_key_here
```

**Getting your credentials:**

- **MongoDB URL**:
  1. Go to [MongoDB Atlas](https://cloud.mongodb.com/)
  2. Create a new cluster (free tier available)
  3. Click "Connect" → "Connect your application"
  4. Copy the connection string
  5. Replace `<username>`, `<password>`, and `<cluster>` with your values

- **Google API Key**:
  1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
  2. Create a new API key
  3. Copy and paste into `.env`

### 4. Activate Poetry Virtual Environment

```bash
poetry shell
```

This activates the virtual environment created by Poetry.

### 5. Run the Development Server

```bash
# Option 1: Using Poetry
poetry run python -m src.main

# Option 2: If you're already in the poetry shell
python -m src.main

# Option 3: Using the built-in server command
poetry run agno serve
```

The server will start on `http://localhost:8000` by default.

### 6. Verify Installation

Open your browser and visit:
- Health check: `http://localhost:8000/health`
- API documentation: `http://localhost:8000/docs`

You should see:
```json
{"status": "healthy"}
```

## Project Structure

```
mumble_ai-api/
├── src/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── agents/
│   │   ├── mainAgent.py        # Main orchestrator team
│   │   └── planningAgent.py    # Curriculum planning agent
│   ├── api/
│   │   └── main.py             # API routes (coming soon)
│   ├── core/
│   │   └── database.py         # MongoDB connection manager
│   └── prompts/
│       ├── mainAgent.py        # Main agent system prompt
│       └── planningAgent.py    # Planning agent prompt
├── .env                        # Environment variables (not in git)
├── .gitignore                  # Git ignore file
├── pyproject.toml              # Poetry dependencies
├── poetry.lock                 # Locked dependency versions
└── README.md                   # This file
```

## Common Poetry Commands

```bash
# Install dependencies
poetry install

# Add a new package
poetry add <package-name>

# Add a development dependency
poetry add --group dev <package-name>

# Update dependencies
poetry update

# Activate virtual environment
poetry shell

# Run a command in the virtual environment
poetry run <command>

# Exit virtual environment
exit  # or Ctrl+D

# Show installed packages
poetry show

# Remove a package
poetry remove <package-name>
```

## Development

### Running Tests (Coming Soon)

```bash
poetry run pytest
```

### Code Formatting

```bash
# Format code with black
poetry run black src/

# Sort imports
poetry run isort src/
```

### Type Checking

```bash
poetry run mypy src/
```

## API Endpoints

### REST API

```
GET  /health                    # Health check
POST /api/sessions              # Create new session
GET  /api/sessions/{session_id} # Get session details
GET  /api/sessions/{user_id}    # Get all user sessions
```

### WebSocket

```
/ws/sessions/{session_id}       # Real-time voice conversation
```

## Architecture

This project uses a **multi-agent architecture** with AGNO framework:

- **MainAgent (Team)**: Primary orchestrator that manages the session and delegates to specialized coaches
- **PronunciationCoachAgent**: Real-time phoneme-level pronunciation feedback
- **WritingCoachAgent**: Grammar and writing structure feedback
- **ReadingCoachAgent**: Reading fluency and comprehension assessment
- **SpeakingCoachAgent**: Conversational practice and fluency development
- **VocabularyCoach**: Spaced repetition vocabulary drills

For detailed architecture documentation, see [ARCHITECTURE.md](ARCHITECTURE.md).

## Troubleshooting

### Poetry Install Issues

**Issue**: `does not contain any element`
```bash
# Solution: Ensure src/__init__.py exists
touch src/__init__.py
poetry install
```

**Issue**: `command not found: poetry`
```bash
# Solution: Add Poetry to PATH
export PATH="$HOME/.local/bin:$PATH"  # On macOS/Linux
```

### MongoDB Connection Issues

**Issue**: `MONGODB_URL environment variable is not set`
```bash
# Solution: Ensure .env file exists and contains MONGODB_URL
cat .env | grep MONGODB_URL
```

**Issue**: `Connection timeout` or `Authentication failed`
```bash
# Solution: Check your MongoDB Atlas settings
# 1. Whitelist your IP address in Network Access
# 2. Verify database user credentials
# 3. Check connection string format
```

### Import Errors

**Issue**: `ModuleNotFoundError: No module named 'agno'`
```bash
# Solution: Ensure you're in the poetry environment
poetry shell
poetry install
```

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Commit your changes: `git commit -m 'Add some feature'`
4. Push to the branch: `git push origin feature/your-feature`
5. Submit a pull request

## License

[Add your license here]

## Support

For issues and questions:
- Open an issue on GitHub
- Contact: [your-email@example.com]

## Roadmap

- [x] Basic FastAPI setup
- [x] MongoDB integration
- [x] AGNO multi-agent framework
- [ ] Pronunciation coach agent with Speechace API
- [ ] Writing coach agent with LanguageTool
- [ ] Reading coach agent
- [ ] Speaking coach agent
- [ ] WebSocket real-time communication
- [ ] Session history and progress tracking
- [ ] Adaptive curriculum generation
- [ ] Multi-language support
