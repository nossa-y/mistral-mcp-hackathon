/**
 * X/Twitter specific MCP tools
 */
import { Tool } from '@modelcontextprotocol/sdk/types.js';
export declare class XTools {
    private apify;
    constructor();
    /**
     * Define the get_x_posts MCP tool
     */
    getToolDefinition(): Tool;
    /**
     * Execute the get_x_posts tool
     */
    execute(args: unknown): Promise<string>;
}
//# sourceMappingURL=x-tools.d.ts.map