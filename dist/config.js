/**
 * Configuration management for Social Snapshot Hub
 */
import { config } from 'dotenv';
// Load environment variables
config();
function parseAllowedOrigins(origins) {
    return origins.split(',').map(origin => origin.trim());
}
export const appConfig = {
    // Apify configuration
    apifyToken: process.env.APIFY_TOKEN,
    apifyTwitterActor: process.env.APIFY_TWITTER_ACTOR || "apidojo/tweet-scraper",
    apifyLinkedInPostsActor: process.env.APIFY_LINKEDIN_POSTS_ACTOR || "your_linkedin_posts_actor",
    // Server configuration
    serverName: process.env.SERVER_NAME || "Social Snapshot Hub",
    host: process.env.HOST || "0.0.0.0",
    port: parseInt(process.env.PORT || "8080", 10),
    serverToken: process.env.SERVER_TOKEN,
    allowedOrigins: parseAllowedOrigins(process.env.ALLOWED_ORIGINS || "https://chat.mistral.ai"),
    // Default limits
    defaultFreshnessDays: parseInt(process.env.DEFAULT_FRESHNESS_DAYS || "30", 10),
    defaultPostLimitX: parseInt(process.env.DEFAULT_POST_LIMIT_X || "20", 10),
    defaultPostLimitLinkedIn: parseInt(process.env.DEFAULT_POST_LIMIT_LINKEDIN || "10", 10),
    // Cache configuration
    cacheTtlHours: parseInt(process.env.CACHE_TTL_HOURS || "24", 10),
    storageBackend: process.env.STORAGE_BACKEND || 'memory',
    diskPath: process.env.DISK_PATH,
    s3Bucket: process.env.S3_BUCKET,
    s3Region: process.env.S3_REGION,
    s3Prefix: process.env.S3_PREFIX
};
export function validateConfig() {
    if (!appConfig.apifyToken) {
        throw new Error("APIFY_TOKEN environment variable is required");
    }
    if (appConfig.port < 1 || appConfig.port > 65535) {
        throw new Error("PORT must be between 1 and 65535");
    }
    if (appConfig.storageBackend === 's3' && (!appConfig.s3Bucket || !appConfig.s3Region)) {
        throw new Error("S3_BUCKET and S3_REGION are required when STORAGE_BACKEND=s3");
    }
}
//# sourceMappingURL=config.js.map