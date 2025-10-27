# Quick Start Guide

Get the Ask-ALCF MCP Server running in 5 minutes!

## Prerequisites

- Python 3.8+
- pip
- Internet connection

## Installation Steps

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Install Playwright Browser

```bash
playwright install chromium
```

### 3. Test the Installation

```bash
python -m py_compile ask_alcf_mcp.py
```

If no errors appear, you're ready to go!

## Usage Options

### Option A: Use with Claude Desktop (Recommended)

1. **Find your configuration file:**
   - **MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`
   - **Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

2. **Edit the configuration:**
   ```json
   {
     "mcpServers": {
       "alcf": {
         "command": "python",
         "args": ["/full/path/to/ask_alcf_mcp.py"]
       }
     }
   }
   ```

3. **Replace** `/full/path/to/ask_alcf_mcp.py` with the actual path

4. **Restart Claude Desktop**

5. **Test it!** Ask Claude:
   - "What is Aurora?"
   - "How do I compile code on Polaris?"
   - "What are the ALCF AI Testbed systems?"

### Option B: Run Examples Script

```bash
python examples.py
```

This will demonstrate the MCP server tools with sample queries.

### Option C: Use Programmatically

```python
from alcf_mcp import alcf_ask_question, AskALCFInput, ResponseFormat

# Create query
params = AskALCFInput(
    question="What is Aurora?",
    response_format=ResponseFormat.MARKDOWN
)

# Get response (async)
result = await alcf_ask_question(params)
print(result)
```

## Common Questions

### Q: How long do queries take?
**A:** Typically 10-60 seconds, depending on complexity.

### Q: Can I use this offline?
**A:** No, it requires internet access to query ask.alcf.anl.gov.

### Q: What if I get a timeout error?
**A:** Increase the timeout parameter:
```python
params = AskALCFInput(
    question="Your question",
    timeout=120000  # 120 seconds
)
```

### Q: How do I get JSON responses?
**A:** Set the response format:
```python
params = AskALCFInput(
    question="Your question",
    response_format=ResponseFormat.JSON
)
```

## Example Questions

**System Information:**
- "What is Aurora and what are its specifications?"
- "How many GPUs does Polaris have?"
- "What systems are in the AI Testbed?"

**Software & Development:**
- "How do I compile MPI code on Aurora?"
- "What Python environments are available on Polaris?"
- "How do I use Intel compilers?"

**Job Management:**
- "How do I submit a job on Polaris?"
- "What are the queue policies?"
- "How do I check my allocation usage?"

**Best Practices:**
- "What are best practices for I/O on ALCF systems?"
- "How do I optimize code for Intel GPUs?"
- "What's the recommended way to use MPI+OpenMP?"

## Troubleshooting

### Installation Failed?

```bash
# Make sure pip is updated
pip install --upgrade pip

# Install dependencies with verbose output
pip install -v -r requirements.txt

# On Linux, install system dependencies
playwright install-deps chromium
```

### Permission Denied?

```bash
# Make the script executable
chmod +x ask_alcf_mcp.py
```

### Import Errors?

```bash
# Verify installation
pip list | grep -E "(mcp|playwright|pydantic)"

# Reinstall if needed
pip install --force-reinstall -r requirements.txt
```

## Next Steps

- Read [README.md](README.md) for complete documentation
- Check [examples.py](examples.py) for usage patterns
- See [CONTRIBUTING.md](CONTRIBUTING.md) to contribute
- Review [CHANGELOG.md](CHANGELOG.md) for version history

## Support

- **ALCF Issues**: support@alcf.anl.gov
- **Server Issues**: Open a GitHub issue
- **MCP Questions**: https://modelcontextprotocol.io/

## Quick Reference

| File | Purpose |
|------|---------|
| `ask_alcf_mcp.py` | Main server implementation |
| `requirements.txt` | Python dependencies |
| `README.md` | Full documentation |
| `examples.py` | Usage examples |
| `setup.py` | Installation script |

---

**Ready to go?** Ask your first question about ALCF! 🚀
