#!/usr/bin/env python3
"""
AskALCF Playwright Client

A simple script that uses Playwright to interact with ask.alcf.anl.gov
by automating a real browser session.
"""

import argparse
import sys
import time
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeout


def ask_alcf(question: str, timeout: int = 60000, headless: bool = True, verbose: bool = False):
    """
    Send a question to ask.alcf.anl.gov and retrieve the response.

    Args:
        question: The question to ask
        timeout: Maximum time to wait for response in milliseconds (default: 60000)
        headless: Whether to run browser in headless mode (default: True)
        verbose: Whether to print debug information (default: False)

    Returns:
        str: The response from AskALCF

    Raises:
        Exception: If unable to get response
    """

    with sync_playwright() as p:
        # Launch browser
        if verbose:
            print(f"Launching browser (headless={headless})...")

        browser = p.chromium.launch(headless=headless)
        context = browser.new_context()
        page = context.new_page()

        try:
            # Navigate to AskALCF
            if verbose:
                print("Navigating to ask.alcf.anl.gov...")

            page.goto("https://ask.alcf.anl.gov", wait_until="networkidle", timeout=30000)

            # Wait for the page to be ready
            if verbose:
                print("Waiting for page to load...")

            # Look for the chat input - Streamlit chat_input widget
            # Try multiple possible selectors
            input_selector = 'input[placeholder*="Ask"], textarea[placeholder*="Ask"], input[data-testid*="chatInput"], textarea[data-testid*="chatInput"]'

            if verbose:
                print(f"Looking for input field with selector: {input_selector}")

            # Wait for input to be visible
            page.wait_for_selector(input_selector, timeout=10000, state="visible")

            if verbose:
                print(f"Sending question: {question}")

            # Type the question
            page.fill(input_selector, question)

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
                    if page.locator(selector).is_visible():
                        if verbose:
                            print(f"Clicking submit button: {selector}")
                        page.click(selector)
                        submitted = True
                        break
                except:
                    continue

            # If no submit button found, press Enter
            if not submitted:
                if verbose:
                    print("No submit button found, pressing Enter")
                page.press(input_selector, "Enter")

            # Wait for "Generating answer..." to appear (confirmation that question was sent)
            if verbose:
                print("Waiting for response to start...")

            try:
                page.wait_for_selector('text="Generating answer..."', timeout=10000, state="visible")
                if verbose:
                    print("Response generation started")
            except PlaywrightTimeout:
                if verbose:
                    print("Warning: 'Generating answer...' text not found, continuing anyway")

            # Wait for the response to complete
            # The "Generating answer..." text should disappear when done
            if verbose:
                print(f"Waiting for response to complete (timeout: {timeout}ms)...")

            max_wait = timeout / 1000  # Convert to seconds
            start_time = time.time()

            # Wait for "Generating answer..." to disappear or timeout
            while time.time() - start_time < max_wait:
                try:
                    # Check if "Generating answer..." is still visible
                    generating_locator = page.locator('text="Generating answer..."')
                    if not generating_locator.is_visible():
                        if verbose:
                            print("Response generation completed")
                        break
                except:
                    # If we can't find it, it might have already disappeared
                    break

                time.sleep(0.5)
            else:
                # Timeout reached
                raise Exception(f"Response generation timed out after {timeout}ms")

            # Wait a bit more to ensure the DOM is fully updated
            time.sleep(2)

            if verbose:
                print("Extracting response...")

            # Look for the AskALCF response
            # The response appears after text containing "AskALCF"
            # We'll search for paragraphs that contain the actual response content

            # Strategy: Find all paragraphs and look for the response pattern
            # The response comes after the user's question
            try:
                # Get all paragraph elements
                all_paragraphs = page.locator('p').all()

                # Find the question paragraph and response paragraphs
                response_paragraphs = []
                found_question = False

                for para in all_paragraphs:
                    text = para.inner_text().strip()

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

                page_text = page.locator('body').inner_text()

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
            # Clean up
            context.close()
            browser.close()


def main():
    """Main entry point for command-line usage."""
    parser = argparse.ArgumentParser(
        description="Ask questions to ask.alcf.anl.gov programmatically",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s "What is Aurora?"
  %(prog)s "How do I compile code on Aurora?" --timeout 90000
  %(prog)s "What is the best environment variable setting for oneCCL?" --no-headless --verbose
        """
    )

    parser.add_argument(
        "question",
        help="The question to ask"
    )

    parser.add_argument(
        "-t", "--timeout",
        type=int,
        default=60000,
        help="Maximum time to wait for response in milliseconds (default: 60000)"
    )

    parser.add_argument(
        "--no-headless",
        action="store_true",
        help="Show browser window (useful for debugging)"
    )

    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print debug information"
    )

    args = parser.parse_args()

    try:
        response = ask_alcf(
            question=args.question,
            timeout=args.timeout,
            headless=not args.no_headless,
            verbose=args.verbose
        )

        print("\n" + "="*80)
        print("RESPONSE:")
        print("="*80)
        print(response)
        print("="*80 + "\n")

        return 0

    except KeyboardInterrupt:
        print("\n\nInterrupted by user", file=sys.stderr)
        return 130

    except Exception as e:
        print(f"\nError: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        return 1


if __name__ == "__main__":
    sys.exit(main())
