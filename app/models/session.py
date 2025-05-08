from pydantic import BaseModel
from typing import Optional, Dict, Union

class SessionConfig(BaseModel):
    browser: str
    headless: bool = True

class SessionId(BaseModel):
    sessionId: str

class ActionRequest(BaseModel):
    sessionId: str
    locator: Union[str, Dict[str, str]]
    value: Optional[str] = None

class ActionResponse(BaseModel):
    status: str
    screenshot: Optional[str] = None
    error: Optional[str] = None

class NavigateRequest(BaseModel):
    url: str
    sessionId: str