from fastapi import APIRouter, HTTPException
from playwright.async_api import async_playwright
import uuid
import logging
from ..models.session import SessionConfig, SessionId
from ..utils.helpers import take_screenshot

router = APIRouter()
logger = logging.getLogger(__name__)

# Store active sessions
active_sessions = {}

@router.post("/start")
async def start_session(config: SessionConfig):
    session_id = str(uuid.uuid4())
    try:
        playwright = await async_playwright().start()
        browser_type = config.browser.lower()
        
        if browser_type not in ["chromium", "firefox", "webkit"]:
            raise HTTPException(status_code=400, detail="Invalid browser type")
            
        browser = await getattr(playwright, browser_type).launch(headless=config.headless)
        context = await browser.new_context()
        page = await context.new_page()
        
        active_sessions[session_id] = {
            "playwright": playwright,
            "browser": browser,
            "context": context,
            "page": page
        }
        
        logger.info(f"Started session: {session_id} with {browser_type}")
        return {"sessionId": session_id}
    except Exception as e:
        logger.error(f"Error starting session: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/close")
async def close_session(session: SessionId):
    if session.sessionId not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        session_data = active_sessions[session.sessionId]
        await session_data["page"].close()
        await session_data["context"].close()
        await session_data["browser"].close()
        await session_data["playwright"].stop()
        del active_sessions[session.sessionId]
        
        logger.info(f"Closed session: {session.sessionId}")
        return {"status": "success"}
    except Exception as e:
        logger.error(f"Error closing session {session.sessionId}: {e}")
        raise HTTPException(status_code=500, detail=str(e))