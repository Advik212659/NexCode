# NexCode - Agent Documentation

## Project Overview

NexCode is a production-grade AI coding assistant built with FastAPI (Python) and vanilla HTML/CSS/JavaScript. It features dual execution modes (File Mode and Code Mode) and uses Google Gemini Flash as the primary AI provider.

## Build & Verification Commands

### Install Dependencies
```bash
pip install -r requirements.txt
```

### Run Application
```bash
python -m app.main
# Or
uvicorn app.main:app --host 0.0.0.0 --port 9000 --reload
```

### Run Tests
```bash
pytest -v
```

### Run Specific Test Files
```bash
pytest tests/test_mode_endpoints.py -v
pytest tests/test_notebook_history.py -v
pytest tests/test_token_limiter.py -v
pytest tests/test_gsc_routes.py -v
```

## Configuration

Required environment variables in `.env`:
- `GEMINI_API_KEY` - Google Gemini API key (required)
- `OPENROUTER_API_KEY` - OpenRouter API key (optional fallback)
- `MAX_CONTEXT_TOKENS` - Default: 200000
- `PORT` - Default: 9000
- `GOOGLE_SITE_VERIFICATION` - Optional for Google Search Console

## Key Features

1. **Dual Mode System**: File Mode (repo analysis) and Code Mode (snippet helper)
2. **200K Context Window**: Token counting with live meter and automatic prioritization
3. **Notebook System**: Persistent session history with CRUD operations
4. **Collapsible Sidebar**: History management with toggle functionality
5. **SEO Ready**: robots.txt, sitemap.xml, and metadata
6. **Zero-Cost AI**: Gemini Flash free tier with OpenRouter fallback

## Architecture

- **Backend**: FastAPI with async/await
- **Frontend**: Pure HTML5/CSS3/JavaScript (no frameworks)
- **AI Provider**: Google Gemini Flash (primary) + OpenRouter (fallback)
- **Token Counter**: tiktoken with cl100k_base encoding
- **Storage**: JSON file for notebook persistence

## File Structure

```
app/
├── main.py              # FastAPI app with routers
├── config.py            # Settings management
├── models/schemas.py    # Pydantic models
├── routers/
│   ├── mode.py          # Mode switching
│   ├── notebook.py     # Notebook CRUD
│   ├── llm.py           # Chat endpoints
│   └── seo.py           # SEO routes
├── services/
│   ├── llm.py           # AI provider
│   └── token_counter.py # Token management
├── static/app.js        # Frontend JS
└── templates/index.html # Main HTML
```

## Testing Coverage

- `test_mode_endpoints.py`: Mode switching and session management
- `test_notebook_history.py`: Notebook CRUD operations
- `test_token_limiter.py`: Token counting and limits
- `test_gsc_routes.py`: SEO routes and metadata

All tests should pass with `pytest -v`.

## Important Notes

- The application uses a 200K token limit (user-facing) even though Gemini supports 1M
- File uploads automatically exclude `.git`, `node_modules`, `venv`, `__pycache__`
- Notebook history is stored in `notebook_history.json` (gitignored)
- Static files are served from `app/static/`
- The UI is fully responsive and dark-themed

## Dependencies

Key packages:
- fastapi==0.115.0
- uvicorn[standard]==0.32.0
- httpx==0.27.2
- google-genai==1.7.0
- tiktoken==0.8.0
- python-dotenv==1.0.1
- pydantic==2.9.2
- pytest==8.3.3
