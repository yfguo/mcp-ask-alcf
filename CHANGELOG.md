# Changelog

All notable changes to the ALCF MCP Server will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-10-27

### Added
- Initial release of ALCF MCP Server
- `alcf_ask_question` tool for general ALCF queries
- `alcf_get_system_info` convenience tool for system information
- Support for both JSON and Markdown response formats
- Configurable timeout settings (10-180 seconds)
- Character limit handling (25,000 character limit)
- Comprehensive error handling with actionable messages
- Pydantic v2 input validation
- Async/await operations using Playwright
- Complete documentation (README, CONTRIBUTING, examples)
- MIT License
- Setup script for easy installation

### Features
- Query information about ALCF systems (Aurora, Polaris, AI Testbed)
- Get software and environment guidance
- Learn about job submission and scheduling
- Access best practices and optimization tips
- Retrieve data management information
- Account and project management queries

### Technical Details
- Uses MCP Python SDK with FastMCP framework
- Playwright browser automation for querying ask.alcf.anl.gov
- Robust error handling for timeouts and connectivity issues
- Response truncation for large outputs
- Tool annotations for MCP compliance

## [Unreleased]

### Planned Features
- Response caching for frequently asked questions
- Retry logic with exponential backoff
- Enhanced response parsing
- Comprehensive test suite
- Performance optimizations
- Additional specialized tools
- HTTP/SSE transport support
- Configuration file support
- Structured logging
- Metrics collection

### Known Issues
- Response extraction may need adjustment if ask.alcf.anl.gov structure changes
- Long response times for complex queries (typically 10-60 seconds)
- Requires internet connectivity to function

---

## Version History

- **1.0.0** (2025-10-27) - Initial public release
