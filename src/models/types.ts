/**
 * TypeScript interfaces converted from Python Pydantic models
 * Normalized data structures for social media data
 */

import { z } from 'zod';

// Enums
export enum Platform {
  X = "x",
  LINKEDIN = "linkedin"
}

export const PlatformSchema = z.enum(["x", "linkedin"]);

// Person model
export interface Person {
  name: string;
  platform: Platform;
  profile_url?: string;
  handle?: string;
  headline_or_bio: string;
}

export const PersonSchema = z.object({
  name: z.string().describe("Display name or handle"),
  platform: PlatformSchema.describe("Source platform"),
  profile_url: z.string().optional().describe("Full profile URL"),
  handle: z.string().optional().describe("Username/handle"),
  headline_or_bio: z.string().default("").describe("Brief bio or headline")
});

// Post model
export interface Post {
  platform: Platform;
  post_id: string;
  url: string;
  created_at_iso: string;
  text: string;
  hashtags: string[];
  mentions: string[];
  engagement: Record<string, number>;
  inferred_themes: string[];
}

export const PostSchema = z.object({
  platform: PlatformSchema.describe("Source platform"),
  post_id: z.string().describe("Unique post identifier"),
  url: z.string().describe("Direct link to post"),
  created_at_iso: z.string().describe("ISO 8601 creation timestamp"),
  text: z.string().describe("Post content"),
  hashtags: z.array(z.string()).default([]).describe("Extracted hashtags"),
  mentions: z.array(z.string()).default([]).describe("Mentioned users"),
  engagement: z.record(z.string(), z.number()).default({}).describe("Like/retweet counts"),
  inferred_themes: z.array(z.string()).default([]).describe("Detected themes")
});

// Meta model
export interface Meta {
  source: string;
  fetched_at_iso: string;
  limit: number;
  total_found: number;
}

export const MetaSchema = z.object({
  source: z.string().describe("MCP server name that fetched data"),
  fetched_at_iso: z.string().describe("ISO 8601 fetch timestamp"),
  limit: z.number().describe("Requested post limit"),
  total_found: z.number().default(0).describe("Total posts found")
});

// Bundle model
export interface Bundle {
  person: Person;
  posts: Post[];
  meta: Meta;
}

export const BundleSchema = z.object({
  person: PersonSchema.describe("Person information"),
  posts: z.array(PostSchema).default([]).describe("Recent posts"),
  meta: MetaSchema.describe("Fetch metadata")
});

// Candidate Profile (for Apollo integration)
export interface CandidateProfile {
  candidate_id: string;
  full_name: string;
  organization_name?: string;
  domain?: string;
  linkedin_url?: string;
  x_handle?: string;
  confidence: number;
  source: 'apollo' | 'manual';
}

export const CandidateProfileSchema = z.object({
  candidate_id: z.string().describe("UUID per session"),
  full_name: z.string(),
  organization_name: z.string().optional(),
  domain: z.string().optional(),
  linkedin_url: z.string().optional(),
  x_handle: z.string().optional().describe("without '@'"),
  confidence: z.number().min(0).max(1).describe("0..1"),
  source: z.enum(['apollo', 'manual'])
});

// Error types
export enum ErrorType {
  NOT_FOUND = "NOT_FOUND",
  RATE_LIMITED = "RATE_LIMITED",
  SCHEMA_MISMATCH = "SCHEMA_MISMATCH",
  PRIVATE_PROFILE = "PRIVATE_PROFILE",
  INVALID_INPUT = "INVALID_INPUT",
  API_ERROR = "API_ERROR",
  COOKIE_EXPIRED = "COOKIE_EXPIRED",
  APIFY_RUN_ERROR = "APIFY_RUN_ERROR",
  APOLLO_AUTH_ERROR = "APOLLO_AUTH_ERROR",
  INSUFFICIENT_DATA = "INSUFFICIENT_DATA"
}

// Input schemas for MCP tools
export const GetPostsInputSchema = z.object({
  handle: z.string().describe("Username/handle (without @)"),
  limit: z.number().min(1).max(100).default(20).describe("Number of posts to fetch")
});

export const FetchContextsInputSchema = z.object({
  first_name: z.string(),
  last_name: z.string(),
  linkedin_url: z.string().optional(),
  organization_name: z.string().optional(),
  domain: z.string().optional(),
  apollo_limit: z.number().min(1).max(3).default(1),
  include_recent_posts_summary: z.boolean().default(true)
});

export const SuggestOpenersInputSchema = z.object({
  linkedin_context_resource: z.string(),
  apollo_context_resource: z.string(),
  posts_combined_summary: z.string().optional(),
  tone_options: z.array(z.string()).default(["casual", "professional", "playful"])
});

// Response types
export interface FetchContextsResponse {
  linkedin_context: string;
  apollo_context: string;
  combined_context: string;
  apollo_candidates: CandidateProfile[];
  warnings: string[];
}

export interface OpenerSuggestion {
  tone: string;
  text: string;
  why: string;
}

export interface SuggestOpenersResponse {
  openers: OpenerSuggestion[];
  warnings: string[];
}