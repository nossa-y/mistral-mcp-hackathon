/**
 * LinkedIn specific MCP tools
 */
import { Tool } from '@modelcontextprotocol/sdk/types.js';
export declare class LinkedInTools {
    private apify;
    constructor();
    /**
     * Define the get_linkedin_posts MCP tool
     */
    getToolDefinition(): Tool;
    /**
     * Execute the get_linkedin_posts tool
     */
    execute(args: unknown): Promise<string>;
    /**
     * Validate LinkedIn profile URL
     */
    private isValidLinkedInUrl;
    /**
     * Extract profile name from LinkedIn URL
     */
    private extractProfileName;
}
//# sourceMappingURL=linkedin-tools.d.ts.map