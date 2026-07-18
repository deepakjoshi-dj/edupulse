"""Capture full-page screenshots of every dashboard page via headless Chromium.

Usage (from project root, with venv activated):
    1) In one terminal:   streamlit run Home.py --server.headless true
    2) Wait until the app prints "You can now view your Streamlit app"
    3) In another terminal:   python scripts/capture_screenshots.py

Output: assets/screenshots/screenshot_5_1_home.png … screenshot_5_6_insights.png
"""

from __future__ import annotations

import asyncio
import time
from pathlib import Path

from playwright.async_api import async_playwright

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "screenshots"
OUT.mkdir(parents=True, exist_ok=True)

BASE = "http://localhost:8501"

PAGES = [
    ("screenshot_5_1_home.png",                f"{BASE}/"),
    ("screenshot_5_2_overview.png",            f"{BASE}/Overview"),
    ("screenshot_5_3_course_analytics.png",    f"{BASE}/Course_Analytics"),
    ("screenshot_5_4_engagement_patterns.png", f"{BASE}/Engagement_Patterns"),
    ("screenshot_5_5_dropout_prediction.png",  f"{BASE}/Dropout_Prediction"),
    ("screenshot_5_6_insights.png",            f"{BASE}/Insights"),
]


async def main() -> None:
    async with async_playwright() as p:
        browser = await p.chromium.launch()
        ctx = await browser.new_context(
            viewport={"width": 1440, "height": 900},
            device_scale_factor=2,           # retina-quality PNG
        )
        page = await ctx.new_page()

        for name, url in PAGES:
            print(f"→ {url}")
            try:
                await page.goto(url, wait_until="networkidle", timeout=60_000)
            except Exception as e:
                print(f"   first nav failed ({e}); retrying with domcontentloaded")
                await page.goto(url, wait_until="domcontentloaded", timeout=60_000)
            # Streamlit charts hydrate after first paint — give them a moment
            await page.wait_for_timeout(4500)
            out_path = OUT / name
            await page.screenshot(path=str(out_path), full_page=True)
            print(f"   wrote {out_path.relative_to(ROOT)}")

        await browser.close()


if __name__ == "__main__":
    asyncio.run(main())
