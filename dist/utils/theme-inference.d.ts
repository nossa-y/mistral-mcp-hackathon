/**
 * Theme inference engine for social media posts
 */
import { Post } from '../models/index.js';
export interface Theme {
    name: string;
    keywords: string[];
    weight: number;
}
export declare class ThemeInferenceEngine {
    private static readonly THEMES;
    /**
     * Infer themes from a single post
     */
    static inferThemes(post: Post): string[];
    /**
     * Infer themes for multiple posts in bulk
     */
    static inferThemesBulk(posts: Post[]): void;
    /**
     * Get dominant themes across multiple posts
     */
    static getDominantThemes(posts: Post[]): string[];
    /**
     * Generate theme summary for context
     */
    static generateThemeSummary(posts: Post[]): string;
}
//# sourceMappingURL=theme-inference.d.ts.map