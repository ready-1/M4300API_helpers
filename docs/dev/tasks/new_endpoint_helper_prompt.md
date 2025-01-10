# New Endpoint Helper Creation Prompt

Use this prompt template to request creation of a new endpoint helper:

```
Please create a new endpoint helper based on the following:

1. Info Doc:
docs/dev/mcp_info/[info doc filename]

2. Current Branch:
[Name of feature branch you've created and checked out]

3. Endpoint:
[Endpoint path, e.g., "/device_info"]

Please follow these requirements:
- Use make_api_call and build_switch_url helpers according to docs/dev/components/using_make_api_call.md
- Follow architecture guidelines in docs/dev/architecture.md
- Implement systematic verification from docs/dev/systematic_verification.md
- Create both implementation and tests
- Follow endpoint helper structure from existing examples
- Include comprehensive error handling
- Add type hints and documentation
- Ensure all pre-commit hooks pass

The implementation should include:
1. Helper module with proper structure
2. Unit tests with mocked responses
3. Integration tests with real API calls
4. README.md with usage examples
5. Type definitions for request/response data
6. Error handling for all cases
7. Documentation following project standards

Please proceed step by step, waiting for confirmation after each file creation or modification.
```

## Example Usage

```
Please create a new endpoint helper based on the following:

1. Info Doc:
docs/dev/mcp_info/info_dog_GET_device_info.txt

2. Current Branch:
endpoint/device_info

3. Endpoint:
/device_info

[Rest of requirements as above...]
```

## Expected Implementation Steps

The assistant will:

1. Analyze Requirements
   - Read info doc from specified file
   - Identify request/response patterns
   - Note error cases
   - Plan implementation approach

2. Create Type Definitions
   - Define response TypedDict
   - Add request type hints
   - Document type structures

3. Implement Helper
   - Create helper module
   - Use make_api_call pattern
   - Add error handling
   - Include documentation

4. Add Tests
   - Create unit tests
   - Add integration tests
   - Mock responses
   - Test error cases

5. Add Documentation
   - Create README
   - Add usage examples
   - Document error handling
   - Include type information

6. Verify Implementation
   - Run pre-commit hooks
   - Fix any issues
   - Commit changes
   - Run tests

The assistant will wait for confirmation after each step before proceeding.

## Validation Checklist

The assistant will validate:

1. Code Structure
   - Proper module organization
   - Clear separation of concerns
   - Consistent naming
   - Type safety

2. Error Handling
   - All error cases covered
   - Clear error messages
   - Proper error propagation
   - Response validation

3. Testing
   - Unit test coverage
   - Integration tests
   - Error case testing
   - Mock responses

4. Documentation
   - Clear usage examples
   - Error documentation
   - Type information
   - Response format

5. Quality Checks
   - Pre-commit hooks pass
   - Type checking passes
   - Tests pass
   - Documentation complete

## Response Format

The assistant will:
1. Think through requirements
2. Propose next step
3. Execute step with appropriate tool
4. Wait for confirmation
5. Proceed to next step

Each step will be clearly documented and validated against project requirements.
