/**
 * Utility functions for data normalization
 */

import { Post } from '../models/index.js';

export class NormalizationUtils {
  /**
   * Strip tracking URLs and clean up post text
   */
  static cleanPostText(text: string): string {
    // Remove tracking URLs (t.co, bit.ly, etc.)
    const cleanText = text
      .replace(/https?:\/\/t\.co\/\w+/gi, '')
      .replace(/https?:\/\/bit\.ly\/\w+/gi, '')
      .replace(/https?:\/\/tinyurl\.com\/\w+/gi, '')
      .trim();

    // Remove extra whitespace
    return cleanText.replace(/\s+/g, ' ');
  }

  /**
   * Validate and normalize ISO timestamp
   */
  static normalizeTimestamp(timestamp: string): string {
    try {
      const date = new Date(timestamp);
      if (isNaN(date.getTime())) {
        return new Date().toISOString();
      }
      return date.toISOString();
    } catch (error) {
      return new Date().toISOString();
    }
  }

  /**
   * Clean and validate hashtags
   */
  static normalizeHashtags(hashtags: string[]): string[] {
    return hashtags
      .filter(tag => typeof tag === 'string' && tag.length > 0)
      .map(tag => tag.replace('#', '').toLowerCase())
      .filter((tag, index, array) => array.indexOf(tag) === index); // Remove duplicates
  }

  /**
   * Clean and validate mentions
   */
  static normalizeMentions(mentions: string[]): string[] {
    return mentions
      .filter(mention => typeof mention === 'string' && mention.length > 0)
      .map(mention => mention.replace('@', '').toLowerCase())
      .filter((mention, index, array) => array.indexOf(mention) === index); // Remove duplicates
  }

  /**
   * Normalize engagement metrics
   */
  static normalizeEngagement(engagement: any): Record<string, number> {
    const normalized: Record<string, number> = {};

    if (typeof engagement === 'object' && engagement !== null) {
      for (const [key, value] of Object.entries(engagement)) {
        if (typeof value === 'number' && value >= 0) {
          normalized[key] = value;
        } else if (typeof value === 'string' && !isNaN(Number(value))) {
          normalized[key] = Number(value);
        }
      }
    }

    return normalized;
  }

  /**
   * Apply all normalizations to a post
   */
  static normalizePost(post: Post): Post {
    return {
      ...post,
      text: this.cleanPostText(post.text),
      created_at_iso: this.normalizeTimestamp(post.created_at_iso),
      hashtags: this.normalizeHashtags(post.hashtags),
      mentions: this.normalizeMentions(post.mentions),
      engagement: this.normalizeEngagement(post.engagement)
    };
  }

  /**
   * Calculate overlap score between two text strings
   */
  static calculateOverlap(text1: string, text2: string): number {
    const words1 = new Set(text1.toLowerCase().split(/\s+/));
    const words2 = new Set(text2.toLowerCase().split(/\s+/));

    const intersection = new Set([...words1].filter(word => words2.has(word)));
    const union = new Set([...words1, ...words2]);

    return union.size > 0 ? intersection.size / union.size : 0;
  }

  /**
   * Extract URLs from text
   */
  static extractUrls(text: string): string[] {
    const urlRegex = /https?:\/\/(www\.)?[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)/gi;
    return text.match(urlRegex) || [];
  }

  /**
   * Generate short hash for resource IDs
   */
  static generateResourceId(input: string): string {
    let hash = 0;
    for (let i = 0; i < input.length; i++) {
      const char = input.charCodeAt(i);
      hash = ((hash << 5) - hash) + char;
      hash = hash & hash; // Convert to 32bit integer
    }
    return Math.abs(hash).toString(36);
  }
}