/**
 * Apify client adapter for Node.js
 */

import { ApifyClient } from 'apify-client';
import pino from 'pino';
import { appConfig } from '../config.js';
import { Post, Platform, ErrorType } from '../models/index.js';

const logger = pino({ name: 'apify-adapter' });

export class ApifyAdapter {
  private client: ApifyClient;

  constructor() {
    if (!appConfig.apifyToken) {
      throw new Error("APIFY_TOKEN is required");
    }
    this.client = new ApifyClient({ token: appConfig.apifyToken });
  }

  /**
   * Fetch X/Twitter posts using Apify Tweet Scraper
   */
  async fetchXPosts(handle: string, limit: number = 20): Promise<Post[]> {
    const cleanHandle = handle.replace('@', '');

    try {
      logger.info(`Fetching ${limit} X posts for @${cleanHandle}`);

      const input = {
        handles: [cleanHandle],
        tweetsPerQuery: limit,
        includeReplies: false,
        includeRetweets: false
      };

      const run = await this.client.actor(appConfig.apifyTwitterActor).call(input);

      if (!run.defaultDatasetId) {
        throw new Error("No dataset returned from Apify run");
      }

      const dataset = this.client.dataset(run.defaultDatasetId);
      const { items } = await dataset.listItems();

      if (!items || items.length === 0) {
        throw new Error(`No posts found for @${cleanHandle}`);
      }

      const posts = items.map(item => this.normalizeXPost(item as any, cleanHandle));

      logger.info(`Successfully fetched ${posts.length} X posts for @${cleanHandle}`);
      return posts;

    } catch (error) {
      logger.error(`Failed to fetch X posts for @${cleanHandle}:`, error);
      throw this.classifyError(error as Error);
    }
  }

  /**
   * Fetch LinkedIn posts using Apify LinkedIn actor
   */
  async fetchLinkedInPosts(profileUrl: string, limit: number = 10): Promise<Post[]> {
    try {
      logger.info(`Fetching ${limit} LinkedIn posts for ${profileUrl}`);

      const input = {
        profileUrl: profileUrl,
        postsCount: limit
      };

      const run = await this.client.actor(appConfig.apifyLinkedInPostsActor).call(input);

      if (!run.defaultDatasetId) {
        throw new Error("No dataset returned from Apify run");
      }

      const dataset = this.client.dataset(run.defaultDatasetId);
      const { items } = await dataset.listItems();

      if (!items || items.length === 0) {
        throw new Error(`No posts found for LinkedIn profile: ${profileUrl}`);
      }

      const posts = items.map(item => this.normalizeLinkedInPost(item as any, profileUrl));

      logger.info(`Successfully fetched ${posts.length} LinkedIn posts`);
      return posts;

    } catch (error) {
      logger.error(`Failed to fetch LinkedIn posts for ${profileUrl}:`, error);
      throw this.classifyError(error as Error);
    }
  }

  /**
   * Convert Apify X/Twitter response to normalized Post
   */
  private normalizeXPost(item: any, handle: string): Post {
    const postId = String(item.id || '');
    const url = item.url || `https://twitter.com/${handle}/status/${postId}`;
    const text = item.text || '';
    let createdAt = item.createdAt || '';

    // Handle date normalization
    if (createdAt && !createdAt.endsWith('Z')) {
      try {
        const date = new Date(createdAt.replace('Z', '+00:00'));
        createdAt = date.toISOString();
      } catch (error) {
        createdAt = new Date().toISOString();
      }
    }

    // Extract hashtags and mentions
    const hashtags: string[] = [];
    const mentions: string[] = [];

    const entities = item.entities || {};
    if (entities.hashtags) {
      hashtags.push(...entities.hashtags.map((tag: any) => tag.text || ''));
    }
    if (entities.user_mentions) {
      mentions.push(...entities.user_mentions.map((mention: any) => mention.screen_name || ''));
    }

    // Extract engagement metrics
    const engagement: Record<string, number> = {
      likes: item.likeCount || 0,
      retweets: item.retweetCount || 0,
      replies: item.replyCount || 0,
      quotes: item.quoteCount || 0
    };

    return {
      platform: Platform.X,
      post_id: postId,
      url,
      created_at_iso: createdAt,
      text,
      hashtags,
      mentions,
      engagement,
      inferred_themes: []
    };
  }

  /**
   * Convert Apify LinkedIn response to normalized Post
   */
  private normalizeLinkedInPost(item: any, profileUrl: string): Post {
    const postId = String(item.id || item.urn || '');
    const url = item.url || item.permalink || '';
    const text = item.text || item.commentary || '';
    let createdAt = item.createdAt || item.publishedAt || '';

    // Handle date normalization
    if (createdAt) {
      try {
        const date = new Date(createdAt);
        createdAt = date.toISOString();
      } catch (error) {
        createdAt = new Date().toISOString();
      }
    }

    // Extract hashtags from text
    const hashtags = this.extractHashtags(text);
    const mentions = this.extractMentions(text);

    // Extract engagement metrics
    const engagement: Record<string, number> = {
      likes: item.likeCount || item.reactions?.total || 0,
      comments: item.commentCount || 0,
      shares: item.shareCount || item.reposts || 0
    };

    return {
      platform: Platform.LINKEDIN,
      post_id: postId,
      url,
      created_at_iso: createdAt,
      text,
      hashtags,
      mentions,
      engagement,
      inferred_themes: []
    };
  }

  /**
   * Extract hashtags from text
   */
  private extractHashtags(text: string): string[] {
    const hashtagRegex = /#[\w\u0100-\u017f]+/gi;
    const matches = text.match(hashtagRegex) || [];
    return matches.map(tag => tag.replace('#', ''));
  }

  /**
   * Extract mentions from text
   */
  private extractMentions(text: string): string[] {
    const mentionRegex = /@[\w\u0100-\u017f]+/gi;
    const matches = text.match(mentionRegex) || [];
    return matches.map(mention => mention.replace('@', ''));
  }

  /**
   * Classify and wrap errors with appropriate error types
   */
  private classifyError(error: Error): Error {
    const message = error.message.toLowerCase();
    let errorType: ErrorType;

    if (message.includes('rate limit')) {
      errorType = ErrorType.RATE_LIMITED;
    } else if (message.includes('private') || message.includes('protected')) {
      errorType = ErrorType.PRIVATE_PROFILE;
    } else if (message.includes('not found')) {
      errorType = ErrorType.NOT_FOUND;
    } else if (message.includes('actor run failed')) {
      errorType = ErrorType.APIFY_RUN_ERROR;
    } else {
      errorType = ErrorType.API_ERROR;
    }

    const wrappedError = new Error(`${errorType}: ${error.message}`);
    wrappedError.name = errorType;
    return wrappedError;
  }

  /**
   * Estimate cost for Apify operations
   */
  estimateCost(platform: Platform, limit: number): { cost: number; currency: string } {
    // Rough estimates based on Apify pricing
    const costPerThousand = platform === Platform.X ? 0.40 : 0.30;
    const cost = (limit / 1000) * costPerThousand;

    return {
      cost: Math.round(cost * 100) / 100, // Round to 2 decimal places
      currency: 'USD'
    };
  }
}