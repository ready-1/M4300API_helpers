# Task Transition Format

## Overview
This document defines the standard format for transitioning between tasks in the M4300 API Helpers project. This format ensures compliance with OODA workflow and critical validation requirements.

## Task Start Format

```markdown
# Task Context
Task Name: [Brief description]
Branch: [Current git branch]
Previous State: [What was completed]
Next Steps: [What needs to be done]

# OODA Analysis
## OBSERVE
- Current Implementation State:
  * [List relevant files and their states]
  * [Note any known issues or discrepancies]
- Documentation Review:
  * [List relevant documentation reviewed]
  * [Note any documentation gaps]
- Live API State:
  * [Note any API validation results]
  * [List any discrepancies from docs]

## ORIENT
- Architecture Considerations:
  * [How this fits into project architecture]
  * [Impact on other components]
- Dependencies:
  * [Required tools/servers]
  * [Configuration requirements]
  * [Test environment needs]

## DECIDE
- Approach:
  * [Chosen implementation strategy]
  * [Justification for approach]
  * [Considered alternatives]
- Implementation Steps:
  1. [Step-by-step breakdown]
  2. [Include validation points]
  3. [Note critical checkpoints]

## ACT
- Current Action:
  * [Specific tool/command to be used]
  * [Expected outcome]
  * [Validation criteria]

# Validation Requirements
- Critical Rules Checked:
  * [List specific rules validated]
- Validation Scripts:
  * [Status of validate_endpoint.sh]
  * [Status of validate_helper.sh]
- Test Coverage:
  * [Unit test status]
  * [Integration test status]

# Environment State
- Active Branches:
  * [List current git branches]
- Running Services:
  * [List active servers/tools]
- Test Environment:
  * [Status of test switch]
  * [Other test resources]
```

## Usage Guidelines

1. **Start Each Task**:
   - Copy this template
   - Fill out all sections
   - Document any N/A sections

2. **During Task**:
   - Update OODA sections as needed
   - Document all validation results
   - Track any discrepancies found

3. **End Task**:
   - Complete validation checklist
   - Document any remaining issues
   - Update task status

## Critical Requirements

1. **Validation**:
   - Must validate before each tool use
   - Must validate before each command
   - Must validate before each sequence

2. **Documentation**:
   - Document all changes
   - Note any discrepancies
   - Track validation results

3. **Error Handling**:
   - Stop on new issues
   - Document all issues
   - Validate fixes

4. **Scope Control**:
   - Stay focused on current task
   - Keep changes minimal
   - Document scope changes
