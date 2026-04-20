import json
import asyncio
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from sse_starlette.sse import EventSourceResponse
from scraper import search_leads_stream
from sheets_exporter import export_to_sheets
import os

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/api/scrape/stream")
def scrape_stream(request: Request, query: str, max_results: int, sheet_name: str, country: str = ""):
    max_results = min(max_results, 100) # Safety cap
    
    async def event_generator():
        try:
            yield {"data": json.dumps({"type": "log", "message": "Initializing live scraping engine..."})}
            await asyncio.sleep(0.1)
            
            # Since DDGS is synchronous, we run it in a thread to not block the main loop
            # But EventSourceResponse expects an async generator. 
            # The simple workaround: we process the sync generator directly.
            
            final_leads = []
            
            for event in search_leads_stream(query, max_results, country):
                # If client disconnected
                if await request.is_disconnected():
                    break
                    
                # Store the final leads if finished
                if event.get("type") == "done":
                    final_leads = event.get("results", [])
                    yield {"data": json.dumps({"type": "log", "message": f"Successfully scraped {len(final_leads)} leads."})}
                    break
                    
                yield {"data": json.dumps(event)}
                await asyncio.sleep(0.01)
                
            # Phase 2: Export
            yield {"data": json.dumps({"type": "log", "message": f"Exporting {len(final_leads)} leads to Google Sheet: {sheet_name}..."})}
            
            if final_leads:
                # To prevent blocking the async loop, push sheets stuff to a thread
                success = await asyncio.to_thread(export_to_sheets, final_leads, sheet_name, 'credentials.json')
                if success:
                    yield {"data": json.dumps({"type": "log", "message": "Successfully exported data to Google Sheets!"})}
                else:
                    yield {"data": json.dumps({"type": "log", "message": "Error exporting data. Check formatting and permissions."})}
            else:
                yield {"data": json.dumps({"type": "log", "message": "No leads found. Skipping export."})}
                
            yield {"data": json.dumps({"type": "complete"})}
            
        except Exception as e:
            yield {"data": json.dumps({"type": "error", "message": str(e)})}
            
    return EventSourceResponse(event_generator())

