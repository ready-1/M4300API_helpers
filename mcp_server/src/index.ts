#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';
import { spawn } from 'child_process';
import { join } from 'path';

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

class M4300Server {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'm4300-api-server',
        version: '0.1.0',
      },
      {
        capabilities: {
          tools: {},
        },
      }
    );

    this.setupTools();
  }

  private setupTools() {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => ({
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
        }
      ]
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name !== 'login') {
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
      }

      if (!request.params.arguments) {
        throw new McpError(
          ErrorCode.InvalidParams,
          'Arguments are required'
        );
      }

      const { baseUrl, username, password } = request.params.arguments;

      if (typeof baseUrl !== 'string' || typeof username !== 'string' || typeof password !== 'string') {
        throw new McpError(
          ErrorCode.InvalidParams,
          'Missing required parameters: baseUrl, username, and password are required'
        );
      }

      try {
        const result = await this.executeLoginHelper(baseUrl, username, password);
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
          `Login failed: ${(error as Error).message}`
        );
      }
    });
  }

  private executeLoginHelper(baseUrl: string, username: string, password: string): Promise<LoginResponse> {
    return new Promise((resolve, reject) => {
      const pythonScript = join(__dirname, '../../src/login/login.py');
      const python = spawn('python', [
        '-c',
        `
import sys
sys.path.append('${join(__dirname, '../..')}')
from src.login.login import login
import json

try:
    result = login('${baseUrl}', '${username}', '${password}')
    print(json.dumps(result))
except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1)
        `
      ]);

      let stdout = '';
      let stderr = '';

      python.stdout.on('data', (data) => {
        stdout += data.toString();
      });

      python.stderr.on('data', (data) => {
        stderr += data.toString();
      });

      python.on('close', (code) => {
        if (code !== 0) {
          reject(new Error(stderr.trim() || 'Login helper execution failed'));
          return;
        }

        try {
          const result = JSON.parse(stdout);
          if (result.error) {
            reject(new Error(result.error));
            return;
          }
          resolve(result as LoginResponse);
        } catch (error) {
          reject(new Error('Failed to parse login helper response'));
        }
      });
    });
  }

  async run() {
    try {
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      console.error('M4300 API MCP server running on stdio');
      
      // Keep the process alive
      process.stdin.resume();
      
      // Handle graceful shutdown
      const cleanup = () => {
        console.error('Server shutting down');
        this.server.close().catch(console.error);
      };
      
      process.on('SIGINT', cleanup);
      process.on('SIGTERM', cleanup);
      
    } catch (error) {
      const err = error as Error;
      console.error('Failed to start server:', err.message);
      process.exit(1);
    }
  }
}

const server = new M4300Server();
server.run().catch((error) => {
  const err = error as Error;
  console.error('Server error:', err.message);
  process.exit(1);
});
