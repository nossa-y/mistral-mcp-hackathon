/**
 * Configuration management for Social Snapshot Hub
 */
export interface Config {
    apifyToken: string | undefined;
    apifyTwitterActor: string;
    apifyLinkedInPostsActor: string;
    serverName: string;
    host: string;
    port: number;
    serverToken: string | undefined;
    allowedOrigins: string[];
    defaultFreshnessDays: number;
    defaultPostLimitX: number;
    defaultPostLimitLinkedIn: number;
    cacheTtlHours: number;
    storageBackend: 'memory' | 'disk' | 's3';
    diskPath?: string | undefined;
    s3Bucket?: string | undefined;
    s3Region?: string | undefined;
    s3Prefix?: string | undefined;
}
export declare const appConfig: Config;
export declare function validateConfig(): void;
//# sourceMappingURL=config.d.ts.map