/**
 * TypeScript interfaces converted from Python Pydantic models
 * Normalized data structures for social media data
 */
import { z } from 'zod';
// Enums
export var Platform;
(function (Platform) {
    Platform["X"] = "x";
    Platform["LINKEDIN"] = "linkedin";
})(Platform || (Platform = {}));
export const PlatformSchema = z.enum(["x", "linkedin"]);
export const PersonSchema = z.object({
    name: z.string().describe("Display name or handle"),
    platform: PlatformSchema.describe("Source platform"),
    profile_url: z.string().optional().describe("Full profile URL"),
    handle: z.string().optional().describe("Username/handle"),
    headline_or_bio: z.string().default("").describe("Brief bio or headline")
});
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
export const MetaSchema = z.object({
    source: z.string().describe("MCP server name that fetched data"),
    fetched_at_iso: z.string().describe("ISO 8601 fetch timestamp"),
    limit: z.number().describe("Requested post limit"),
    total_found: z.number().default(0).describe("Total posts found")
});
export const BundleSchema = z.object({
    person: PersonSchema.describe("Person information"),
    posts: z.array(PostSchema).default([]).describe("Recent posts"),
    meta: MetaSchema.describe("Fetch metadata")
});
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
export var ErrorType;
(function (ErrorType) {
    ErrorType["NOT_FOUND"] = "NOT_FOUND";
    ErrorType["RATE_LIMITED"] = "RATE_LIMITED";
    ErrorType["SCHEMA_MISMATCH"] = "SCHEMA_MISMATCH";
    ErrorType["PRIVATE_PROFILE"] = "PRIVATE_PROFILE";
    ErrorType["INVALID_INPUT"] = "INVALID_INPUT";
    ErrorType["API_ERROR"] = "API_ERROR";
    ErrorType["COOKIE_EXPIRED"] = "COOKIE_EXPIRED";
    ErrorType["APIFY_RUN_ERROR"] = "APIFY_RUN_ERROR";
    ErrorType["APOLLO_AUTH_ERROR"] = "APOLLO_AUTH_ERROR";
    ErrorType["INSUFFICIENT_DATA"] = "INSUFFICIENT_DATA";
})(ErrorType || (ErrorType = {}));
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
//# sourceMappingURL=types.js.map