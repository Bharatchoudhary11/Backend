import base64
from fastapi import HTTPException
from playwright.async_api import Page
import logging

logger = logging.getLogger(__name__)

async def get_locator(page: Page, locator_data):
    if isinstance(locator_data, str):
        logger.debug(f"Using string locator: {locator_data}")
        return page.locator(locator_data)
    elif isinstance(locator_data, dict):
        logger.debug(f"Using role locator: {locator_data}")
        return page.get_by_role(locator_data["role"], name=locator_data["name"])
    else:
        raise HTTPException(status_code=400, detail="Invalid locator format")

async def take_screenshot(page: Page):
    screenshot = await page.screenshot()
    return base64.b64encode(screenshot).decode()