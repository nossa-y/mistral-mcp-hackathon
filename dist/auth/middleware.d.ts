/**
 * Authentication and CORS middleware for HTTP MCP server
 */
import { Request, Response, NextFunction } from 'express';
export interface AuthenticatedRequest extends Request {
    userId?: string;
    requestId?: string;
}
/**
 * Bearer token authentication middleware
 */
export declare function bearerTokenAuth(req: AuthenticatedRequest, res: Response, next: NextFunction): void;
/**
 * CORS middleware configured for Le Chat and other allowed origins
 */
export declare function corsMiddleware(req: Request, res: Response, next: NextFunction): void;
/**
 * Request logging middleware
 */
export declare function requestLogging(req: AuthenticatedRequest, res: Response, next: NextFunction): void;
/**
 * Rate limiting middleware (simple in-memory implementation)
 */
export declare class RateLimiter {
    private requests;
    private readonly maxRequests;
    private readonly windowMs;
    constructor(maxRequests?: number, windowMs?: number);
    middleware: (req: Request, res: Response, next: NextFunction) => void;
    private getClientKey;
}
/**
 * Error handling middleware
 */
export declare function errorHandler(error: any, req: Request, res: Response, next: NextFunction): void;
//# sourceMappingURL=middleware.d.ts.map