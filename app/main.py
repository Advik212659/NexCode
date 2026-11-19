from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from app.routers import mode, notebook, llm, seo
from app.config import get_settings
import os

settings = get_settings()

app = FastAPI(
    title="NexCode - Autonomous AI Coding Assistant",
    description="Production-grade AI coding assistant with File Mode and Code Mode",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(mode.router, prefix="/api/mode", tags=["mode"])
app.include_router(notebook.router, prefix="/api/notebook", tags=["notebook"])
app.include_router(llm.router, prefix="/api/llm", tags=["llm"])
app.include_router(seo.router, tags=["seo"])

static_dir = os.path.join(os.path.dirname(__file__), "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    from fastapi.templating import Jinja2Templates
    templates = Jinja2Templates(directory="app/templates")
    return templates.TemplateResponse("index.html", {
        "request": request,
        "google_site_verification": settings.google_site_verification
    })


@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "NexCode"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=settings.port, reload=True)
