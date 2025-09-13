/**
 * TypeScript interfaces converted from Python Pydantic models
 * Normalized data structures for social media data
 */
import { z } from 'zod';
export declare enum Platform {
    X = "x",
    LINKEDIN = "linkedin"
}
export declare const PlatformSchema: z.ZodEnum<["x", "linkedin"]>;
export interface Person {
    name: string;
    platform: Platform;
    profile_url?: string;
    handle?: string;
    headline_or_bio: string;
}
export declare const PersonSchema: z.ZodObject<{
    name: z.ZodString;
    platform: z.ZodEnum<["x", "linkedin"]>;
    profile_url: z.ZodOptional<z.ZodString>;
    handle: z.ZodOptional<z.ZodString>;
    headline_or_bio: z.ZodDefault<z.ZodString>;
}, "strip", z.ZodTypeAny, {
    name: string;
    platform: "x" | "linkedin";
    headline_or_bio: string;
    profile_url?: string | undefined;
    handle?: string | undefined;
}, {
    name: string;
    platform: "x" | "linkedin";
    profile_url?: string | undefined;
    handle?: string | undefined;
    headline_or_bio?: string | undefined;
}>;
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
export declare const PostSchema: z.ZodObject<{
    platform: z.ZodEnum<["x", "linkedin"]>;
    post_id: z.ZodString;
    url: z.ZodString;
    created_at_iso: z.ZodString;
    text: z.ZodString;
    hashtags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    mentions: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    engagement: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodNumber>>;
    inferred_themes: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    platform: "x" | "linkedin";
    post_id: string;
    url: string;
    created_at_iso: string;
    text: string;
    hashtags: string[];
    mentions: string[];
    engagement: Record<string, number>;
    inferred_themes: string[];
}, {
    platform: "x" | "linkedin";
    post_id: string;
    url: string;
    created_at_iso: string;
    text: string;
    hashtags?: string[] | undefined;
    mentions?: string[] | undefined;
    engagement?: Record<string, number> | undefined;
    inferred_themes?: string[] | undefined;
}>;
export interface Meta {
    source: string;
    fetched_at_iso: string;
    limit: number;
    total_found: number;
}
export declare const MetaSchema: z.ZodObject<{
    source: z.ZodString;
    fetched_at_iso: z.ZodString;
    limit: z.ZodNumber;
    total_found: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    source: string;
    fetched_at_iso: string;
    limit: number;
    total_found: number;
}, {
    source: string;
    fetched_at_iso: string;
    limit: number;
    total_found?: number | undefined;
}>;
export interface Bundle {
    person: Person;
    posts: Post[];
    meta: Meta;
}
export declare const BundleSchema: z.ZodObject<{
    person: z.ZodObject<{
        name: z.ZodString;
        platform: z.ZodEnum<["x", "linkedin"]>;
        profile_url: z.ZodOptional<z.ZodString>;
        handle: z.ZodOptional<z.ZodString>;
        headline_or_bio: z.ZodDefault<z.ZodString>;
    }, "strip", z.ZodTypeAny, {
        name: string;
        platform: "x" | "linkedin";
        headline_or_bio: string;
        profile_url?: string | undefined;
        handle?: string | undefined;
    }, {
        name: string;
        platform: "x" | "linkedin";
        profile_url?: string | undefined;
        handle?: string | undefined;
        headline_or_bio?: string | undefined;
    }>;
    posts: z.ZodDefault<z.ZodArray<z.ZodObject<{
        platform: z.ZodEnum<["x", "linkedin"]>;
        post_id: z.ZodString;
        url: z.ZodString;
        created_at_iso: z.ZodString;
        text: z.ZodString;
        hashtags: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
        mentions: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
        engagement: z.ZodDefault<z.ZodRecord<z.ZodString, z.ZodNumber>>;
        inferred_themes: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
    }, "strip", z.ZodTypeAny, {
        platform: "x" | "linkedin";
        post_id: string;
        url: string;
        created_at_iso: string;
        text: string;
        hashtags: string[];
        mentions: string[];
        engagement: Record<string, number>;
        inferred_themes: string[];
    }, {
        platform: "x" | "linkedin";
        post_id: string;
        url: string;
        created_at_iso: string;
        text: string;
        hashtags?: string[] | undefined;
        mentions?: string[] | undefined;
        engagement?: Record<string, number> | undefined;
        inferred_themes?: string[] | undefined;
    }>, "many">>;
    meta: z.ZodObject<{
        source: z.ZodString;
        fetched_at_iso: z.ZodString;
        limit: z.ZodNumber;
        total_found: z.ZodDefault<z.ZodNumber>;
    }, "strip", z.ZodTypeAny, {
        source: string;
        fetched_at_iso: string;
        limit: number;
        total_found: number;
    }, {
        source: string;
        fetched_at_iso: string;
        limit: number;
        total_found?: number | undefined;
    }>;
}, "strip", z.ZodTypeAny, {
    person: {
        name: string;
        platform: "x" | "linkedin";
        headline_or_bio: string;
        profile_url?: string | undefined;
        handle?: string | undefined;
    };
    posts: {
        platform: "x" | "linkedin";
        post_id: string;
        url: string;
        created_at_iso: string;
        text: string;
        hashtags: string[];
        mentions: string[];
        engagement: Record<string, number>;
        inferred_themes: string[];
    }[];
    meta: {
        source: string;
        fetched_at_iso: string;
        limit: number;
        total_found: number;
    };
}, {
    person: {
        name: string;
        platform: "x" | "linkedin";
        profile_url?: string | undefined;
        handle?: string | undefined;
        headline_or_bio?: string | undefined;
    };
    meta: {
        source: string;
        fetched_at_iso: string;
        limit: number;
        total_found?: number | undefined;
    };
    posts?: {
        platform: "x" | "linkedin";
        post_id: string;
        url: string;
        created_at_iso: string;
        text: string;
        hashtags?: string[] | undefined;
        mentions?: string[] | undefined;
        engagement?: Record<string, number> | undefined;
        inferred_themes?: string[] | undefined;
    }[] | undefined;
}>;
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
export declare const CandidateProfileSchema: z.ZodObject<{
    candidate_id: z.ZodString;
    full_name: z.ZodString;
    organization_name: z.ZodOptional<z.ZodString>;
    domain: z.ZodOptional<z.ZodString>;
    linkedin_url: z.ZodOptional<z.ZodString>;
    x_handle: z.ZodOptional<z.ZodString>;
    confidence: z.ZodNumber;
    source: z.ZodEnum<["apollo", "manual"]>;
}, "strip", z.ZodTypeAny, {
    source: "apollo" | "manual";
    candidate_id: string;
    full_name: string;
    confidence: number;
    organization_name?: string | undefined;
    domain?: string | undefined;
    linkedin_url?: string | undefined;
    x_handle?: string | undefined;
}, {
    source: "apollo" | "manual";
    candidate_id: string;
    full_name: string;
    confidence: number;
    organization_name?: string | undefined;
    domain?: string | undefined;
    linkedin_url?: string | undefined;
    x_handle?: string | undefined;
}>;
export declare enum ErrorType {
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
export declare const GetPostsInputSchema: z.ZodObject<{
    handle: z.ZodString;
    limit: z.ZodDefault<z.ZodNumber>;
}, "strip", z.ZodTypeAny, {
    handle: string;
    limit: number;
}, {
    handle: string;
    limit?: number | undefined;
}>;
export declare const FetchContextsInputSchema: z.ZodObject<{
    first_name: z.ZodString;
    last_name: z.ZodString;
    linkedin_url: z.ZodOptional<z.ZodString>;
    organization_name: z.ZodOptional<z.ZodString>;
    domain: z.ZodOptional<z.ZodString>;
    apollo_limit: z.ZodDefault<z.ZodNumber>;
    include_recent_posts_summary: z.ZodDefault<z.ZodBoolean>;
}, "strip", z.ZodTypeAny, {
    first_name: string;
    last_name: string;
    apollo_limit: number;
    include_recent_posts_summary: boolean;
    organization_name?: string | undefined;
    domain?: string | undefined;
    linkedin_url?: string | undefined;
}, {
    first_name: string;
    last_name: string;
    organization_name?: string | undefined;
    domain?: string | undefined;
    linkedin_url?: string | undefined;
    apollo_limit?: number | undefined;
    include_recent_posts_summary?: boolean | undefined;
}>;
export declare const SuggestOpenersInputSchema: z.ZodObject<{
    linkedin_context_resource: z.ZodString;
    apollo_context_resource: z.ZodString;
    posts_combined_summary: z.ZodOptional<z.ZodString>;
    tone_options: z.ZodDefault<z.ZodArray<z.ZodString, "many">>;
}, "strip", z.ZodTypeAny, {
    linkedin_context_resource: string;
    apollo_context_resource: string;
    tone_options: string[];
    posts_combined_summary?: string | undefined;
}, {
    linkedin_context_resource: string;
    apollo_context_resource: string;
    posts_combined_summary?: string | undefined;
    tone_options?: string[] | undefined;
}>;
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
//# sourceMappingURL=types.d.ts.map