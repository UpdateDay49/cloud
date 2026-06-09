from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from playwright.async_api import async_playwright
import base64

app = FastAPI(title="Cloud Browser Proxy")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/render")
async def render_page(url: str):
    """
    Navigates to the provided URL using Playwright and returns a base64 encoded screenshot.
    """
    if not url.startswith("http"):
        url = "https://" + url

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(
                headless=True,
                args=["--no-sandbox", "--disable-setuid-sandbox", "--disable-dev-shm-usage"]
            )
            
            context = await browser.new_context(
                viewport={"width": 1920, "height": 1080},
                user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            )
            
            page = await context.new_page()
            
            await page.goto(url, wait_until="networkidle", timeout=15000)
            
            screenshot_bytes = await page.screenshot(full_page=True, type="jpeg", quality=80)
            await browser.close()
            
            encoded_image = base64.b64encode(screenshot_bytes).decode('utf-8')
            
            return {"status": "success", "url": url, "data": encoded_image}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
