#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { spawnSync } from 'child_process';
import { resolve, dirname } from 'path';
import { fileURLToPath } from 'url';

const __filename = fileURLToPath(import.meta.url);
const __dirname = dirname(__filename);

interface LoginParams {
  baseUrl: string;
  username: string;
  password: string;
}

interface LoginResponse {
  login: {
    token: string;
    expire: string;
  };
  resp: {
    status: string;
    respCode: number;
    respMsg: string;
  };
}

const server = new Server(
  {
    name: 'm4300',
    version: '0.1.0',
  },
  {
    capabilities: {
      tools: {},
    },
  }
);

// Store root directory for Python imports
const rootDir = resolve(__dirname, '../..');

// List available tools
server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: [
    {
      name: 'login',
      description: 'Login to device and obtain authentication token',
      inputSchema: {
        type: 'object',
        properties: {
          baseUrl: {
            type: 'string',
            description: 'Base URL of the API (e.g., https://192.168.99.92:8443)'
          },
          username: {
            type: 'string',
            description: 'Admin username'
          },
          password: {
            type: 'string',
            description: 'Admin user\'s password'
          }
        },
        required: ['baseUrl', 'username', 'password']
      }
    },
    {
      name: 'logout',
      description: 'Logout from device and invalidate authentication token',
      inputSchema: {
        type: 'object',
        properties: {
          baseUrl: {
            type: 'string',
            description: 'Base URL of the API (e.g., https://192.168.99.92:8443)'
          },
          token: {
            type: 'string',
            description: 'Authentication token from login'
          }
        },
        required: ['baseUrl', 'token']
      }
    }
  ]
}));

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  if (!request.params.arguments) {
    throw new McpError(
      ErrorCode.InvalidParams,
      'Arguments are required'
    );
  }

  if (request.params.name === 'login') {
    const { baseUrl, username, password } = request.params.arguments;

    if (typeof baseUrl !== 'string' || typeof username !== 'string' || typeof password !== 'string') {
      throw new McpError(
        ErrorCode.InvalidParams,
        'Missing required parameters: baseUrl, username, and password are required'
      );
    }

    try {
      const pythonCode = `
import sys
sys.path.append('${rootDir}')
from src.login.login import login
import json

try:
    result = login('${baseUrl}', '${username}', '${password}')
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1)
      `;

      const python = spawnSync('python', ['-c', pythonCode], {
        encoding: 'utf-8',
        cwd: rootDir
      });

      if (python.status !== 0) {
        throw new McpError(
          ErrorCode.InternalError,
          python.stderr || 'Login helper execution failed'
        );
      }

      try {
        const result = JSON.parse(python.stdout);
        if (result.error) {
          throw new McpError(
            ErrorCode.InternalError,
            result.error
          );
        }
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          'Failed to parse login helper response'
        );
      }
    } catch (error) {
      if (error instanceof McpError) {
        throw error;
      }
      throw new McpError(
        ErrorCode.InternalError,
        `Login failed: ${(error as Error).message}`
      );
    }
  } else if (request.params.name === 'logout') {
    const { baseUrl, token } = request.params.arguments;

    if (typeof baseUrl !== 'string' || typeof token !== 'string') {
      throw new McpError(
        ErrorCode.InvalidParams,
        'Missing required parameters: baseUrl and token are required'
      );
    }

    try {
      const pythonCode = `
import sys
sys.path.append('${rootDir}')
from src.logout.logout import logout
import json

try:
    result = logout('${baseUrl}', '${token}')
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1)
      `;

      const python = spawnSync('python', ['-c', pythonCode], {
        encoding: 'utf-8',
        cwd: rootDir
      });

      if (python.status !== 0) {
        throw new McpError(
          ErrorCode.InternalError,
          python.stderr || 'Logout helper execution failed'
        );
      }

      try {
        const result = JSON.parse(python.stdout);
        if (result.error) {
          throw new McpError(
            ErrorCode.InternalError,
            result.error
          );
        }
        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify(result, null, 2)
            }
          ]
        };
      } catch (error) {
        throw new McpError(
          ErrorCode.InternalError,
          'Failed to parse logout helper response'
        );
      }
    } catch (error) {
      if (error instanceof McpError) {
        throw error;
      }
      throw new McpError(
        ErrorCode.InternalError,
        `Logout failed: ${(error as Error).message}`
      );
    }
  } else {
    throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
  }
});

// Connect server to stdio transport
const transport = new StdioServerTransport();
server.connect(transport).catch((error) => {
  console.error('Server error:', error);
  process.exit(1);
});
