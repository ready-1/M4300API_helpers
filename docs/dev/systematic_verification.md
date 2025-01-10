# Systematic Verification Method

A structured approach to verify functionality and diagnose issues, designed to prevent cascading failures from incorrect assumptions.

## Core Principles

1. Verify behavior before investigating syntax
2. Test actual operations before trusting display output
3. Work from data structures to functionality to error messages
4. Use Python's type system and operations for verification

## Verification Steps

### 1. Structure Verification
```python
# Always verify the actual data structure first
d = get_config()
assert isinstance(d, dict)
assert set(d.keys()) == expected_keys
assert all(isinstance(v, expected_type) for v in d.values())
```

### 2. Behavior Verification
```python
# Test actual operations and functionality
assert d['key'].startswith('expected')
assert json.dumps(d)  # Verify serialization
assert len(list(d.items())) == expected_length
```

### 3. Function Verification
```python
# Test the actual function behavior
result = function(arg1, arg2)
assert 'expected_key' in result
assert isinstance(result['key'], expected_type)
assert result['status'] == expected_status
```

### 4. Error Handling Verification
```python
# Test error conditions and messages
try:
    function(invalid_input)
except Exception as e:
    assert isinstance(e, expected_error_type)
    assert str(e).startswith(expected_message)
```

### 5. API/External System Verification
```python
# Test raw API responses if needed
response = requests.post(url, headers=headers)
print(f'Status: {response.status_code}')
print(f'Headers: {dict(response.headers)}')
print(f'Body: {response.text}')
```

## Common Pitfalls to Avoid

1. **Display Trust**
   - Don't assume error message formatting reflects actual data structure
   - Verify actual operations instead of trusting string representations
   - Use type checking and operations to confirm structure

2. **Cascading Fixes**
   - Don't make changes based solely on how data looks
   - Verify the actual issue exists in behavior
   - Test each fix independently

3. **Assumption Propagation**
   - Don't let one incorrect assumption lead to multiple invalid fixes
   - Re-verify assumptions when behavior doesn't match expectations
   - Use systematic verification before making changes

## Example Application

### Problem: Dictionary appears to have syntax issues
```python
# Instead of immediately fixing "missing" commas:

# 1. Verify Structure
d = get_config()
print(f'Is dict: {isinstance(d, dict)}')
print(f'Has keys: {set(d.keys()) == expected_keys}')

# 2. Verify Behavior
print(f'Can access: {d["key"] == expected_value}')
print(f'Can iterate: {len(list(d.items())) == expected_length}')

# 3. Verify Function
result = function(d)
print(f'Function works: {result["status"] == "success"}')

# 4. Verify Errors
try:
    function(invalid_input)
except Exception as e:
    print(f'Error type: {type(e).__name__}')
    print(f'Error message: {str(e)}')

# 5. Verify External System
response = requests.get(url)
print(f'Raw response: {response.text}')
```

## Benefits

1. Prevents cascading failures from incorrect assumptions
2. Identifies actual issues versus display artifacts
3. Provides clear evidence for root cause analysis
4. Creates reproducible verification steps
5. Separates behavior from appearance

## M4300 API Response Format

### Important: Response Format Display vs Reality

The M4300 API returns responses that may appear malformed in test output but are actually valid:

```python
# What you see in test output (appears to have missing commas):
{
    "login":    {
        "token":    "abc123"
        "expire":   "86400"     # No comma!
    }                          # No comma!
    "resp": {
        "status":   "success"   # No comma!
        "respCode": 0           # No comma!
        "respMsg":  "Operation success"
    }
}

# What Python actually sees (valid JSON):
{
    "login": {
        "token": "abc123",
        "expire": "86400"
    },
    "resp": {
        "status": "success",
        "respCode": 0,
        "respMsg": "Operation success"
    }
}
```

### Key Points

1. DO NOT attempt to "fix" missing commas in test output
   - This is a display artifact only
   - Python's json parser handles the format correctly
   - The actual JSON structure is valid

2. Verify using operations, not appearance:
   ```python
   # Good - Verify structure and operations
   response = api_call()
   assert isinstance(response, dict)
   assert "resp" in response
   assert response["resp"]["status"] == "success"

   # Bad - Don't try to fix format based on how it looks
   # response_text = response_text.replace("}\n", "},\n")  # DON'T DO THIS
   ```

3. Trust the verification steps:
   - If json.loads() succeeds, the JSON is valid
   - If dict operations work, the structure is correct
   - If tests pass, don't "fix" display artifacts

## Implementation

1. Use this document as a checklist for issue investigation
2. Follow steps in order - don't skip verification levels
3. Document findings at each step
4. Only proceed with fixes after full verification
5. Add new verification steps based on lessons learned
