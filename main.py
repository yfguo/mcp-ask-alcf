#!/usr/bin/env python3
"""
ALCF OpenAPI Tool Server

A FastAPI-based OpenAPI server that provides access to information about ALCF systems
through the ask.alcf.anl.gov AI assistant interface.

This server exposes RESTful API endpoints that can be used by Open WebUI and other
OpenAPI-compatible clients to query ALCF resources, systems, and best practices.
"""

from typing import Optional
from enum import Enum
import asyncio
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, field_validator, ConfigDict
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Constants
CHARACTER_LIMIT = 25000
DEFAULT_TIMEOUT = 60000
ASK_ALCF_URL = "https://ask.alcf.anl.gov"


# Pydantic Models
class ResponseFormat(str, Enum):
    """Output format for responses."""
    MARKDOWN = "markdown"
    JSON = "json"


class AskQuestionRequest(BaseModel):
    """Request model for asking ALCF questions."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    question: str = Field(
        ...,
        description="Question to ask about ALCF systems, resources, or best practices",
        min_length=5,
        max_length=1000,
        examples=["What is Aurora?", "How do I compile code on Polaris?"]
    )

    timeout: Optional[int] = Field(
        default=DEFAULT_TIMEOUT,
        description="Maximum time to wait for response in milliseconds",
        ge=10000,
        le=180000
    )

    response_format: ResponseFormat = Field(
        default=ResponseFormat.MARKDOWN,
        description="Output format: 'markdown' for human-readable or 'json' for machine-readable"
    )

    @field_validator('question')
    @classmethod
    def validate_question(cls, v: str) -> str:
        """Ensure question is not empty after stripping."""
        if not v.strip():
            raise ValueError("Question cannot be empty")
        return v.strip()


class SystemInfoRequest(BaseModel):
    """Request model for system information queries."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        extra='forbid'
    )

    system_name: str = Field(
        ...,
        description="Name of the ALCF system",
        examples=["Aurora", "Polaris", "AI Testbed", "Cerebras"]
    )


class ALCFResponse(BaseModel):
    """Standard response model for ALCF queries."""
    question: str = Field(..., description="The question that was asked")
    answer: str = Field(..., description="The answer from AskALCF")
    source: str = Field(default=ASK_ALCF_URL, description="Source of the information")
    truncated: bool = Field(default=False, description="Whether the response was truncated")


class ErrorResponse(BaseModel):
    """Error response model."""
    error: bool = Field(default=True, description="Indicates an error occurred")
    message: str = Field(..., description="Error message")
    question: Optional[str] = Field(None, description="The question that caused the error")


# Core functionality
async def _query_ask_alcf(
    question: str,
    timeout: int = DEFAULT_TIMEOUT,
    headless: bool = True,
    verbose: bool = False
) -> str:
    """
    Query the ask.alcf.anl.gov service using Playwright automation.

    Args:
        question: The question to ask
        timeout: Maximum time to wait for response in milliseconds
        headless: Whether to run browser in headless mode
        verbose: Whether to print debug information

    Returns:
        str: The response from AskALCF

    Raises:
        Exception: If the query fails for any reason
    """
    try:
        async with async_playwright() as p:
            if verbose:
                print(f"Launching browser (headless={headless})...")

            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page()

            try:
                if verbose:
                    print(f"Navigating to {ASK_ALCF_URL}...")

                await page.goto(ASK_ALCF_URL, wait_until="networkidle", timeout=30000)

                if verbose:
                    print("Waiting for page to load...")

                # Look for the chat input - try multiple possible selectors
                input_selector = 'input[placeholder*="Ask"], textarea[placeholder*="Ask"], input[data-testid*="chatInput"], textarea[data-testid*="chatInput"]'

                if verbose:
                    print(f"Looking for input field with selector: {input_selector}")

                # Wait for input to be visible
                await page.wait_for_selector(input_selector, timeout=10000, state="visible")

                if verbose:
                    print(f"Sending question: {question}")

                # Type the question
                await page.fill(input_selector, question)

                # Submit - look for submit button or press Enter
                # Try to find a submit button first
                submit_selectors = [
                    'button[kind="primary"]',
                    'button[type="submit"]',
                    'button:has-text("Submit")',
                    'button:has-text("Send")'
                ]

                submitted = False
                for selector in submit_selectors:
                    try:
                        if await page.locator(selector).is_visible():
                            if verbose:
                                print(f"Clicking submit button: {selector}")
                            await page.click(selector)
                            submitted = True
                            break
                    except:
                        continue

                # If no submit button found, press Enter
                if not submitted:
                    if verbose:
                        print("No submit button found, pressing Enter")
                    await page.press(input_selector, "Enter")

                if verbose:
                    print("Waiting for response to start...")

                try:
                    await page.wait_for_selector(
                        'text="Generating answer..."',
                        timeout=10000,
                        state="visible"
                    )
                    if verbose:
                        print("Response generation started")
                except PlaywrightTimeoutError:
                    if verbose:
                        print("Warning: 'Generating answer...' text not found, continuing anyway")

                if verbose:
                    print(f"Waiting for response to complete (timeout: {timeout}ms)...")

                # Wait for "Generating answer..." to disappear
                max_wait = timeout / 1000  # Convert to seconds
                start_time = asyncio.get_event_loop().time()

                while asyncio.get_event_loop().time() - start_time < max_wait:
                    try:
                        generating_locator = page.locator('text="Generating answer..."')
                        is_visible = await generating_locator.is_visible()
                        if not is_visible:
                            if verbose:
                                print("Response generation completed")
                            break
                    except:
                        # If we can't find it, it might have already disappeared
                        break

                    await asyncio.sleep(0.5)
                else:
                    # Timeout reached
                    if verbose:
                        print("Warning: Response generation timed out")

                # Wait a bit more to ensure the DOM is fully updated
                await asyncio.sleep(2)

                if verbose:
                    print("Extracting response...")

                # Look for the AskALCF response using paragraph-based extraction
                # The response comes after the user's question
                try:
                    # Get all paragraph elements
                    all_paragraphs = await page.locator('p').all()

                    # Find the question paragraph and response paragraphs
                    response_paragraphs = []
                    found_question = False

                    for para in all_paragraphs:
                        text = (await para.inner_text()).strip()

                        # Skip empty paragraphs
                        if not text:
                            continue

                        # Look for the user's question
                        if text == question:
                            found_question = True
                            continue

                        # After finding the question, collect response paragraphs
                        if found_question:
                            # Skip the "AskALCF" header, "Send" button, and feedback text
                            if text in ["AskALCF", "Send", "Generating answer...", "AskALCF Feedback"]:
                                continue
                            # Stop if we hit the feedback section
                            if "AskALCF Feedback" in text or "Ask a question about ALCF" in text:
                                break
                            # Collect response paragraphs
                            response_paragraphs.append(text)

                    if not response_paragraphs:
                        raise Exception("No response paragraphs found")

                    response_text = '\n\n'.join(response_paragraphs)

                    if verbose:
                        print(f"Response extracted ({len(response_text)} characters)")

                    return response_text

                except Exception as e:
                    # Fallback: try to get all text from the page and extract what looks like a response
                    if verbose:
                        print(f"Warning: Structured extraction failed ({e}), trying fallback method")

                    page_text = await page.locator('body').inner_text()

                    # Try to find the response after the question
                    if question in page_text:
                        parts = page_text.split(question, 1)
                        if len(parts) > 1:
                            # Get text after the question
                            after_question = parts[1]

                            # Try to extract meaningful response
                            # Look for text before common UI elements
                            end_markers = ["AskALCF Feedback", "Ask a question about ALCF", "AskALCF User Documentation"]
                            for marker in end_markers:
                                if marker in after_question:
                                    after_question = after_question.split(marker)[0]

                            response_text = after_question.strip()

                            if response_text and len(response_text) > 10:
                                if verbose:
                                    print(f"Fallback extraction successful ({len(response_text)} characters)")
                                return response_text

                    raise Exception("Could not extract response from page")

            finally:
                await browser.close()

    except Exception as e:
        error_msg = f"Error querying AskALCF: {type(e).__name__}: {str(e)}"
        if verbose:
            print(error_msg)
        raise Exception(error_msg)


def _handle_error(e: Exception, context: str = "") -> str:
    """
    Provide clear, actionable error messages.

    Args:
        e: The exception that occurred
        context: Additional context about where the error occurred

    Returns:
        str: Formatted error message
    """
    error_type = type(e).__name__
    error_msg = str(e)

    if "timeout" in error_msg.lower() or isinstance(e, PlaywrightTimeoutError):
        return (
            f"Request timed out while {context}. "
            "The AskALCF service may be slow or unavailable. "
            "Try increasing the timeout parameter or try again later."
        )
    elif "navigation" in error_msg.lower() or "net::" in error_msg.lower():
        return (
            f"Could not connect to {ASK_ALCF_URL}. "
            "Please check your internet connection and verify that ask.alcf.anl.gov is accessible."
        )
    elif "selector" in error_msg.lower():
        return (
            "Could not find expected elements on the page. "
            "The AskALCF website structure may have changed. "
            "Please report this issue to the server maintainer."
        )
    else:
        return f"{error_type}: {error_msg}"


# Lifespan context manager
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for FastAPI application."""
    # Startup
    print(f"ALCF OpenAPI Server starting up...")
    print(f"Documentation available at: http://localhost:8000/docs")
    yield
    # Shutdown
    print("ALCF OpenAPI Server shutting down...")


# FastAPI Application
app = FastAPI(
    title="ALCF Tool Server",
    description=(
        "OpenAPI tool server for querying ALCF (Argonne Leadership Computing Facility) "
        "systems and resources through the ask.alcf.anl.gov AI assistant.\n\n"
        "This server provides access to information about:\n"
        "- ALCF Systems (Aurora, Polaris, AI Testbed)\n"
        "- Software environments and modules\n"
        "- Job submission and scheduling\n"
        "- Compilation and optimization guidance\n"
        "- Best practices for HPC workloads\n"
        "- Data management and file systems\n"
        "- Account and project management"
    ),
    version="1.0.0",
    lifespan=lifespan,
    servers=[
        {"url": "http://localhost:8000", "description": "Local development server"},
    ]
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", tags=["Health"])
async def root():
    """Root endpoint - returns server information."""
    return {
        "name": "ALCF Tool Server",
        "version": "1.0.0",
        "description": "OpenAPI server for querying ALCF systems and resources",
        "documentation": "/docs",
        "health": "/health"
    }


@app.get("/health", tags=["Health"])
async def health():
    """Health check endpoint."""
    return {"status": "healthy", "service": "ALCF Tool Server"}


@app.post(
    "/ask",
    response_model=ALCFResponse,
    responses={
        200: {"description": "Successful response", "model": ALCFResponse},
        400: {"description": "Invalid request", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    },
    tags=["ALCF"],
    summary="Ask a question about ALCF",
    description=(
        "Query the ALCF AI assistant for information about ALCF systems and resources.\n\n"
        "**Examples:**\n"
        "- System information: 'What is Aurora?', 'How many nodes does Polaris have?'\n"
        "- Software: 'How do I compile code on Aurora?', 'What Python environments are available?'\n"
        "- Jobs: 'How do I submit a job on Polaris?', 'What are the queue policies?'\n"
        "- Best practices: 'What are best practices for MPI+OpenMP on Aurora?'"
    ),
    operation_id="ask_alcf_question"
)
async def ask_question(request: AskQuestionRequest):
    """
    Ask a question about ALCF systems, resources, or best practices.

    This endpoint queries the official ALCF AI assistant to provide current,
    accurate information directly from ALCF's knowledge base.
    """
    try:
        response = await _query_ask_alcf(
            question=request.question,
            timeout=request.timeout,
            headless=True,
            verbose=True
        )

        if len(response) > CHARACTER_LIMIT:
            response = response[:CHARACTER_LIMIT]
            truncated = True
            response += f"\n\n[Response truncated at {CHARACTER_LIMIT} characters]"
        else:
            truncated = False

        if request.response_format == ResponseFormat.JSON:
            return ALCFResponse(
                question=request.question,
                answer=response,
                source=ASK_ALCF_URL,
                truncated=truncated
            )
        else:  # MARKDOWN format
            markdown_response = f"# ALCF Query Response\n\n"
            markdown_response += f"**Question:** {request.question}\n\n"
            markdown_response += f"**Answer:**\n\n{response}\n\n"
            markdown_response += f"*Source: [{ASK_ALCF_URL}]({ASK_ALCF_URL})*"

            return ALCFResponse(
                question=request.question,
                answer=markdown_response,
                source=ASK_ALCF_URL,
                truncated=truncated
            )

    except Exception as e:
        error_message = _handle_error(e, context="querying AskALCF")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


@app.post(
    "/system-info",
    response_model=ALCFResponse,
    responses={
        200: {"description": "Successful response", "model": ALCFResponse},
        400: {"description": "Invalid request", "model": ErrorResponse},
        500: {"description": "Internal server error", "model": ErrorResponse}
    },
    tags=["ALCF"],
    summary="Get system information",
    description=(
        "Get detailed information about a specific ALCF system.\n\n"
        "**Valid systems:** Aurora, Polaris, AI Testbed, Cerebras, SambaNova, Groq"
    ),
    operation_id="get_system_info"
)
async def get_system_info(request: SystemInfoRequest):
    """
    Get detailed information about a specific ALCF system.

    This is a convenience endpoint that queries for system-specific information.
    """
    question = f"What is {request.system_name} and what are its key specifications, architecture, and capabilities?"

    try:
        response = await _query_ask_alcf(
            question=question,
            timeout=DEFAULT_TIMEOUT,
            headless=True,
            verbose=False
        )

        if len(response) > CHARACTER_LIMIT:
            response = response[:CHARACTER_LIMIT]
            truncated = True
            response += f"\n\n[Response truncated at {CHARACTER_LIMIT} characters]"
        else:
            truncated = False

        markdown_response = f"# {request.system_name} Information\n\n"
        markdown_response += f"{response}\n\n"
        markdown_response += f"*Source: [{ASK_ALCF_URL}]({ASK_ALCF_URL})*"

        return ALCFResponse(
            question=question,
            answer=markdown_response,
            source=ASK_ALCF_URL,
            truncated=truncated
        )

    except Exception as e:
        error_message = _handle_error(e, context=f"getting information about {request.system_name}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=error_message
        )


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
