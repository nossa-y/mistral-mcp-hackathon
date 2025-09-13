/**
 * Simple MCP HTTP Server for Mistral Le Chat integration
 */

import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import express from 'express';
import cors from 'cors';
import pino from 'pino';
import { appConfig, validateConfig } from './config.js';
import { XTools, LinkedInTools, SocialTools } from './tools/index.js';

const logger = pino({ name: 'mcp-server' });

class SimpleMCPServer {
  private server: Server;
  private xTools: XTools;
  private linkedinTools: LinkedInTools;
  private socialTools: SocialTools;

  constructor() {
    this.server = new Server(
      {
        name: appConfig.serverName,
        version: '1.0.0'
      },
      {
        capabilities: {
          tools: {},
          resources: {}
        }
      }
    );

    this.xTools = new XTools();
    this.linkedinTools = new LinkedInTools();
    this.socialTools = new SocialTools();

    this.setupHandlers();
  }

  private setupHandlers(): void {
    // List available tools
    this.server.setRequestHandler(ListToolsRequestSchema, async () => {
      return {
        tools: [
          this.xTools.getToolDefinition(),
          this.linkedinTools.getToolDefinition(),
          this.socialTools.getFetchContextsToolDefinition(),
          this.socialTools.getSuggestOpenersToolDefinition()
        ]
      };
    });

    // Handle tool calls
    this.server.setRequestHandler(CallToolRequestSchema, async (request) => {
      const { name, arguments: args } = request.params;

      try {
        switch (name) {
          case 'get_x_posts':
            const xResult = await this.xTools.execute(args);
            return {
              content: [
                {
                  type: 'text',
                  text: xResult
                }
              ]
            };

          case 'get_linkedin_posts':
            const linkedinResult = await this.linkedinTools.execute(args);
            return {
              content: [
                {
                  type: 'text',
                  text: linkedinResult
                }
              ]
            };

          case 'social.fetch_contexts':
            const contextsResult = await this.socialTools.executeFetchContexts(args);
            return {
              content: [
                {
                  type: 'text',
                  text: contextsResult
                }
              ]
            };

          case 'social.suggest_openers':
            const openersResult = await this.socialTools.executeSuggestOpeners(args);
            return {
              content: [
                {
                  type: 'text',
                  text: openersResult
                }
              ]
            };

          default:
            throw new Error(`Unknown tool: ${name}`);
        }
      } catch (error) {
        logger.error(`Tool execution failed for ${name}:`, error);

        return {
          content: [
            {
              type: 'text',
              text: JSON.stringify({
                error: 'TOOL_EXECUTION_FAILED',
                message: error instanceof Error ? error.message : 'Unknown error',
                tool: name,
                timestamp: new Date().toISOString()
              }, null, 2)
            }
          ],
          isError: true
        };
      }
    });
  }

  /**
   * Run server with stdio transport (for local testing)
   */
  async runStdio(): Promise<void> {
    logger.info('Starting MCP server with stdio transport...');

    const transport = new StdioServerTransport();
    await this.server.connect(transport);

    logger.info('MCP server connected via stdio');
  }

  /**
   * Create HTTP server for Vercel deployment
   */
  createHTTPServer(): express.Application {
    const app = express();

    // Basic middleware
    app.use(cors({
      origin: appConfig.allowedOrigins,
      credentials: true
    }));
    app.use(express.json({ limit: '1mb' }));

    // Health check endpoints
    app.get('/health', (req, res) => {
      res.json({ status: 'ok', timestamp: new Date().toISOString() });
    });

    app.get('/healthz', (req, res) => {
      res.send('OK');
    });

    // MCP endpoints
    app.post('/mcp/tools/list', async (req, res) => {
      try {
        const result = await this.server.request(
          { method: 'tools/list' },
          ListToolsRequestSchema
        );
        res.json(result);
      } catch (error) {
        logger.error('Error listing tools:', error);
        res.status(500).json({ error: 'Internal server error' });
      }
    });

    app.post('/mcp/tools/call', async (req, res) => {
      try {
        const { name, arguments: args } = req.body;

        const result = await this.server.request(
          {
            method: 'tools/call',
            params: { name, arguments: args }
          },
          CallToolRequestSchema
        );

        res.json(result);
      } catch (error) {
        logger.error('Error calling tool:', error);
        res.status(500).json({
          error: 'Tool execution failed',
          message: error instanceof Error ? error.message : 'Unknown error'
        });
      }
    });

    return app;
  }
}

// Main execution
async function main(): Promise<void> {
  try {
    validateConfig();
    logger.info('Configuration validated successfully');

    const mcpServer = new SimpleMCPServer();

    // Check if running in HTTP mode (for Vercel) or stdio mode
    if (process.env.NODE_ENV === 'production' || process.argv.includes('--http')) {
      const app = mcpServer.createHTTPServer();
      const port = appConfig.port;

      app.listen(port, appConfig.host, () => {
        logger.info(`MCP HTTP server listening on ${appConfig.host}:${port}`);
        logger.info(`Health check: http://${appConfig.host}:${port}/health`);
        logger.info(`MCP endpoints: http://${appConfig.host}:${port}/mcp/`);
      });
    } else {
      // Default stdio mode for local testing
      await mcpServer.runStdio();
    }

  } catch (error) {
    logger.error('Failed to start MCP server:', error);
    process.exit(1);
  }
}

// Handle process signals
process.on('SIGINT', () => {
  logger.info('Received SIGINT, shutting down gracefully...');
  process.exit(0);
});

process.on('SIGTERM', () => {
  logger.info('Received SIGTERM, shutting down gracefully...');
  process.exit(0);
});

// Start the server
if (import.meta.url === `file://${process.argv[1]}`) {
  main().catch(error => {
    logger.error('Unhandled error:', error);
    process.exit(1);
  });
}

export { SimpleMCPServer };