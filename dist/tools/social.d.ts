/**
 * Main social tools implementing the CLAUDE.md specification
 */
import { Tool } from '@modelcontextprotocol/sdk/types.js';
export declare class SocialTools {
    private apify;
    private xTools;
    private linkedinTools;
    private resourceStorage;
    constructor();
    /**
     * Define the social.fetch_contexts MCP tool (NEW)
     */
    getFetchContextsToolDefinition(): Tool;
    /**
     * Execute social.fetch_contexts tool
     */
    executeFetchContexts(args: unknown): Promise<string>;
    /**
     * Define the social.suggest_openers MCP tool
     */
    getSuggestOpenersToolDefinition(): Tool;
    /**
     * Execute social.suggest_openers tool
     */
    executeSuggestOpeners(args: unknown): Promise<string>;
    /**
     * Fetch LinkedIn context with optional posts summary
     */
    private fetchLinkedInContext;
    /**
     * Fetch Apollo context (placeholder implementation)
     */
    private fetchApolloContext;
    /**
     * Create combined context from LinkedIn and Apollo data
     */
    private createCombinedContext;
    /**
     * Generate conversation openers based on contexts
     */
    private generateOpeners;
    private generateCasualOpener;
    private generateProfessionalOpener;
    private generatePlayfulOpener;
    /**
     * Get a stored resource by URI
     */
    getResource(uri: string): string | undefined;
    /**
     * List all available resource URIs
     */
    listResources(): string[];
}
//# sourceMappingURL=social.d.ts.map