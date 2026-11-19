# NexCode - Autonomous AI Coding Assistant

A production-grade AI coding assistant with dual execution modes: **File Mode** for repo-level analysis and **Code Mode** for single-file snippets. Powered by Google Gemini Flash with a 200K context window.

## Features

- **Dual Execution Modes**
  - **File Mode**: Full workspace analyzer with multi-file agent capabilities
  - **Code Mode**: Isolated snippet helper for quick prototyping

- **Zero-Cost AI Engine**
  - Primary: Google Gemini Flash (gemini-1.5-flash) with 1M token free tier
  - Optional: OpenRouter Free fallback
  - 200K token context window (user-facing limit)

- **Intelligent Context Management**
  - Live token usage meter with visual progress bar
  - Automatic file prioritization when context exceeds limits
  - Smart truncation to stay within budget

- **Notebook System**
  - Create and manage multiple coding sessions
  - Session history with chronological grouping
  - Persistent storage for context and state

- **Collapsible Sidebar**
  - Quick access to notebook history
  - Toggle between full and icon-only views
  - Delete sessions with one click

- **File Mode Features**
  - Drag-and-drop folder upload
  - Interactive file tree view
  - Side-by-side code diff previewer
  - Step-by-step agent milestones

- **Code Mode Features**
  - Full-width conversational interface
  - Code snippet box with syntax highlighting
  - Copy to clipboard functionality
  - Safe mock execution (5-second timeout)

- **SEO Ready**
  - Google Search Console compatible
  - Dynamic sitemap.xml generation
  - robots.txt configuration
  - Open Graph and Twitter Card metadata

## Installation

### Prerequisites

- Python 3.10 or higher
- pip (Python package manager)

### Setup

1. Clone the repository:
```bash
git clone <repository-url>
cd NexCode
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure environment variables:
```bash
cp .env.example .env
```

4. Edit `.env` and add your API key:
```env
GEMINI_API_KEY=your_free_gemini_api_key_here
OPENROUTER_API_KEY=optional_openrouter_key_here
MAX_CONTEXT_TOKENS=200000
PORT=9000
GOOGLE_SITE_VERIFICATION=GOOGLE_VERIFICATION_TOKEN_HERE
```

### Getting a Gemini API Key

1. Go to [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Sign in with your Google account
3. Create a new API key (free tier)
4. Copy the key to your `.env` file

## Running the Application

### Development Mode

```bash
python -m app.main
```

Or using uvicorn directly:
```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### Production Mode

```bash
uvicorn app.main:app --host 0.0.0.0 --port 9000 --workers 4
```

The application will be available at `http://localhost:9000`

## Testing

Run the complete test suite:

```bash
pytest -v
```

Run specific test files:
```bash
pytest tests/test_mode_endpoints.py -v
pytest tests/test_notebook_history.py -v
pytest tests/test_token_limiter.py -v
pytest tests/test_gsc_routes.py -v
```

## Project Structure

```
NexCode/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI application entry point
│   ├── config.py            # Configuration and settings
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py       # Pydantic models and schemas
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── mode.py          # Mode switching endpoints
│   │   ├── notebook.py     # Notebook CRUD endpoints
│   │   ├── llm.py           # LLM chat endpoints
│   │   └── seo.py           # SEO routes (robots.txt, sitemap)
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm.py           # AI provider (Gemini + OpenRouter)
│   │   └── token_counter.py # Token counting and context management
│   ├── static/
│   │   └── app.js           # Frontend JavaScript
│   └── templates/
│       └── index.html       # Main HTML template
├── tests/
│   ├── __init__.py
│   ├── test_mode_endpoints.py
│   ├── test_notebook_history.py
│   ├── test_token_limiter.py
│   └── test_gsc_routes.py
├── requirements.txt
├── pytest.ini
├── .env.example
└── README.md
```

## Usage Guide

### File Mode

1. Click the upload zone or drag-and-drop a codebase folder
2. The system will analyze the workspace and display file tree
3. Type your request in the chat input (e.g., "Analyze the authentication flow")
4. View step-by-step agent milestones and code diffs
5. Monitor token usage in the header progress bar

### Code Mode

1. Click the `</> CODE` button in the top right
2. The interface switches to a single-column layout
3. Ask questions about code snippets, debugging, or API usage
4. Use the code snippet box to write and test code
5. Copy code to clipboard or run with safe mock execution

### Notebook Management

1. Click `+ New Notebook` to start a fresh session
2. Click any history item to restore a previous session
3. Hover over history items and click the trash icon to delete
4. Toggle sidebar with the `«` / `»` button

## API Endpoints

### Mode Management
- `GET /api/mode/current` - Get current mode and session ID
- `POST /api/mode/switch` - Switch between FILE and CODE mode
- `POST /api/mode/reset` - Reset current session

### Notebook Management
- `POST /api/notebook/create` - Create a new notebook
- `GET /api/notebook/` - List all notebooks
- `GET /api/notebook/{id}` - Get specific notebook
- `DELETE /api/notebook/{id}` - Delete a notebook
- `PUT /api/notebook/{id}` - Update notebook context

### LLM Services
- `POST /api/llm/chat` - Send chat message and get AI response
- `GET /api/llm/token-usage` - Get token count for text
- `POST /api/llm/analyze-workspace` - Analyze uploaded workspace

### SEO Routes
- `GET /robots.txt` - Robots.txt for search engines
- `GET /sitemap.xml` - Dynamic sitemap
- `GET /favicon.ico` - Favicon

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `GEMINI_API_KEY` | Google Gemini API key | Required |
| `OPENROUTER_API_KEY` | OpenRouter API key (optional) | None |
| `MAX_CONTEXT_TOKENS` | Maximum context tokens | 200000 |
| `PORT` | Server port | 9000 |
| `GOOGLE_SITE_VERIFICATION` | Google Search Console verification token | None |

### Token Limits

- **User-facing limit**: 200,000 tokens
- **Gemini Flash capacity**: 1,000,000 tokens (free tier)
- **Progress bar colors**:
  - Green: < 70% usage
  - Yellow: 70-90% usage
  - Red: > 90% usage

### File Exclusions

The following are automatically excluded from workspace analysis:
- `.git/` directories
- `node_modules/` directories
- `venv/` virtual environments
- `__pycache__/` Python cache
- Binary files (`.pyc`, etc.)

## Architecture

### Backend
- **FastAPI**: Modern, fast web framework
- **uvicorn**: ASGI server
- **httpx**: Async HTTP client for API calls
- **tiktoken**: Token counting
- **pydantic**: Data validation

### Frontend
- **Pure HTML5/CSS3/JavaScript**: No framework dependencies
- **Responsive design**: Mobile-friendly layout
- **Dark theme**: Developer-focused UI
- **Real-time updates**: Live token meter and chat

### AI Provider
- **Primary**: Google Gemini Flash via REST API
- **Fallback**: OpenRouter (optional)
- **Token counting**: tiktoken (cl100k_base encoding)
- **Context management**: Smart prioritization and truncation

## Development

### Adding New Features

1. Add routes in `app/routers/`
2. Implement services in `app/services/`
3. Update schemas in `app/models/schemas.py`
4. Add tests in `tests/`
5. Update documentation

### Code Style

- Follow PEP 8 for Python code
- Use type hints where appropriate
- Write descriptive commit messages
- Add tests for new features

## Troubleshooting

### API Key Issues

If you see "Connection failed - check API configuration":
1. Verify your `GEMINI_API_KEY` is set in `.env`
2. Check the key is valid at [Google AI Studio](https://makersuite.google.com/app/apikey)
3. Ensure no extra spaces in the `.env` file

### Token Limit Exceeded

If token usage exceeds 200K:
1. The system automatically prioritizes core files
2. Consider excluding unnecessary files
3. Split large projects into smaller workspaces

### Port Already in Use

If port 9000 is busy:
1. Change `PORT` in `.env`
2. Or kill the process using the port:
   ```bash
   # Windows
   netstat -ano | findstr :9000
   taskkill /PID <PID> /F
   ```

## Security Considerations

- Never commit `.env` files to version control
- API keys are loaded from environment variables only
- File uploads are scanned for exclusions
- Code execution uses safe mock timeout
- No permanent code execution in production

## Performance

- Async/await throughout for non-blocking operations
- Token counting optimized with tiktoken
- File prioritization reduces context size
- Static files served efficiently
- Response caching where appropriate

## License

MIT License - See LICENSE file for details

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Submit a pull request

## Support

For issues and questions:
- Check the troubleshooting section
- Review test files for usage examples
- Open an issue on GitHub

## Acknowledgments

- Google AI for Gemini Flash API
- OpenAI for tiktoken library
- FastAPI for the web framework
- The open-source community
