/**
 * Apify client adapter for Node.js
 */
import { Post, Platform } from '../models/index.js';
export declare class ApifyAdapter {
    private client;
    constructor();
    /**
     * Fetch X/Twitter posts using Apify Tweet Scraper
     */
    fetchXPosts(handle: string, limit?: number): Promise<Post[]>;
    /**
     * Fetch LinkedIn posts using Apify LinkedIn actor
     */
    fetchLinkedInPosts(profileUrl: string, limit?: number): Promise<Post[]>;
    /**
     * Convert Apify X/Twitter response to normalized Post
     */
    private normalizeXPost;
    /**
     * Convert Apify LinkedIn response to normalized Post
     */
    private normalizeLinkedInPost;
    /**
     * Extract hashtags from text
     */
    private extractHashtags;
    /**
     * Extract mentions from text
     */
    private extractMentions;
    /**
     * Classify and wrap errors with appropriate error types
     */
    private classifyError;
    /**
     * Estimate cost for Apify operations
     */
    estimateCost(platform: Platform, limit: number): {
        cost: number;
        currency: string;
    };
}
//# sourceMappingURL=apify.d.ts.map