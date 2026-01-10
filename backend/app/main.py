from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse, JSONResponse
from pydantic import BaseModel
from typing import Optional
import logging
from datetime import datetime
from pathlib import Path
import sys

sys.path.insert(0, str(Path(__file__).parent.parent))

from backend.app.core.config import Config
from backend.app.core.logger import setup_logger
from backend.app.services.rss_reader import RSSReader
from backend.app.services.news_crawler import NewsCrawler
from backend.app.services.ai_client import AIModelClient
from backend.app.services.html_generator import HTMLGenerator


app = FastAPI(
    title="AI News Analysis API",
    description="美國財經新聞分析與報告生成 API",
    version="1.0.0",
)

config = Config()
logger = setup_logger(config.MARKDOWN_LOG_OUTPUT_PATH, config.LOG_FILENAME)


class AnalysisRequest(BaseModel):
    topic: Optional[str] = (
        f"美國重要財經新聞分析 - {datetime.now().strftime('%Y年%m月%d日')}"
    )
    return_html: bool = False


class StatusResponse(BaseModel):
    status: str
    api_key_configured: bool
    model: str
    last_update: Optional[str]
    hostname: str


@app.get("/")
async def root():
    return {
        "message": "AI News Analysis API",
        "version": "1.0.0",
        "docs": "/docs",
        "endpoints": {
            "POST /api/analyze": "觸發新聞分析",
            "GET /api/news": "獲取新聞列表",
            "GET /api/report": "獲取 HTML 報告",
            "GET /api/status": "系統狀態",
        },
    }


@app.get("/api/status", response_model=StatusResponse)
async def get_status():
    html_path = config.HTML_OUTPUT_PATH / config.HTML_FILENAME
    last_update = None
    if html_path.exists():
        last_update = datetime.fromtimestamp(html_path.stat().st_mtime).isoformat()

    return StatusResponse(
        status="running",
        api_key_configured=bool(config.OPENROUTER_API_KEY),
        model=config.ANALYSIS_OUTPUT_MODEL,
        last_update=last_update,
        hostname=config.HOSTNAME,
    )


@app.post("/api/analyze")
async def analyze_news(request: AnalysisRequest, background_tasks: BackgroundTasks):
    def run_analysis(topic: str):
        try:
            from AI_News import AI_News_Agent

            agent = AI_News_Agent(config, logger)
            agent.run(topic)
        except Exception as e:
            logger.error(f"背景分析任務失敗: {e}", exc_info=True)

    background_tasks.add_task(run_analysis, request.topic)

    return {"message": "分析任務已啟動", "topic": request.topic, "status": "running"}


@app.get("/api/news")
async def get_news(limit: Optional[int] = 10, offset: Optional[int] = 0):
    html_path = config.HTML_OUTPUT_PATH / config.HTML_FILENAME
    if not html_path.exists():
        raise HTTPException(
            status_code=404, detail="尚未生成報告，請先執行 /api/analyze"
        )

    from backend.app.services.html_generator import HTMLGenerator
    import re
    import markdown

    html_content = html_path.read_text(encoding="utf-8")

    return {
        "total": 0,
        "limit": limit,
        "offset": offset,
        "message": "請使用 /api/report 查看完整 HTML 報告",
    }


@app.get("/api/report", response_class=HTMLResponse)
async def get_report():
    html_path = config.HTML_OUTPUT_PATH / config.HTML_FILENAME
    if not html_path.exists():
        raise HTTPException(
            status_code=404, detail="尚未生成報告，請先執行 /api/analyze"
        )

    html_content = html_path.read_text(encoding="utf-8")
    return HTMLResponse(content=html_content)


@app.get("/api/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("backend.app.main:app", host="0.0.0.0", port=8000, reload=True)
