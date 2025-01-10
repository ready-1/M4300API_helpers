# New Endpoint Helper Creation

## Request Format
```
Create new endpoint helper using [info_doc_path]
```

Example:
```
Create new endpoint helper using docs/dev/mcp_info/POST_login_info_doc.txt
```

## Automated Setup
The `create_endpoint_helper.sh` script will:
1. Create properly named branch (e.g., endpoint/login)
2. Set up directory structure
3. Create template files:
   - Helper implementation (index.ts)
   - Tests (index.test.ts)
   - Documentation (README.md)
   - Copy info doc for reference

## Implementation Steps
After script execution:

1. **Parse Info Document**
   - Review endpoint_info.txt in helper directory
   - Extract interfaces and types
   - Document request/response formats
   - Note error cases and handling

2. **Implementation**
   - Complete helper function
   - Add error handling
   - Implement tests
   - Update documentation

3. **Validation**
   - Run validate_endpoint.sh
   - Run validate_helper.sh
   - Fix any warnings
   - Test with live API

## Information Document Format
```
==== ENDPOINT ====
# endpoint Method and URL
# example "POST /api/v1/login"

==== PDF DOCUMENTATION ====
# oficial documentation of the endpoint with
# Method
# URL
# Headers
# Parameters
# Request Body
# Response Format
# Valid Values

==== WORKING PYTHON CODE FROM POSTMAN ====
'''
# sample python code

'''

==== ACTUAL LIVE RESPONSE FROM POSTMAN FOR THE ABOVE CODE ====
Status: HTTP 1.1 200 OK
'''
# sample json response


```

## Parsing Instructions
1. Headers:
   - Extract all required headers
   - Note any conditional headers
   - Document header format requirements

2. Parameters:
   - List all query parameters
   - Document parameter types
   - Note required vs optional
   - Include validation rules

3. Request Body:
   - Parse full payload structure
   - Document field requirements
   - Note data type constraints
   - Include example values

4. Response Format:
   - Document success response structure
   - Note field types and formats
   - Include conditional fields
   - Document metadata if present

5. Error Cases:
   - List all possible error codes
   - Document error response formats
   - Include trigger conditions
   - Note recovery steps

6. Documentation References:
   - Extract PDF section numbers
   - Note relevant page ranges
   - Link to Postman examples
   - Document any special cases

## Validation Checklist
- [ ] Branch name follows convention
- [ ] Documentation complete
- [ ] Tests written
- [ ] Live API validated
- [ ] Error handling implemented
- [ ] Helper interface documented
- [ ] All validation scripts pass

## Notes
- Follow one branch per endpoint rule
- Document all key decisions
- Handle all error cases
- Maintain type safety
- Update examples
