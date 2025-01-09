#!/bin/bash

# Validate arguments
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <info_doc_path>"
    echo "Example: $0 docs/dev/mcp_info/POST_login_info_doc.txt"
    exit 1
fi

INFO_DOC="$1"

# Validate info doc exists
if [ ! -f "$INFO_DOC" ]; then
    echo "Error: Info doc not found at $INFO_DOC"
    exit 1
fi

# Extract endpoint details
ENDPOINT_LINE=$(grep -m 1 "^[A-Z]\+ /.*" "$INFO_DOC")
if [ -z "$ENDPOINT_LINE" ]; then
    echo "Error: Could not find endpoint definition in info doc"
    exit 1
fi

METHOD=$(echo "$ENDPOINT_LINE" | cut -d' ' -f1)
PATH=$(echo "$ENDPOINT_LINE" | cut -d' ' -f2 | sed 's/^\/api\/v1\///')
BRANCH_NAME="endpoint/$PATH"

# Create and switch to branch
git checkout -b "$BRANCH_NAME"
if [ $? -ne 0 ]; then
    echo "Error: Failed to create branch $BRANCH_NAME"
    exit 1
fi

# Create directory structure
HELPER_DIR="src/helpers/$PATH"
TEST_DIR="tests/helpers/$PATH"

mkdir -p "$HELPER_DIR"
mkdir -p "$TEST_DIR"

# Copy info doc to helper directory
cp "$INFO_DOC" "$HELPER_DIR/endpoint_info.txt"

# Create helper implementation file
cat > "$HELPER_DIR/index.ts" << EOL
import { AxiosInstance } from 'axios';
import { ApiResponse, ErrorResponse } from '../../types';

export interface ${PATH^}Request {
    // TODO: Add request interface based on info doc
}

export interface ${PATH^}Response {
    // TODO: Add response interface based on info doc
}

export async function ${PATH}Helper(
    client: AxiosInstance,
    request: ${PATH^}Request
): Promise<ApiResponse<${PATH^}Response> | ErrorResponse> {
    try {
        // TODO: Implement helper based on info doc
        throw new Error('Not implemented');
    } catch (error) {
        // TODO: Implement error handling
        throw error;
    }
}
EOL

# Create test file
cat > "$TEST_DIR/index.test.ts" << EOL
import { ${PATH}Helper } from '../../../src/helpers/${PATH}';
import { mockAxios } from '../../mocks/axios';

describe('${PATH}Helper', () => {
    it('should handle successful response', async () => {
        // TODO: Add success test based on info doc
    });

    it('should handle error response', async () => {
        // TODO: Add error test based on info doc
    });
});
EOL

# Create documentation file
cat > "$HELPER_DIR/README.md" << EOL
# ${PATH^} Helper

## Overview
Helper function for the ${METHOD} /api/v1/${PATH} endpoint.

## Usage
\`\`\`typescript
import { ${PATH}Helper } from './helpers/${PATH}';

// TODO: Add usage example based on info doc
\`\`\`

## Request Interface
\`\`\`typescript
// TODO: Document request interface
\`\`\`

## Response Interface
\`\`\`typescript
// TODO: Document response interface
\`\`\`

## Error Handling
\`\`\`typescript
// TODO: Document error cases
\`\`\`
EOL

echo "Created endpoint helper structure in branch $BRANCH_NAME"
echo "Next steps:"
echo "1. Parse info doc at $HELPER_DIR/endpoint_info.txt"
echo "2. Implement interfaces and helper function"
echo "3. Add tests"
echo "4. Update documentation"
echo "5. Run validation scripts"
