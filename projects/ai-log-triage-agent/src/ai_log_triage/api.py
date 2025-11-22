from fastapi import FastAPI
from pydantic import BaseModel
from .log_parser import LogEvent
from .triage_agent import TriageAgent

app = FastAPI()
agent = TriageAgent()

class TriageRequest(BaseModel):
    log_text: str

@app.post("/triage")
async def triage_log(request: TriageRequest):
    # For now, wrap the raw log text as a single LogEvent
    event = LogEvent(
        raw_content=request.log_text,
        line_number=1,
        timestamp=None,
        log_level=None,
        source_file="api_request.log",
    )
    results = agent.triage_batch([event])
    return [r.to_dict() for r in results]

@app.get("/health")
async def health():
    return {"status": "ok"}

