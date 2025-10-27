# Testing Guide for Ask-ALCF MCP Server

This document provides comprehensive testing procedures for the Ask-ALCF MCP Server.

## Pre-Testing Checklist

Before running tests, ensure:

- [ ] Python 3.8+ installed
- [ ] All dependencies installed (`pip install -r requirements.txt`)
- [ ] Playwright browsers installed (`playwright install chromium`)
- [ ] Internet connection available
- [ ] ask.alcf.anl.gov is accessible

## Quick Verification

### 1. Syntax Check

Verify the code compiles:
```bash
python -m py_compile ask_alcf_mcp.py
```

**Expected**: No output (success)
**If errors**: Check Python version and dependencies

### 2. Import Check

Test all imports work:
```bash
python -c "import alcf_mcp; print('Imports successful')"
```

**Expected**: "Imports successful"
**If errors**: Install missing dependencies

### 3. Basic Function Test

Run the examples script:
```bash
python examples.py
```

**Expected**: Successfully queries ask.alcf.anl.gov and displays responses
**Duration**: 1-3 minutes
**If errors**: Check internet connection and Playwright installation

## Manual Testing

### Test 1: Basic Question Query

**Test Case**: Simple system information query
**Input**:
```python
{
  "question": "What is Aurora?",
  "timeout": 60000,
  "response_format": "markdown"
}
```

**Expected Output**:
- Response contains information about Aurora
- Formatted as Markdown with headers
- Includes source attribution
- Completes within 60 seconds
- No error messages

**Pass Criteria**:
- ✅ Response received
- ✅ Contains relevant information
- ✅ Proper formatting
- ✅ No exceptions raised

### Test 2: Technical Question

**Test Case**: Complex technical query
**Input**:
```python
{
  "question": "How do I compile MPI code on Aurora?",
  "timeout": 90000,
  "response_format": "markdown"
}
```

**Expected Output**:
- Detailed compilation instructions
- Module loading commands
- Compiler flags and options
- Example commands

**Pass Criteria**:
- ✅ Comprehensive response
- ✅ Contains practical guidance
- ✅ No timeout errors

### Test 3: JSON Response Format

**Test Case**: Verify JSON output
**Input**:
```python
{
  "question": "What are the specifications of Polaris?",
  "timeout": 60000,
  "response_format": "json"
}
```

**Expected Output**:
```json
{
  "question": "What are the specifications of Polaris?",
  "answer": "...",
  "source": "ask.alcf.anl.gov",
  "truncated": false
}
```

**Pass Criteria**:
- ✅ Valid JSON format
- ✅ Contains all expected fields
- ✅ Parseable by json.loads()

### Test 4: System Info Tool

**Test Case**: Convenience tool functionality
**Input**:
```python
system_name = "Polaris"
```

**Expected Output**:
- Detailed Polaris information
- Markdown formatted
- Includes specifications and capabilities

**Pass Criteria**:
- ✅ Successfully queries system information
- ✅ Returns formatted response
- ✅ No errors

### Test 5: Timeout Handling

**Test Case**: Short timeout with complex question
**Input**:
```python
{
  "question": "Detailed optimization strategies for Aurora",
  "timeout": 15000,  # Very short timeout
  "response_format": "markdown"
}
```

**Expected Output**:
- Timeout error message
- Actionable guidance to increase timeout
- No crash or exception

**Pass Criteria**:
- ✅ Handles timeout gracefully
- ✅ Returns error message
- ✅ Suggests solution

### Test 6: Invalid Input Validation

**Test Case**: Empty question
**Input**:
```python
{
  "question": "",
  "timeout": 60000
}
```

**Expected Output**:
- Pydantic validation error
- Clear message about empty question
- No query sent to server

**Pass Criteria**:
- ✅ Validation error raised
- ✅ Clear error message
- ✅ No unnecessary network calls

### Test 7: Character Limit

**Test Case**: Query that generates long response
**Input**:
```python
{
  "question": "Explain all ALCF systems in detail",
  "timeout": 120000
}
```

**Expected Output**:
- Response truncated at 25,000 characters
- Truncation notice included
- Still readable and useful

**Pass Criteria**:
- ✅ Response length ≤ 25,000 characters
- ✅ Includes truncation message if applicable
- ✅ Content is useful despite truncation

### Test 8: Multiple Sequential Queries

**Test Case**: Multiple queries in sequence
**Procedure**:
1. Query about Aurora
2. Query about Polaris
3. Query about AI Testbed

**Expected**: All queries succeed independently

**Pass Criteria**:
- ✅ All queries complete successfully
- ✅ No memory leaks
- ✅ Consistent performance
- ✅ Browser properly cleaned up

## Integration Testing

### Test with Claude Desktop

1. **Configure Claude Desktop**
   - Add server to config file
   - Restart Claude Desktop
   - Verify server appears in settings

2. **Test Basic Query**
   - Ask: "What is Aurora?"
   - Verify: Response received and accurate

3. **Test Tool Selection**
   - Ask: "Tell me about Polaris specifications"
   - Verify: Correct tool selected automatically

4. **Test Error Handling**
   - Disconnect internet briefly
   - Ask question
   - Verify: Error message displayed clearly

5. **Test Multiple Tools**
   - Ask questions requiring different tools
   - Verify: Tools work together correctly

## Performance Testing

### Response Time Benchmarks

| Query Type | Expected Time | Acceptable Range |
|------------|---------------|------------------|
| Simple system info | 20-40s | 10-60s |
| Technical question | 30-60s | 20-90s |
| Complex query | 40-90s | 30-120s |
| Very detailed query | 60-120s | 45-180s |

### Memory Usage

Monitor memory during operation:
```bash
# On Linux/Mac
top -p $(pgrep -f ask_alcf_mcp.py)

# Expected: 100-200 MB for Chromium
```

**Pass Criteria**:
- ✅ Memory usage stays below 500 MB
- ✅ No memory leaks over multiple queries
- ✅ Browser processes properly cleaned up

## Error Scenario Testing

### Test E1: Network Disconnection

**Procedure**:
1. Start query
2. Disconnect internet mid-query
3. Observe error handling

**Expected**:
- Connection error detected
- Clear error message
- Suggests checking connectivity

### Test E2: Service Unavailable

**Scenario**: ask.alcf.anl.gov is down
**Expected**:
- Navigation timeout
- Error message suggests trying later
- No crash

### Test E3: Invalid System Name

**Input**: `alcf_get_system_info("InvalidSystem")`
**Expected**:
- Query still sent
- Response indicates system not found or clarification needed

### Test E4: Extremely Long Question

**Input**: Question with 1500 characters
**Expected**:
- Validation error (max 1000 chars)
- Clear message about limit

## Regression Testing

After any code changes, run:

1. ✅ Syntax check
2. ✅ Import verification
3. ✅ Basic query test
4. ✅ JSON format test
5. ✅ Error handling test
6. ✅ Examples script

**All tests must pass before deployment**

## Continuous Testing Checklist

### Daily (if in active development)
- [ ] Run examples.py
- [ ] Test basic query
- [ ] Verify ask.alcf.anl.gov accessibility

### Weekly
- [ ] Full manual test suite
- [ ] Performance benchmarks
- [ ] Error scenario testing
- [ ] Integration test with Claude Desktop

### Before Release
- [ ] Complete test suite
- [ ] All examples work
- [ ] Documentation accuracy verified
- [ ] Performance benchmarks met
- [ ] Error handling verified

## Test Environment Setup

### Minimal Test Environment
```bash
# Create test virtual environment
python -m venv test_env
source test_env/bin/activate  # On Windows: test_env\Scripts\activate

# Install dependencies
pip install -r requirements.txt
playwright install chromium

# Run tests
python examples.py
```

### Docker Test Environment (Optional)

```dockerfile
FROM python:3.11-slim

RUN apt-get update && apt-get install -y \
    wget gnupg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
RUN playwright install chromium
RUN playwright install-deps chromium

COPY . .

CMD ["python", "ask_alcf_mcp.py"]
```

## Debugging Failed Tests

### Debug Mode

Run with verbose output:
```python
# In ask_alcf_mcp.py, temporarily set:
response = await _query_ask_alcf(
    question=params.question,
    timeout=params.timeout,
    headless=False,  # Show browser
    verbose=True     # Print debug info
)
```

### Common Issues

1. **Timeout Errors**
   - Increase timeout value
   - Check internet speed
   - Verify ask.alcf.anl.gov is responsive

2. **Import Errors**
   - Reinstall dependencies
   - Check Python version
   - Verify virtual environment

3. **Playwright Errors**
   - Reinstall browsers: `playwright install chromium`
   - Install system deps: `playwright install-deps chromium`
   - Check disk space

4. **Selector Not Found**
   - ask.alcf.anl.gov structure may have changed
   - Update selectors in code
   - Report issue to maintainers

## Test Reporting

Document test results:

```markdown
## Test Report - [Date]

### Environment
- Python Version: 3.11.5
- Playwright Version: 1.40.0
- OS: Ubuntu 24.04

### Test Results
- ✅ Syntax Check: PASS
- ✅ Basic Query: PASS (32s)
- ✅ JSON Format: PASS
- ✅ Error Handling: PASS
- ✅ System Info Tool: PASS

### Issues Found
None

### Performance
- Average query time: 35s
- Memory usage: 150 MB
- All within acceptable ranges

### Recommendations
All tests passed. Ready for use.
```

## Automated Testing (Future)

Plans for automated test suite:

1. **Unit Tests**: Test individual functions
2. **Integration Tests**: Test tool workflows
3. **End-to-End Tests**: Full query cycle
4. **Performance Tests**: Benchmark response times
5. **CI/CD**: Automated testing on commits

---

**Testing Status**: Manual testing procedures documented
**Last Updated**: October 27, 2025
**Next Review**: As needed for releases
