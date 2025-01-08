# Architectural Document for Python API Helpers Library

## Overview

This library provides a Python interface for accessing the management API of Netgear switches. It is designed for integration with management front ends, primarily as the API interface for a Django application. The library supports synchronous operations and provides modular functionality with centralized token management.

---

## Key Features

1. **Modular Structure**
   - Centralized token management.
   - Separate modules for different functional areas (e.g., diagnostics, configuration).

2. **Authentication**
   - Basic username/password authentication.
   - Bearer Token-based API access.
   - Tokens managed in memory for the session duration.

3. **Error Handling**
   - Basic error handling for API responses.
   - Centralized API call function to maintain DRY principles.

4. **Configuration**
   - Primary settings in `config.py`.
   - Debug level tied to an environment variable for `development`, `test`, and `production` states.
   - Consuming applications provide switch credentials and hostnames.

5. **Logging**
   - Controlled by an environment variable.
   - Logs include:
     - Request and response details.
     - Token lifecycle events.

6. **Response Handling**
   - Converts API responses to Python dictionaries.
   - Processes JSON responses to extract relevant data, reducing workload for consuming applications.

7. **Endpoint Definitions**
   - Static endpoint definitions sourced from a YAML file.
   - Includes parameter validation for API requests.

---

## Library Structure

```plaintext
api_helpers/
│
├── __init__.py        # Initialization and top-level imports
├── auth.py            # Centralized authentication and token management
├── config.py          # Configuration settings
├── api_core.py        # Centralized API call functions
├── diagnostics.py     # Diagnostics-related API operations
├── configuration.py   # Configuration management operations
├── utils.py           # Shared utilities (e.g., validation, logging)
├── tests/             # Unit tests for library modules
└── endpoints.yaml     # YAML file with static endpoint definitions