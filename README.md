Objective
Build a REST API service that exposes Playwright browser automation actions (e.g., click, hover, fill, etc.) as real-time HTTP endpoints. The system must support multiple browser sessions and return a screenshot after each action.

Tech Stack
You may use either of the following stacks:

Python with FastAPI
JavaScript with Express.js
All automation must use Playwright.

Core Requirements
1. Session Management
Support multiple browser sessions via a sessionId. Each action must operate within its own session context.

POST /session/start
Start a new browser session.

Sample Request:

{
  "browser": "chromium",
  "headless": true,
}
Sample Response:

{
  "sessionId": "abc123"
}
POST /session/close
Close an active session.

Request:

{
  "sessionId": "abc123"
}
2. Action Endpoints
Expose each Playwright action as a separate endpoint. Each endpoint should:

Accept a sessionId
Accept a locator (either string or structured format)
Execute in real time
Return a base64-encoded screenshot
Refer to the full list of actions and their usage here:
📚 Playwright Input Actions Documentation

3. Locator Format
Endpoints must support both:

String selectors (e.g., "text=Submit", "#email")

Structured locators using role and name:

{
  "role": "button",
  "name": "Continue"
}
Response Format
Each action endpoint should return:

Success:

{
  "status": "success",
  "screenshot": "base64_png_data"
}
Error:

{
  "status": "error",
  "error": "Element not found: text=Login"
}
What NOT to Build
No frontend UI
No authentication or rate limiting
No saving of screenshots (return as base64 only)
