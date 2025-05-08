import sys
sys.dont_write_bytecode = True
from fastapi import FastAPI
import logging
from app.routes import session, actions

# Setup logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Playwright Action API")

# Add root route
@app.get("/")
async def root():
    return {
        "message": "Welcome to Playwright Action API",
        "endpoints": {
            "session": {
                "start": "/session/start",
                "close": "/session/close"
            },
            "actions": {
                "click": "/action/click",
                "fill": "/action/fill",
                "hover": "/action/hover",
                "navigate": "/action/navigate"
            }
        }
    }

# Include routers
app.include_router(session.router, prefix="/session", tags=["session"])
app.include_router(actions.router, prefix="/action", tags=["actions"])
