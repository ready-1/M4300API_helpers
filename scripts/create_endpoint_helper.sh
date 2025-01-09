#!/bin/bash

# Check for argument
if [ "$#" -ne 1 ]; then
    echo "Error: Missing endpoint name"
    echo "Usage: $0 <endpoint_name>"
    echo "Example: $0 login"
    exit 1
fi

# Create and switch to branch
BRANCH_NAME="endpoint/$1"
if ! git checkout -b "$BRANCH_NAME"; then
    echo "Error: Failed to create branch $BRANCH_NAME"
    exit 1
fi

# Copy template
if ! cp docs/dev/mcp_info/endpoint_doc_template.txt "info_doc_$1.txt"; then
    echo "Error: Failed to copy template"
    exit 1
fi

echo "Success: Created branch $BRANCH_NAME and info doc info_doc_$1.txt"
exit 0
