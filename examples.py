#!/usr/bin/env python3
"""
Example usage of the ALCF MCP Server.

This script demonstrates how to use the MCP server tools programmatically.
Note: This is for demonstration purposes. In practice, the MCP server is
typically used through an MCP client like Claude Desktop.
"""

import asyncio
from alcf_mcp import alcf_ask_question, alcf_get_system_info, AskALCFInput, ResponseFormat


async def example_basic_question():
    """Example: Ask a basic question about Aurora."""
    print("=" * 80)
    print("Example 1: Basic Question about Aurora")
    print("=" * 80)

    params = AskALCFInput(
        question="What is Aurora?",
        timeout=60000,
        response_format=ResponseFormat.MARKDOWN
    )

    result = await alcf_ask_question(params)
    print(result)
    print()


async def example_technical_question():
    """Example: Ask a technical question about compilation."""
    print("=" * 80)
    print("Example 2: Technical Question about Compilation")
    print("=" * 80)

    params = AskALCFInput(
        question="How do I compile C++ code with MPI on Aurora?",
        timeout=90000,  # Longer timeout for complex question
        response_format=ResponseFormat.MARKDOWN
    )

    result = await alcf_ask_question(params)
    print(result)
    print()


async def example_json_response():
    """Example: Get response in JSON format."""
    print("=" * 80)
    print("Example 3: JSON Response Format")
    print("=" * 80)

    params = AskALCFInput(
        question="What are the specifications of Polaris?",
        timeout=60000,
        response_format=ResponseFormat.JSON
    )

    result = await alcf_ask_question(params)
    print(result)
    print()


async def example_system_info():
    """Example: Use the convenience system info tool."""
    print("=" * 80)
    print("Example 4: System Information Tool")
    print("=" * 80)

    result = await alcf_get_system_info("Polaris")
    print(result)
    print()


async def example_best_practices():
    """Example: Ask about best practices."""
    print("=" * 80)
    print("Example 5: Best Practices Question")
    print("=" * 80)

    params = AskALCFInput(
        question="What are the best practices for running PyTorch on Polaris?",
        timeout=90000,
        response_format=ResponseFormat.MARKDOWN
    )

    result = await alcf_ask_question(params)
    print(result)
    print()


async def example_data_management():
    """Example: Ask about data management."""
    print("=" * 80)
    print("Example 6: Data Management Question")
    print("=" * 80)

    params = AskALCFInput(
        question="How do I transfer large datasets to ALCF systems?",
        timeout=60000,
        response_format=ResponseFormat.MARKDOWN
    )

    result = await alcf_ask_question(params)
    print(result)
    print()


async def main():
    """Run all examples."""
    print("\n" + "=" * 80)
    print("ALCF MCP Server - Usage Examples")
    print("=" * 80 + "\n")

    print("NOTE: These examples will make real queries to ask.alcf.anl.gov")
    print("Each query may take 10-60 seconds to complete.\n")

    # Run examples
    try:
        await example_basic_question()
        await example_system_info()
        await example_json_response()
        # Uncomment to run additional examples (will take more time)
        # await example_technical_question()
        # await example_best_practices()
        # await example_data_management()

    except Exception as e:
        print(f"\nError running examples: {e}")
        print("\nMake sure you have:")
        print("1. Installed dependencies: pip install -r requirements.txt")
        print("2. Installed Playwright browsers: playwright install chromium")
        print("3. Internet connection to access ask.alcf.anl.gov")


if __name__ == "__main__":
    # Run the examples
    asyncio.run(main())
