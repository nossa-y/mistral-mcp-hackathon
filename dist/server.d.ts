/**
 * Simple MCP HTTP Server for Mistral Le Chat integration
 */
import express from 'express';
declare class SimpleMCPServer {
    private server;
    private xTools;
    private linkedinTools;
    private socialTools;
    constructor();
    private setupHandlers;
    /**
     * Run server with stdio transport (for local testing)
     */
    runStdio(): Promise<void>;
    /**
     * Create HTTP server for Vercel deployment
     */
    createHTTPServer(): express.Application;
}
export { SimpleMCPServer };
//# sourceMappingURL=server.d.ts.map