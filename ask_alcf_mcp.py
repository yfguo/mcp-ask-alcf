#!/usr/bin/env python3
"""
MCP Server for ALCF (Argonne Leadership Computing Facility).

This server provides tools to query information about ALCF systems including Aurora,
Polaris, AI Testbed systems, and general HPC guidance through the ask.alcf.anl.gov
AI-powered assistant interface.
"""

from typing import Optional
from enum import Enum
import asyncio
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError
from pydantic import BaseModel, Field, field_validator, ConfigDict
from mcp.server.fastmcp import FastMCP

# Initialize the MCP server
mcp = FastMCP("alcf_mcp")

# Constants
CHARACTER_LIMIT = 25000  # Maximum response size in characters
DEFAULT_TIMEOUT = 60000  # Default timeout in milliseconds (60 seconds)
ASK_ALCF_URL = "https://ask.alcf.anl.gov"


# Enums
class ResponseFormat(str, Enum):
    """Output format for tool responses."""
    MARKDOWN = "markdown"
    JSON = "json"


# Pydantic Models for Input Validation
class AskALCFInput(BaseModel):
    """Input model for querying ALCF information."""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )

    question: str = Field(
        ...,
        description=(
            "Question to ask about ALCF systems, resources, or best practices. "
            "Examples: 'What is Aurora?', 'How do I compile code on Aurora?', "
            "'What are the best practices for running PyTorch on Polaris?', "
            "'How do I set up my environment on ALCF systems?'"
        ),
        min_length=5,
        max_length=1000
    )

    timeout: Optional[int] = Field(
        default=DEFAULT_TIMEOUT,
        description="Maximum time to wait for response in milliseconds (default: 60000 for 60 seconds)",
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

            # Launch browser
            browser = await p.chromium.launch(headless=headless)
            page = await browser.new_page()

            try:
                if verbose:
                    print(f"Navigating to {ASK_ALCF_URL}...")

                # Navigate to the AskALCF page
                await page.goto(ASK_ALCF_URL, timeout=timeout)

                if verbose:
                    print("Waiting for chat input field...")

                # Wait for the page to load and find the input field
                # The actual selector may need adjustment based on the page structure
                input_selector = 'textarea[data-testid="stChatInputTextArea"], textarea[placeholder*="chat"], textarea'
                await page.wait_for_selector(input_selector, timeout=30000)

                if verbose:
                    print(f"Typing question: {question}")

                # Type the question
                await page.fill(input_selector, question)

                # Submit the question (press Enter)
                await page.press(input_selector, "Enter")

                if verbose:
                    print("Waiting for 'Generating answer...' indicator...")

                # Wait for "Generating answer..." to appear
                try:
                    await page.wait_for_selector(
                        'text=/generating answer/i',
                        timeout=10000,
                        state="visible"
                    )
                except PlaywrightTimeoutError:
                    if verbose:
                        print("Did not detect 'Generating answer...' indicator, continuing...")

                if verbose:
                    print("Waiting for response to complete...")

                # Wait a bit for the response to start appearing
                await asyncio.sleep(2)

                # Wait for the generating indicator to disappear (response complete)
                try:
                    await page.wait_for_selector(
                        'text=/generating answer/i',
                        timeout=timeout,
                        state="hidden"
                    )
                except PlaywrightTimeoutError:
                    if verbose:
                        print("Timeout waiting for response completion, extracting current content...")

                # Additional wait to ensure content is fully rendered
                await asyncio.sleep(1)

                if verbose:
                    print("Extracting response text...")

                # Extract the response - this selector may need adjustment
                # Look for the last message in the chat that's not from the user
                response_text = ""

                # Try multiple strategies to get the response
                try:
                    # Strategy 1: Look for assistant message containers
                    messages = await page.query_selector_all('[data-testid="stChatMessage"]')
                    if messages and len(messages) > 0:
                        # Get the last message (should be the assistant's response)
                        last_message = messages[-1]
                        response_text = await last_message.inner_text()

                    # Strategy 2: If that didn't work, try getting all text from the chat area
                    if not response_text:
                        chat_container = await page.query_selector('[data-testid="stChatMessageContainer"]')
                        if chat_container:
                            response_text = await chat_container.inner_text()

                    # Strategy 3: Fallback to getting visible text from main content area
                    if not response_text:
                        main_content = await page.query_selector('main, .main, #root')
                        if main_content:
                            response_text = await main_content.inner_text()

                except Exception as extract_error:
                    if verbose:
                        print(f"Error during extraction: {extract_error}")
                    response_text = f"Error extracting response: {str(extract_error)}"

                if not response_text or len(response_text.strip()) == 0:
                    response_text = "No response received from AskALCF. The query may have timed out or the page structure may have changed."

                if verbose:
                    print(f"Response received: {response_text[:200]}...")

                return response_text.strip()

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
            f"Error: Request timed out while {context}. "
            "The AskALCF service may be slow or unavailable. "
            "Try increasing the timeout parameter or try again later."
        )
    elif "navigation" in error_msg.lower() or "net::" in error_msg.lower():
        return (
            f"Error: Could not connect to {ASK_ALCF_URL}. "
            "Please check your internet connection and verify that ask.alcf.anl.gov is accessible."
        )
    elif "selector" in error_msg.lower():
        return (
            f"Error: Could not find expected elements on the page. "
            "The AskALCF website structure may have changed. "
            "Please report this issue to the server maintainer."
        )
    else:
        return f"Error: {error_type} - {error_msg}"


# MCP Tools
@mcp.tool(
    name="alcf_ask_question",
    annotations={
        "title": "Ask ALCF Question",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def alcf_ask_question(params: AskALCFInput) -> str:
    """
    Query the ALCF AI assistant (ask.alcf.anl.gov) for information about ALCF systems and resources.

    This tool provides access to ALCF-specific information including:
    - System specifications (Aurora, Polaris, AI Testbed systems)
    - Software environments and modules
    - Job submission and scheduling
    - Compilation and optimization guidance
    - Best practices for HPC workloads
    - Data management and file systems
    - Account and project management
    - Training resources and documentation

    The tool automates interaction with the official ALCF AI assistant to provide
    current, accurate information directly from ALCF's knowledge base.

    Args:
        params (AskALCFInput): Validated input parameters containing:
            - question (str): Your question about ALCF systems or resources
            - timeout (Optional[int]): Maximum wait time in milliseconds (default: 60000)
            - response_format (ResponseFormat): Output format (default: "markdown")

    Returns:
        str: Response from the ALCF AI assistant in the requested format

    Examples:
        Questions about systems:
        - "What is Aurora and what are its specifications?"
        - "How many nodes does Polaris have?"
        - "What AI accelerators are available in the AI Testbed?"

        Questions about software:
        - "How do I compile code on Aurora?"
        - "What is the best way to set up PyTorch on Polaris?"
        - "How do I use Intel compilers on Aurora?"

        Questions about usage:
        - "How do I submit a job on Polaris?"
        - "What are the best practices for MPI on Aurora?"
        - "How do I manage my ALCF allocation?"

        Questions about data:
        - "What file systems are available on ALCF systems?"
        - "How do I transfer large datasets to Aurora?"

    Error Handling:
        - Returns clear error message if timeout occurs (suggest increasing timeout)
        - Returns error if cannot connect to ask.alcf.anl.gov (check connectivity)
        - Returns error if page structure has changed (report to maintainer)
        - Input validation errors are handled by Pydantic model

    Notes:
        - This tool requires an internet connection to access ask.alcf.anl.gov
        - Response times vary depending on question complexity (typically 10-60 seconds)
        - For very complex queries, consider increasing the timeout parameter
        - The service uses Playwright browser automation, so responses reflect
          the current state of the ALCF AI assistant
    """
    try:
        # Query the AskALCF service
        response = await _query_ask_alcf(
            question=params.question,
            timeout=params.timeout,
            headless=True,
            verbose=False
        )

        # Check character limit
        if len(response) > CHARACTER_LIMIT:
            response = response[:CHARACTER_LIMIT]
            response += f"\n\n[Response truncated at {CHARACTER_LIMIT} characters. The full response was longer.]"

        # Format response based on requested format
        if params.response_format == ResponseFormat.JSON:
            import json
            result = {
                "question": params.question,
                "answer": response,
                "source": "ask.alcf.anl.gov",
                "truncated": len(response) >= CHARACTER_LIMIT
            }
            return json.dumps(result, indent=2)
        else:  # MARKDOWN format
            formatted_response = f"# ALCF Query Response\n\n"
            formatted_response += f"**Question:** {params.question}\n\n"
            formatted_response += f"**Answer:**\n\n{response}\n\n"
            formatted_response += f"*Source: [ask.alcf.anl.gov]({ASK_ALCF_URL})*"
            return formatted_response

    except Exception as e:
        error_message = _handle_error(e, context="querying AskALCF")

        if params.response_format == ResponseFormat.JSON:
            import json
            return json.dumps({
                "error": True,
                "message": error_message,
                "question": params.question
            }, indent=2)
        else:
            return f"# Error\n\n{error_message}"


@mcp.tool(
    name="alcf_get_system_info",
    annotations={
        "title": "Get ALCF System Information",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": True
    }
)
async def alcf_get_system_info(system_name: str) -> str:
    """
    Get detailed information about a specific ALCF system.

    This is a convenience tool that queries for system-specific information.

    Args:
        system_name (str): Name of the ALCF system. Valid options include:
            - "Aurora" - The exascale supercomputer
            - "Polaris" - GPU-accelerated supercomputer
            - "AI Testbed" - Collection of AI accelerators
            - "Cerebras" - Cerebras CS-2 wafer-scale system
            - "SambaNova" - SambaNova DataScale system
            - "Groq" - Groq LPU systems

    Returns:
        str: Detailed information about the specified system in Markdown format

    Examples:
        - alcf_get_system_info("Aurora")
        - alcf_get_system_info("Polaris")
        - alcf_get_system_info("AI Testbed")
    """
    question = f"What is {system_name} and what are its key specifications, architecture, and capabilities?"

    params = AskALCFInput(
        question=question,
        timeout=DEFAULT_TIMEOUT,
        response_format=ResponseFormat.MARKDOWN
    )

    try:
        return await alcf_ask_question(params)
    except Exception as e:
        return _handle_error(e, context=f"getting information about {system_name}")


# Main entry point for stdio transport
if __name__ == "__main__":
    mcp.run()
