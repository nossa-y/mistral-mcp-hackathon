/**
 * LinkedIn specific MCP tools
 */
import pino from 'pino';
import { ApifyAdapter } from '../adapters/index.js';
import { Platform } from '../models/index.js';
import { ThemeInferenceEngine, NormalizationUtils } from '../utils/index.js';
import { z } from 'zod';
const logger = pino({ name: 'linkedin-tools' });
const LinkedInInputSchema = z.object({
    profile_url: z.string().url().describe('LinkedIn profile URL'),
    limit: z.number().min(1).max(50).default(10).describe('Number of posts to fetch')
});
export class LinkedInTools {
    apify;
    constructor() {
        this.apify = new ApifyAdapter();
    }
    /**
     * Define the get_linkedin_posts MCP tool
     */
    getToolDefinition() {
        return {
            name: 'get_linkedin_posts',
            description: 'Fetch recent posts from LinkedIn using Apify scraper',
            inputSchema: {
                type: 'object',
                properties: {
                    profile_url: {
                        type: 'string',
                        format: 'uri',
                        description: 'LinkedIn profile URL'
                    },
                    limit: {
                        type: 'number',
                        description: 'Maximum number of posts to fetch',
                        minimum: 1,
                        maximum: 50,
                        default: 10
                    }
                },
                required: ['profile_url']
            }
        };
    }
    /**
     * Execute the get_linkedin_posts tool
     */
    async execute(args) {
        try {
            // Validate input
            const input = LinkedInInputSchema.parse(args);
            const { profile_url, limit = 10 } = input;
            logger.info(`Fetching ${limit} LinkedIn posts for ${profile_url}`);
            // Show compliance warning
            const warning = "LinkedIn scraping may violate ToS. Ensure you have explicit consent and provide your own authentication cookies if required.";
            logger.warn(warning);
            // Estimate cost
            const costEstimate = this.apify.estimateCost(Platform.LINKEDIN, limit);
            logger.info(`Estimated cost: $${costEstimate.cost} ${costEstimate.currency}`);
            // Fetch posts from Apify
            const rawPosts = await this.apify.fetchLinkedInPosts(profile_url, limit);
            if (rawPosts.length === 0) {
                throw new Error('NOT_FOUND: No recent posts found for this LinkedIn profile');
            }
            // Normalize posts
            const posts = rawPosts.map(post => NormalizationUtils.normalizePost(post));
            // Apply theme inference
            ThemeInferenceEngine.inferThemesBulk(posts);
            // Extract name from profile URL
            const profileMatch = profile_url.match(/linkedin\.com\/in\/([^\/]+)/);
            const profileHandle = profileMatch ? profileMatch[1] : 'unknown';
            // Create person object
            const person = {
                name: profileHandle || 'LinkedIn User',
                platform: Platform.LINKEDIN,
                profile_url,
                headline_or_bio: ''
            };
            // Create metadata
            const meta = {
                source: 'social-snapshot-hub',
                fetched_at_iso: new Date().toISOString(),
                limit,
                total_found: posts.length
            };
            // Create bundle
            const bundle = {
                person,
                posts,
                meta
            };
            const result = {
                ...bundle,
                warnings: [warning]
            };
            logger.info(`Successfully fetched ${posts.length} LinkedIn posts`);
            return JSON.stringify(result, null, 2);
        }
        catch (error) {
            logger.error('Error in get_linkedin_posts:', error);
            // Handle specific LinkedIn errors
            let errorType = 'API_ERROR';
            let message = 'An unexpected error occurred';
            if (error instanceof Error) {
                message = error.message;
                if (message.includes('cookie') || message.includes('authentication')) {
                    errorType = 'COOKIE_EXPIRED';
                    message = 'LinkedIn authentication failed. Please provide valid li_at cookie.';
                }
                else if (message.includes('private') || message.includes('protected')) {
                    errorType = 'PRIVATE_PROFILE';
                }
                else if (message.includes('not found')) {
                    errorType = 'NOT_FOUND';
                }
            }
            return JSON.stringify({
                error: errorType,
                message,
                timestamp: new Date().toISOString(),
                remediation: errorType === 'COOKIE_EXPIRED'
                    ? 'Set LINKEDIN_COOKIE environment variable with valid li_at cookie'
                    : 'Check profile URL and try again'
            }, null, 2);
        }
    }
    /**
     * Validate LinkedIn profile URL
     */
    isValidLinkedInUrl(url) {
        const linkedInUrlPattern = /^https:\/\/(www\.)?linkedin\.com\/in\/[a-zA-Z0-9-]+\/?$/;
        return linkedInUrlPattern.test(url);
    }
    /**
     * Extract profile name from LinkedIn URL
     */
    extractProfileName(url) {
        const match = url.match(/linkedin\.com\/in\/([^\/]+)/);
        return match?.[1]?.replace(/-/g, ' ') ?? 'LinkedIn User';
    }
}
//# sourceMappingURL=linkedin-tools.js.map