from fastapi import APIRouter, HTTPException
import asyncio
import logging
from ..models.session import ActionRequest, NavigateRequest
from ..utils.helpers import get_locator, take_screenshot
from .session import active_sessions

router = APIRouter()
logger = logging.getLogger("playwright")

ACTION_TIMEOUT = 10

@router.post("/click")
async def click(action: ActionRequest):
    if action.sessionId not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")

    try:
        page = active_sessions[action.sessionId]["page"]
        current_url = page.url
        logger.info(f"Current page URL: {current_url}")
        
        # Enhanced waiting strategy
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        try:
            if isinstance(action.locator, dict):
                # Try multiple role-based strategies
                role = action.locator.get("role", "")
                name = action.locator.get("name", "")
                
                # Try different combinations
                try_locators = [
                    page.get_by_role(role, name=name),  # Exact match
                    page.get_by_role(role, name=name, exact=True),  # Strict match
                    page.locator(f"[role='{role}']:has-text('{name}')"),  # CSS + text
                    page.locator(f"button:has-text('{name}')"),  # Button with text
                    page.locator(f"input[type='submit'][value='{name}']"),  # Submit input
                ]
                
                for locator in try_locators:
                    try:
                        if await locator.count() > 0:
                            await locator.wait_for(state="visible", timeout=5000)
                            if await locator.is_visible() and await locator.is_enabled():
                                await locator.scroll_into_view_if_needed()
                                await page.wait_for_timeout(1000)
                                
                                # Try clicking with multiple strategies
                                try:
                                    await locator.click(timeout=5000)
                                except:
                                    try:
                                        await locator.click(force=True)
                                    except:
                                        element = await locator.element_handle()
                                        await page.evaluate("el => el.click()", element)
                                
                                await page.wait_for_load_state("networkidle")
                                screenshot = await take_screenshot(page)
                                return {"status": "success", "screenshot": screenshot}
                    except Exception:
                        continue
            
            elif isinstance(action.locator, str):
                # Try multiple selector strategies
                selectors = [
                    action.locator,
                    f"button:has-text('{action.locator}')",
                    f"input[type='submit'][value='{action.locator}']",
                    f"a:has-text('{action.locator}')",
                    f"[role='button']:has-text('{action.locator}')",
                    f"div:has-text('{action.locator}')",
                    f"span:has-text('{action.locator}')"
                ]
                
                for selector in selectors:
                    try:
                        locator = page.locator(selector)
                        if await locator.count() > 0:
                            await locator.wait_for(state="visible", timeout=5000)
                            if await locator.is_visible() and await locator.is_enabled():
                                await locator.scroll_into_view_if_needed()
                                await page.wait_for_timeout(1000)
                                
                                # Try clicking with multiple strategies
                                try:
                                    await locator.click(timeout=5000)
                                except:
                                    try:
                                        await locator.click(force=True)
                                    except:
                                        element = await locator.element_handle()
                                        await page.evaluate("el => el.click()", element)
                                
                                await page.wait_for_load_state("networkidle")
                                screenshot = await take_screenshot(page)
                                return {"status": "success", "screenshot": screenshot}
                    except Exception as selector_error:
                        logger.warning(f"Selector {selector} failed: {str(selector_error)}")
                        continue
            
            else:
                # Handle role-based locator
                locator = await get_locator(page, action.locator)
                await locator.wait_for(state="visible", timeout=5000)
                await locator.scroll_into_view_if_needed()
                await locator.click(force=True)
                await page.wait_for_load_state("networkidle")
                screenshot = await take_screenshot(page)
                return {"status": "success", "screenshot": screenshot}
                
        except Exception as click_error:
            logger.error(f"Click operation failed: {str(click_error)}")
            return {
                "status": "error",
                "error": "Click operation failed",
                "details": f"Failed to click element: {str(click_error)}. URL: {current_url}"
            }
        
        return {
            "status": "error",
            "error": "Element not found",
            "details": f"No clickable elements found matching the criteria. URL: {current_url}"
        }

    except Exception as e:
        logger.error(f"Click handler failed: {str(e)}")
        return {"status": "error", "error": str(e)}

@router.post("/fill")
async def fill(action: ActionRequest):
    if action.sessionId not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    if not action.value:
        raise HTTPException(status_code=400, detail="Missing value to fill")

    try:
        page = active_sessions[action.sessionId]["page"]
        locator = await get_locator(page, action.locator)
        
        # Wait for network and element
        await page.wait_for_load_state("networkidle")
        
        try:
            await locator.wait_for(state="visible", timeout=10000)
            await locator.scroll_into_view_if_needed()
        except Exception as wait_error:
            return {
                "status": "error",
                "error": "Element not visible or not found",
                "details": str(wait_error)
            }

        # Clear existing value first
        await locator.clear()
        await page.wait_for_timeout(500)
        
        # Fill the value
        await locator.fill(action.value)
        await page.wait_for_timeout(500)
        
        screenshot = await take_screenshot(page)
        return {"status": "success", "screenshot": screenshot}
    except Exception as e:
        return {"status": "error", "error": str(e)}

@router.post("/hover")
async def hover(action: ActionRequest):
    if action.sessionId not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        page = active_sessions[action.sessionId]["page"]
        current_url = page.url
        logger.info(f"Current page URL: {current_url}")
        
        # Enhanced waiting strategy
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)
        
        try:
            if isinstance(action.locator, dict):
                # Try multiple role-based strategies
                role = action.locator.get("role", "")
                name = action.locator.get("name", "")
                
                # Try different combinations
                try_locators = [
                    page.get_by_role(role, name=name),  # Exact match
                    page.get_by_role(role, name=name, exact=True),  # Strict match
                    page.locator(f"[role='{role}']:has-text('{name}')"),  # CSS + text
                    page.locator(f"a:has-text('{name}')"),  # Link with text
                    page.locator(f"[href]:has-text('{name}')"),  # Any element with href
                ]
                
                for locator in try_locators:
                    try:
                        if await locator.count() > 0:
                            await locator.wait_for(state="visible", timeout=5000)
                            if await locator.is_visible():
                                await locator.scroll_into_view_if_needed()
                                await page.wait_for_timeout(1000)
                                
                                # Try hovering with multiple strategies
                                try:
                                    await locator.hover(timeout=5000)
                                except:
                                    # If normal hover fails, try JavaScript hover
                                    element = await locator.element_handle()
                                    await page.evaluate("""(el) => {
                                        const event = new MouseEvent('mouseover', {
                                            'view': window,
                                            'bubbles': true,
                                            'cancelable': true
                                        });
                                        el.dispatchEvent(event);
                                    }""", element)
                                
                                await page.wait_for_timeout(1000)  # Wait for hover effects
                                screenshot = await take_screenshot(page)
                                return {"status": "success", "screenshot": screenshot}
                    except Exception:
                        continue
            
            elif isinstance(action.locator, str):
                # Try multiple selector strategies
                selectors = [
                    action.locator,
                    f"a:has-text('{action.locator}')",
                    f"[role='link']:has-text('{action.locator}')",
                    f"[href]:has-text('{action.locator}')",
                    f"div:has-text('{action.locator}')",
                    f"span:has-text('{action.locator}')"
                ]
                
                for selector in selectors:
                    try:
                        locator = page.locator(selector)
                        if await locator.count() > 0:
                            await locator.wait_for(state="visible", timeout=5000)
                            if await locator.is_visible():
                                await locator.scroll_into_view_if_needed()
                                await page.wait_for_timeout(1000)
                                await locator.hover(timeout=5000)
                                await page.wait_for_timeout(1000)
                                screenshot = await take_screenshot(page)
                                return {"status": "success", "screenshot": screenshot}
                    except Exception as selector_error:
                        logger.warning(f"Selector {selector} failed: {str(selector_error)}")
                        continue
            
            return {
                "status": "error",
                "error": "Element not found",
                "details": f"No hoverable elements found matching the criteria. URL: {current_url}"
            }
                
        except Exception as hover_error:
            logger.error(f"Hover operation failed: {str(hover_error)}")
            return {
                "status": "error",
                "error": "Hover operation failed",
                "details": f"Failed to hover element: {str(hover_error)}. URL: {current_url}"
            }

    except Exception as e:
        logger.error(f"Hover handler failed: {str(e)}")
        return {"status": "error", "error": str(e)}

@router.post("/navigate")
async def navigate(request: NavigateRequest):
    if request.sessionId not in active_sessions:
        raise HTTPException(status_code=404, detail="Session not found")
    
    try:
        page = active_sessions[request.sessionId]["page"]
        await page.goto(request.url, wait_until="networkidle", timeout=30000)
        await page.wait_for_load_state("networkidle")
        await page.wait_for_timeout(2000)  # Additional wait for dynamic content
        
        screenshot = await take_screenshot(page)
        return {"status": "success", "screenshot": screenshot}
    except Exception as e:
        logger.error(f"Navigation error: {e}")
        return {"status": "error", "error": str(e)}