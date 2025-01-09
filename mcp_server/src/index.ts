#!/usr/bin/env node
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import {
  CallToolRequestSchema,
  ErrorCode,
  ListToolsRequestSchema,
  McpError,
} from '@modelcontextprotocol/sdk/types.js';

class HelloWorldServer {
  private server: Server;

  constructor() {
    this.server = new Server(
      {
        name: 'm4300-mcp-server',
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
          name: 'hello',
          description: 'Say hello',
          inputSchema: {
            type: 'object',
            properties: {
              name: {
                type: 'string',
                description: 'Name to greet',
                default: 'world'
              }
            }
          }
        }
      ]
    }));

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      if (request.params.name !== 'hello') {
        throw new McpError(ErrorCode.MethodNotFound, `Unknown tool: ${request.params.name}`);
      }

      const name = request.params.arguments?.name || 'world';
      
      return {
        content: [
          {
            type: 'text',
            text: `Hello, ${name}!`
          }
        ]
      };
    });
  }

  async run() {
    try {
      const transport = new StdioServerTransport();
      await this.server.connect(transport);
      console.error('Hello World MCP server running on stdio');
      
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

const server = new HelloWorldServer();
server.run().catch((error) => {
  const err = error as Error;
  console.error('Server error:', err.message);
  process.exit(1);
});
