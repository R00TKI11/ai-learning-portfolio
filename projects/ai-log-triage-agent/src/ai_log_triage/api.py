"""
FastAPI Application for AI Log Triage Agent

This module provides a REST API for log analysis and triage using LLMs.

SPDX-License-Identifier: MIT
Copyright (c) 2025 R00TKI11
"""

from typing import List, Optional, Dict
from enum import Enum

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator

from .log_parser import LogParser, LogEvent
from .triage_agent import TriageAgent, Priority
from .__init__ import __version__


# Pydantic Models for API
class ChunkMethod(str, Enum):
    """Log chunking methods."""
    EVENT = "event"
    LINE = "line"


class TriageRequestSingle(BaseModel):
    """Request model for triaging a single log entry."""
    log_text: str = Field(
        ...,
        description="Raw log text to analyze",
        examples=["2025-02-17 14:23:11 ERROR: Database connection failed"]
    )
    source_file: Optional[str] = Field(
        None,
        description="Optional source filename for context",
        examples=["webserver_error.log"]
    )
    chunk_method: ChunkMethod = Field(
        ChunkMethod.EVENT,
        description="How to chunk the log text (event or line)"
    )
    max_tokens: int = Field(
        1024,
        ge=100,
        le=4096,
        description="Maximum tokens for LLM response"
    )
    model: Optional[str] = Field(
        None,
        description="LLM model to use (overrides default)"
    )

    @field_validator('log_text')
    @classmethod
    def validate_log_text(cls, v: str) -> str:
        if not v or not v.strip():
            raise ValueError("log_text cannot be empty")
        if len(v) > 100000:  # 100KB limit
            raise ValueError("log_text exceeds maximum size of 100KB")
        return v


class TriageRequestBatch(BaseModel):
    """Request model for triaging multiple log entries."""
    logs: List[str] = Field(
        ...,
        description="List of raw log texts to analyze",
        min_length=1,
        max_length=100
    )
    source_file: Optional[str] = Field(
        None,
        description="Optional source filename for context"
    )
    max_tokens: int = Field(
        1024,
        ge=100,
        le=4096,
        description="Maximum tokens per LLM response"
    )
    model: Optional[str] = Field(
        None,
        description="LLM model to use (overrides default)"
    )


class TriageResponse(BaseModel):
    """Response model for triage results."""
    source_file: Optional[str]
    line_number: int
    timestamp: Optional[str]
    log_level: Optional[str]
    summary: str
    classification: str
    priority: str
    suggested_owner: str
    root_cause: str
    action_items: List[str]
    original_log: str


class BatchTriageResponse(BaseModel):
    """Response model for batch triage results."""
    total_events: int
    results: List[TriageResponse]
    priority_breakdown: Dict[str, int]


class ErrorResponse(BaseModel):
    """Error response model."""
    detail: str
    error_type: str


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    version: str
    llm_configured: bool


# FastAPI Application
app = FastAPI(
    title="AI Log Triage Agent API",
    description="REST API for intelligent log analysis and triage using LLMs",
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# CORS middleware for web client access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize components
log_parser = LogParser()


# Exception Handlers
@app.exception_handler(ValueError)
async def value_error_handler(_request, exc):
    """Handle validation errors."""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=ErrorResponse(
            detail=str(exc),
            error_type="ValidationError"
        ).model_dump()
    )


@app.exception_handler(RuntimeError)
async def runtime_error_handler(_request, exc):
    """Handle runtime errors (e.g., LLM API failures)."""
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=ErrorResponse(
            detail=str(exc),
            error_type="RuntimeError"
        ).model_dump()
    )


# API Endpoints
@app.get(
    "/health",
    response_model=HealthResponse,
    tags=["System"],
    summary="Health check endpoint"
)
async def health_check():
    """
    Check if the API is running and properly configured.

    Returns basic system information and configuration status.
    """
    from .config import settings

    return HealthResponse(
        status="healthy",
        version=__version__,
        llm_configured=bool(settings.LLM_OPENROUTER_API_KEY and settings.LLM_ENDPOINT)
    )


@app.post(
    "/triage",
    response_model=TriageResponse,
    tags=["Triage"],
    summary="Triage a single log entry",
    status_code=status.HTTP_200_OK
)
async def triage_single_log(request: TriageRequestSingle):
    """
    Analyze and triage a single log entry.

    This endpoint:
    - Parses the log text using the specified chunking method
    - Analyzes it with an LLM
    - Returns structured triage information including:
      - Summary of the issue
      - Classification (e.g., "Database Error", "Auth Failure")
      - Priority level (CRITICAL, HIGH, MEDIUM, LOW, INFO)
      - Suggested owner/team
      - Root cause analysis
      - Actionable items for resolution

    **Example Request:**
    ```json
    {
      "log_text": "2025-02-17 14:23:11 ERROR: Database connection timeout",
      "source_file": "webserver.log",
      "chunk_method": "event"
    }
    ```
    """
    try:
        # Parse log text
        lines = request.log_text.split('\n')

        if request.chunk_method == ChunkMethod.EVENT:
            events = list(log_parser.chunk_by_event(lines, request.source_file))
        else:
            events = list(log_parser.chunk_by_line(lines, request.source_file))

        if not events:
            raise ValueError("No valid log events found in the provided text")

        # Triage the first event (or combine if multiple)
        event = events[0]

        # Initialize agent with optional model override
        agent = TriageAgent(model=request.model)
        result = agent.triage_event(event, max_tokens=request.max_tokens)

        # Convert to response model
        return TriageResponse(**result.to_dict())

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM processing error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@app.post(
    "/triage/batch",
    response_model=BatchTriageResponse,
    tags=["Triage"],
    summary="Triage multiple log entries",
    status_code=status.HTTP_200_OK
)
async def triage_batch_logs(request: TriageRequestBatch):
    """
    Analyze and triage multiple log entries in a single request.

    This endpoint processes multiple log entries and returns:
    - Individual triage results for each entry
    - Total event count
    - Priority breakdown across all events

    **Example Request:**
    ```json
    {
      "logs": [
        "2025-02-17 14:23:11 ERROR: Database timeout",
        "2025-02-17 14:24:15 WARN: High memory usage"
      ],
      "source_file": "app.log"
    }
    ```
    """
    try:
        # Create LogEvents from raw log texts
        events = []
        for i, log_text in enumerate(request.logs, start=1):
            if not log_text.strip():
                continue

            event = LogEvent(
                raw_content=log_text.strip(),
                line_number=i,
                timestamp=log_parser.extract_timestamp(log_text),
                log_level=log_parser.extract_log_level(log_text),
                source_file=request.source_file or f"batch_request_{i}.log",
                category=log_parser.detect_category(request.source_file) if request.source_file else "general"
            )
            events.append(event)

        if not events:
            raise ValueError("No valid log events found in the batch")

        # Triage all events
        agent = TriageAgent(model=request.model)
        results = agent.triage_batch(events, max_tokens=request.max_tokens)

        # Calculate priority breakdown
        priority_breakdown = {p.value: 0 for p in Priority}
        for result in results:
            priority_breakdown[result.priority.value] += 1

        # Convert to response models
        response_results = [TriageResponse(**r.to_dict()) for r in results]

        return BatchTriageResponse(
            total_events=len(results),
            results=response_results,
            priority_breakdown=priority_breakdown
        )

    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=str(e)
        )
    except RuntimeError as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LLM processing error: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Unexpected error: {str(e)}"
        )


@app.get(
    "/",
    tags=["System"],
    summary="API information"
)
async def root():
    """
    Get basic API information.

    Returns links to documentation and version info.
    """
    return {
        "name": "AI Log Triage Agent API",
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
        "health": "/health",
        "endpoints": {
            "triage_single": "POST /triage",
            "triage_batch": "POST /triage/batch"
        }
    }


# For development/testing
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
