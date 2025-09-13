/**
 * Theme inference engine for social media posts
 */
export class ThemeInferenceEngine {
    static THEMES = [
        {
            name: "technology",
            keywords: ["ai", "ml", "tech", "software", "coding", "programming", "developer", "startup", "saas"],
            weight: 1.0
        },
        {
            name: "business",
            keywords: ["business", "strategy", "growth", "revenue", "marketing", "sales", "leadership", "management"],
            weight: 1.0
        },
        {
            name: "career",
            keywords: ["job", "career", "hiring", "interview", "promotion", "salary", "remote", "work"],
            weight: 0.9
        },
        {
            name: "entrepreneurship",
            keywords: ["entrepreneur", "startup", "founder", "venture", "funding", "investment", "pitch"],
            weight: 0.9
        },
        {
            name: "personal_development",
            keywords: ["learning", "growth", "skill", "education", "course", "book", "productivity"],
            weight: 0.8
        },
        {
            name: "finance",
            keywords: ["finance", "money", "investment", "trading", "crypto", "bitcoin", "market"],
            weight: 0.8
        },
        {
            name: "social_impact",
            keywords: ["climate", "sustainability", "social", "impact", "charity", "volunteer", "community"],
            weight: 0.7
        },
        {
            name: "health_fitness",
            keywords: ["health", "fitness", "wellness", "exercise", "diet", "nutrition", "mental health"],
            weight: 0.6
        }
    ];
    /**
     * Infer themes from a single post
     */
    static inferThemes(post) {
        const text = `${post.text} ${post.hashtags.join(' ')}`.toLowerCase();
        const themes = [];
        for (const theme of this.THEMES) {
            let score = 0;
            for (const keyword of theme.keywords) {
                if (text.includes(keyword)) {
                    score += theme.weight;
                }
            }
            if (score > 0) {
                themes.push({ theme: theme.name, score });
            }
        }
        // Sort by score and return top themes
        return themes
            .sort((a, b) => b.score - a.score)
            .slice(0, 3) // Top 3 themes
            .map(t => t.theme);
    }
    /**
     * Infer themes for multiple posts in bulk
     */
    static inferThemesBulk(posts) {
        for (const post of posts) {
            post.inferred_themes = this.inferThemes(post);
        }
    }
    /**
     * Get dominant themes across multiple posts
     */
    static getDominantThemes(posts) {
        const themeCount = new Map();
        for (const post of posts) {
            if (!post.inferred_themes.length) {
                post.inferred_themes = this.inferThemes(post);
            }
            for (const theme of post.inferred_themes) {
                themeCount.set(theme, (themeCount.get(theme) || 0) + 1);
            }
        }
        return Array.from(themeCount.entries())
            .sort(([, a], [, b]) => b - a)
            .slice(0, 5) // Top 5 dominant themes
            .map(([theme]) => theme);
    }
    /**
     * Generate theme summary for context
     */
    static generateThemeSummary(posts) {
        const dominantThemes = this.getDominantThemes(posts);
        if (dominantThemes.length === 0) {
            return "No clear themes identified from recent posts.";
        }
        const themeList = dominantThemes.map(theme => theme.replace('_', ' ')).join(', ');
        return `Recent posts focus on: ${themeList}`;
    }
}
//# sourceMappingURL=theme-inference.js.map