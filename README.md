# AskALCF Proxy

A simple Playwright-based script to programmatically interact with [ask.alcf.anl.gov](https://ask.alcf.anl.gov).

## Overview

This script automates a real browser session using Playwright to send questions to AskALCF and retrieve responses. It's much simpler than trying to reverse-engineer the WebSocket/protobuf protocol used by Streamlit.

## Setup

1. **Create and activate virtual environment** (already done at `.venv/`):
   ```bash
   source .venv/bin/activate
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers**:
   ```bash
   playwright install chromium
   ```

## Usage

### Basic Usage

```bash
python ask_alcf.py "What is Aurora?"
```

### With Custom Timeout

```bash
python ask_alcf.py "How do I compile code on Aurora?" --timeout 90000
```

### Debug Mode (Show Browser)

```bash
python ask_alcf.py "What is the best environment variable setting for oneCCL?" --no-headless --verbose
```

### Command-Line Options

- `question` - The question to ask (required)
- `-t, --timeout` - Maximum time to wait for response in milliseconds (default: 60000)
- `--no-headless` - Show browser window (useful for debugging)
- `-v, --verbose` - Print debug information

### Help

```bash
python ask_alcf.py --help
```

## How It Works

1. Launches a Chromium browser using Playwright
2. Navigates to ask.alcf.anl.gov
3. Finds the chat input field
4. Sends your question
5. Waits for "Generating answer..." to appear
6. Waits for the response to complete
7. Extracts the response text
8. Returns the formatted response

## Python API

You can also use the script as a Python module:

```python
from ask_alcf import ask_alcf

response = ask_alcf(
    question="What is Aurora?",
    timeout=60000,
    headless=True,
    verbose=False
)

print(response)
```

## Examples

```bash
# Simple query
python ask_alcf.py "What is Aurora?"

# More complex query
python ask_alcf.py "How do I set up PyTorch on Aurora?"

# Debug mode
python ask_alcf.py "What is oneCCL?" --no-headless --verbose
```

## Notes

- The script runs in headless mode by default (no visible browser window)
- Default timeout is 60 seconds, which should be sufficient for most queries
- Use `--verbose` flag to see detailed progress information
- Use `--no-headless` to see the browser in action (useful for debugging)

## Troubleshooting

If you encounter issues:

1. **Timeout errors**: Increase the timeout with `--timeout 90000` (90 seconds)
2. **Connection errors**: Check your internet connection and that ask.alcf.anl.gov is accessible
3. **Browser issues**: Reinstall Playwright browsers with `playwright install chromium`
4. **Debugging**: Use `--no-headless --verbose` to see what's happening

## License

This code uses MIT license (see LICENSE).
