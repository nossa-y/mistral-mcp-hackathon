/**
 * Utility functions for data normalization
 */
import { Post } from '../models/index.js';
export declare class NormalizationUtils {
    /**
     * Strip tracking URLs and clean up post text
     */
    static cleanPostText(text: string): string;
    /**
     * Validate and normalize ISO timestamp
     */
    static normalizeTimestamp(timestamp: string): string;
    /**
     * Clean and validate hashtags
     */
    static normalizeHashtags(hashtags: string[]): string[];
    /**
     * Clean and validate mentions
     */
    static normalizeMentions(mentions: string[]): string[];
    /**
     * Normalize engagement metrics
     */
    static normalizeEngagement(engagement: any): Record<string, number>;
    /**
     * Apply all normalizations to a post
     */
    static normalizePost(post: Post): Post;
    /**
     * Calculate overlap score between two text strings
     */
    static calculateOverlap(text1: string, text2: string): number;
    /**
     * Extract URLs from text
     */
    static extractUrls(text: string): string[];
    /**
     * Generate short hash for resource IDs
     */
    static generateResourceId(input: string): string;
}
//# sourceMappingURL=normalize.d.ts.map