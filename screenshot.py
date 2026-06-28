#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
html-screenshot-skill - Universal HTML Screenshot Script
This script handles the playwright installation check, headless rendering,
selector fallback, and saves individual PNGs of elements matching selectors.
"""

import os
import sys
import json
import argparse
import pathlib
import asyncio
import subprocess
import datetime

def ensure_playwright_installed():
    """
    Checks if playwright is installed. If not, exits with a clear instruction
    for the user or agent to install it.
    """
    try:
        import playwright
    except ImportError:
        print("[ERROR] Dependency missing: 'playwright' library is not installed.", file=sys.stderr)
        print("Please install dependencies by running the following command first:", file=sys.stderr)
        print("  pip install playwright && python -m playwright install chromium", file=sys.stderr)
        sys.exit(1)

async def launch_browser(p):
    """
    Launches browser with high compatibility args.
    """
    compat_args = [
        "--no-sandbox",
        "--disable-setuid-sandbox",
        "--disable-dev-shm-usage",
        "--use-angle=swiftshader",
        "--enable-unsafe-swiftshader",
    ]
    
    try:
        browser = await p.chromium.launch(args=compat_args)
        return browser
    except Exception as e:
        err_msg = str(e)
        if "Executable doesn't exist" in err_msg or "playwright install" in err_msg:
            print("[ERROR] Chromium browser binary not found.", file=sys.stderr)
            print("Please download the Chromium browser binary by running:", file=sys.stderr)
            print("  python -m playwright install chromium", file=sys.stderr)
            sys.exit(1)
        else:
            print(f"Error: Playwright failed to launch Chromium: {e}", file=sys.stderr)
            sys.exit(1)

def resolve_output_dir(html_path, requested_dir):
    """
    Resolves the output directory based on argument, environment variables, or default fallback.
    """
    if requested_dir:
        out_path = pathlib.Path(requested_dir)
    elif os.environ.get("AGENT_OUTPUT_DIR"):
        out_path = pathlib.Path(os.environ.get("AGENT_OUTPUT_DIR"))
    elif pathlib.Path("/mnt/user-data/outputs").exists() and os.access("/mnt/user-data/outputs", os.W_OK):
        # Fallback for specific agent sandbox environments where output collection is mounted
        out_path = pathlib.Path("/mnt/user-data/outputs")
    else:
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        out_path = pathlib.Path(html_path).parent / f"screenshots-{timestamp}"
        
    out_path.mkdir(parents=True, exist_ok=True)
    return out_path.resolve()

async def main_async(args):
    from playwright.async_api import async_playwright
    
    html_path = pathlib.Path(args.html).expanduser().resolve()
    if not html_path.exists():
        print(f"Warning: HTML file '{args.html}' not found at {html_path}", file=sys.stderr)
        # Fallback: search current directory for any html file
        candidates = list(pathlib.Path(".").glob("*.html"))
        if candidates:
            html_path = candidates[0].resolve()
            print(f"Using alternative HTML file found in current directory: {html_path}", file=sys.stderr)
        else:
            print("Error: No HTML file found.", file=sys.stderr)
            sys.exit(1)
            
    out_dir = resolve_output_dir(html_path, args.output_dir)
    
    # Split comma-separated selector candidates
    selectors = [s.strip() for s in args.selector.split(",") if s.strip()]
    if not selectors:
        selectors = ["section.poster", ".poster", "div.card", ".card", "body"]
        
    async with async_playwright() as p:
        browser = await launch_browser(p)
        
        # Create context with DPI scale and large viewport
        context = await browser.new_context(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=args.scale
        )
        
        page = await context.new_page()
        file_url = html_path.as_uri()
        
        try:
            await page.goto(file_url, wait_until="networkidle")
        except Exception as e:
            # Fallback to load state if networkidle fails/timeouts on sandboxed offline environments
            print(f"Warning: goto networkidle failed: {e}. Trying to wait for load state...", file=sys.stderr)
            await page.goto(file_url, wait_until="load")
            
        # Extra wait for webfonts, custom background WebGL animations, etc.
        await page.wait_for_timeout(args.delay)
        
        # Query elements using selectors list with fallback
        elements = []
        chosen_selector = None
        for sel in selectors:
            elements = await page.query_selector_all(sel)
            if elements:
                chosen_selector = sel
                break
                
        if not elements:
            print(f"Warning: None of the selectors {selectors} matched. Screenshotting entire body.", file=sys.stderr)
            body_el = await page.query_selector("body")
            elements = [body_el] if body_el else []
            chosen_selector = "body"
            
        if not elements:
            print("Error: Could not find any element to screenshot (even <body> is missing).", file=sys.stderr)
            await browser.close()
            sys.exit(1)
            
        saved_files = []
        for i, el in enumerate(elements, start=1):
            if chosen_selector == "body":
                file_name = "page.png"
            else:
                file_name = f"card-{i:02d}.png"
                
            out_path = out_dir / file_name
            
            # Capture bounding box dimensions for logging
            bb = await el.bounding_box()
            w = round(bb["width"] * args.scale) if bb else "?"
            h = round(bb["height"] * args.scale) if bb else "?"
            
            await el.screenshot(path=str(out_path))
            saved_files.append(str(out_path.resolve()))
            print(f"Saved: {file_name} ({w}x{h}px) -> {out_path}")
            
        await browser.close()
        return {
            "success": True,
            "output_dir": str(out_dir),
            "files": saved_files,
            "count": len(saved_files)
        }

if __name__ == "__main__":
    ensure_playwright_installed()
    
    parser = argparse.ArgumentParser(description="Universal HTML Poster Screen Shooter")
    parser.add_argument("--html", required=True, help="Path to the target HTML file")
    parser.add_argument("--output-dir", help="Directory to save PNGs (defaults to environment-appropriate folder)")
    parser.add_argument("--selector", default="section.poster,.poster,div.card,.card,section,body", help="CSS selector(s) of target elements to screenshot, comma-separated in order of preference")
    parser.add_argument("--scale", type=float, default=1.0, help="Device scale factor (DPI / resolution scaling)")
    parser.add_argument("--delay", type=int, default=1500, help="Wait time in ms for fonts/animations to load")
    parser.add_argument("--width", type=int, default=2400, help="Viewport width")
    parser.add_argument("--height", type=int, default=2000, help="Viewport height")
    parser.add_argument("-y", "--yes", action="store_true", help="Automatic yes to prompts; assume 'yes' as answer to all prompts and run non-interactively")
    
    args = parser.parse_args()
    
    try:
        result = asyncio.run(main_async(args))
        # Print JSON output on the very last line for easy programmatical parsing
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({"success": False, "error": str(e)}))
        sys.exit(1)
