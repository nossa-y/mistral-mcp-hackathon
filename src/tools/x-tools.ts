/**
 * X/Twitter specific MCP tools
 */

import { Tool } from '@modelcontextprotocol/sdk/types.js';
import pino from 'pino';
import { ApifyAdapter } from '../adapters/index.js';
import { Bundle, Person, Meta, Platform, GetPostsInputSchema } from '../models/index.js';
import { ThemeInferenceEngine, NormalizationUtils } from '../utils/index.js';
import { appConfig } from '../config.js';

const logger = pino({ name: 'x-tools' });

export class XTools {
  private apify: ApifyAdapter;

  constructor() {
    this.apify = new ApifyAdapter();
  }

  /**
   * Define the get_x_posts MCP tool
   */
  getToolDefinition(): Tool {
    return {
      name: 'get_x_posts',
      description: 'Fetch recent posts from X/Twitter using Apify scraper',
      inputSchema: {
        type: 'object',
        properties: {
          handle: {
            type: 'string',
            description: 'Twitter handle (without @)'
          },
          limit: {
            type: 'number',
            description: 'Maximum number of posts to fetch',
            minimum: 1,
            maximum: 100,
            default: 20
          }
        },
        required: ['handle']
      }
    };
  }

  /**
   * Execute the get_x_posts tool
   */
  async execute(args: unknown): Promise<string> {
    try {
      // Validate input
      const input = GetPostsInputSchema.parse(args);
      const { handle, limit = 20 } = input;

      const cleanHandle = handle.replace('@', '').trim();

      if (!cleanHandle) {
        throw new Error('INVALID_INPUT: Handle cannot be empty');
      }

      logger.info(`Fetching ${limit} X posts for @${cleanHandle}`);

      // Estimate cost
      const costEstimate = this.apify.estimateCost(Platform.X, limit);
      logger.info(`Estimated cost: $${costEstimate.cost} ${costEstimate.currency}`);

      // Fetch posts from Apify
      const rawPosts = await this.apify.fetchXPosts(cleanHandle, limit);

      if (rawPosts.length === 0) {
        throw new Error('NOT_FOUND: No recent posts found');
      }

      // Normalize posts
      const posts = rawPosts.map(post => NormalizationUtils.normalizePost(post));

      // Apply theme inference
      ThemeInferenceEngine.inferThemesBulk(posts);

      // Create person object
      const person: Person = {
        name: `@${cleanHandle}`,
        platform: Platform.X,
        handle: cleanHandle,
        profile_url: `https://twitter.com/${cleanHandle}`,
        headline_or_bio: ''
      };

      // Create metadata
      const meta: Meta = {
        source: 'social-snapshot-hub',
        fetched_at_iso: new Date().toISOString(),
        limit,
        total_found: posts.length
      };

      // Create bundle
      const bundle: Bundle = {
        person,
        posts,
        meta
      };

      logger.info(`Successfully fetched ${posts.length} X posts for @${cleanHandle}`);

      return JSON.stringify(bundle, null, 2);

    } catch (error) {
      logger.error('Error in get_x_posts:', error);

      if (error instanceof Error) {
        return JSON.stringify({
          error: error.name || 'API_ERROR',
          message: error.message,
          timestamp: new Date().toISOString()
        }, null, 2);
      }

      return JSON.stringify({
        error: 'UNKNOWN_ERROR',
        message: 'An unexpected error occurred',
        timestamp: new Date().toISOString()
      }, null, 2);
    }
  }
}