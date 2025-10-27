# Ask-ALCF MCP Server

A Model Context Protocol (MCP) server that provides AI assistants with access to information about ALCF (Argonne Leadership Computing Facility) systems and resources through the official ask.alcf.anl.gov AI assistant.

## Overview

This MCP server enables Large Language Models to query detailed information about:

- **ALCF Systems**: Aurora (exascale supercomputer), Polaris (GPU supercomputer), AI Testbed systems
- **Software & Environments**: Compilers, libraries, modules, frameworks
- **Job Management**: Submission, scheduling, resource allocation
- **Best Practices**: Optimization, compilation, parallelization
- **Data Management**: File systems, data transfer, storage
- **Account Management**: Projects, allocations, access

The server uses Playwright to automate interactions with the official ALCF AI assistant at ask.alcf.anl.gov, providing current and authoritative information directly from ALCF's knowledge base.

## Features

- **Two Main Tools**:
  - `alcf_ask_question`: General-purpose tool for any ALCF-related question
  - `alcf_get_system_info`: Convenience tool for quick system information lookup

- **Flexible Response Formats**: JSON or Markdown output
- **Configurable Timeouts**: Adjust wait times for complex queries
- **Robust Error Handling**: Clear, actionable error messages
- **Character Limits**: Prevents overwhelming responses (25,000 character limit)
- **Async Operations**: Non-blocking queries for better performance

## Installation

### Prerequisites

- Python 3.8 or higher
- pip package manager

### Setup

1. **Clone or download this server**

2. **Install Python dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

3. **Install Playwright browsers:**
   ```bash
   playwright install chromium
   ```

4. **Verify installation:**
   ```bash
   python -m py_compile ask_alcf_mcp.py
   ```

## Usage

### Running the Server

The server uses stdio transport by default, making it compatible with MCP clients like Claude Desktop:

```bash
python ask_alcf_mcp.py
```

### Configuration for Claude Desktop

Add to your Claude Desktop configuration file:

**MacOS**: `~/Library/Application Support/Claude/claude_desktop_config.json`  
**Windows**: `%APPDATA%\Claude\claude_desktop_config.json`

```json
{
  "mcpServers": {
    "alcf": {
      "command": "python",
      "args": ["/path/to/ask_alcf_mcp.py"]
    }
  }
}
```

Replace `/path/to/ask_alcf_mcp.py` with the actual path to the server file.

## Available Tools

### 1. alcf_ask_question

Ask any question about ALCF systems, resources, or best practices.

**Parameters:**
- `question` (required, string): Your question about ALCF
  - Min length: 5 characters
  - Max length: 1000 characters
  - Examples: "What is Aurora?", "How do I compile code on Polaris?"

- `timeout` (optional, integer): Maximum wait time in milliseconds
  - Default: 60000 (60 seconds)
  - Range: 10000-180000 (10-180 seconds)
  - Use higher values for complex queries

- `response_format` (optional, string): Output format
  - Options: "markdown" (default) or "json"
  - Markdown: Human-readable with formatting
  - JSON: Structured data for programmatic use

**Example Questions:**

*System Information:*
```
"What is Aurora and what are its specifications?"
"How many nodes does Polaris have?"
"What AI accelerators are in the AI Testbed?"
```

*Software & Development:*
```
"How do I compile code on Aurora?"
"What is the best way to set up PyTorch on Polaris?"
"How do I use Intel compilers on Aurora?"
"What MPI implementations are available?"
```

*Job Management:*
```
"How do I submit a job on Polaris?"
"What are the queue policies on Aurora?"
"How do I check my job status?"
```

*Best Practices:*
```
"What are the best practices for MPI+OpenMP on Aurora?"
"How do I optimize my code for Intel GPUs?"
"What's the recommended way to handle I/O on ALCF systems?"
```

*Data Management:*
```
"What file systems are available on ALCF systems?"
"How do I transfer large datasets to Aurora?"
"What are the storage quotas?"
```

### 2. alcf_get_system_info

Convenience tool for quickly getting information about a specific ALCF system.

**Parameters:**
- `system_name` (required, string): Name of the ALCF system
  - Valid options: "Aurora", "Polaris", "AI Testbed", "Cerebras", "SambaNova", "Groq"

**Example Usage:**
```
alcf_get_system_info("Aurora")
alcf_get_system_info("Polaris")
alcf_get_system_info("Cerebras")
```

## Response Format Examples

### Markdown Response (Default)

```markdown
# ALCF Query Response

**Question:** What is Aurora?

**Answer:**

Aurora is ALCF's exascale supercomputer, featuring Intel Xeon CPU Max Series processors 
and Intel Data Center GPU Max Series accelerators. It has 10,624 nodes with 166 racks, 
providing over 2 exaFLOPS of peak performance...

*Source: [ask.alcf.anl.gov](https://ask.alcf.anl.gov)*
```

### JSON Response

```json
{
  "question": "What is Aurora?",
  "answer": "Aurora is ALCF's exascale supercomputer...",
  "source": "ask.alcf.anl.gov",
  "truncated": false
}
```

## Error Handling

The server provides clear, actionable error messages:

**Timeout Errors:**
```
Error: Request timed out while querying AskALCF. The AskALCF service may be 
slow or unavailable. Try increasing the timeout parameter or try again later.
```
*Solution:* Increase the timeout parameter to 90000 or 120000 milliseconds.

**Connection Errors:**
```
Error: Could not connect to https://ask.alcf.anl.gov. Please check your 
internet connection and verify that ask.alcf.anl.gov is accessible.
```
*Solution:* Check internet connectivity and verify the website is accessible.

**Page Structure Errors:**
```
Error: Could not find expected elements on the page. The AskALCF website 
structure may have changed. Please report this issue to the server maintainer.
```
*Solution:* Report the issue to the server maintainer for updates.

## Limitations and Considerations

1. **Internet Connection Required**: The server needs internet access to query ask.alcf.anl.gov

2. **Response Times**: Queries typically take 10-60 seconds depending on complexity

3. **Rate Limiting**: Be mindful of query frequency to avoid overloading the ALCF service

4. **Page Structure Changes**: If the ask.alcf.anl.gov website structure changes, the server may need updates

5. **Character Limits**: Responses are limited to 25,000 characters to prevent overwhelming context windows

6. **Headless Browser**: Uses Playwright's Chromium in headless mode for automation

## Troubleshooting

### Playwright Installation Issues

If `playwright install chromium` fails:
```bash
# On Linux, you may need to install dependencies
playwright install-deps chromium

# Or install browsers with sudo
sudo playwright install chromium
```

### Permission Errors

Ensure the server file is executable:
```bash
chmod +x ask_alcf_mcp.py
```

### Import Errors

Verify all dependencies are installed:
```bash
pip install --upgrade -r requirements.txt
```

### Timeout Issues

For complex questions, increase the timeout:
```python
# In your MCP client, set timeout to 120 seconds
{
  "question": "Detailed question about optimization...",
  "timeout": 120000
}
```

## Development

### Project Structure

```
alcf_mcp/
├── ask_alcf_mcp.py          # Main MCP server implementation
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

### Key Components

- **FastMCP Framework**: High-level MCP server framework
- **Playwright**: Browser automation for querying ask.alcf.anl.gov
- **Pydantic v2**: Input validation and data modeling
- **Async/Await**: Non-blocking operations for better performance

### Testing

Test the server by running it with a timeout:
```bash
timeout 5s python ask_alcf_mcp.py
```

Or use the MCP evaluation framework (if available) to test tool functionality.

## Contributing

Contributions are welcome! Areas for improvement:

1. **Additional Tools**: Add specialized tools for specific ALCF operations
2. **Caching**: Implement response caching for frequently asked questions
3. **Enhanced Parsing**: Improve response extraction for better accuracy
4. **Error Recovery**: Add retry logic for transient failures
5. **Documentation**: Expand examples and use cases

## License

MIT License - See LICENSE file for details

## Support

For issues related to:
- **This MCP Server**: Open an issue on the GitHub repository
- **ALCF Systems**: Contact support@alcf.anl.gov or visit https://docs.alcf.anl.gov/
- **MCP Protocol**: See https://modelcontextprotocol.io/

## Resources

- [ALCF Documentation](https://docs.alcf.anl.gov/)
- [ALCF Website](https://www.alcf.anl.gov/)
- [Ask ALCF AI Assistant](https://ask.alcf.anl.gov)
- [Model Context Protocol](https://modelcontextprotocol.io/)
- [MCP Python SDK](https://github.com/modelcontextprotocol/python-sdk)
- [Playwright Documentation](https://playwright.dev/python/)

## Acknowledgments

Built using:
- The Model Context Protocol by Anthropic
- ALCF's ask.alcf.anl.gov AI assistant service
- Playwright for browser automation
- FastMCP framework for simplified MCP server development
