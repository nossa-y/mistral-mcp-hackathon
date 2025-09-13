/**
 * Authentication and CORS middleware for HTTP MCP server
 */
import pino from 'pino';
import { appConfig } from '../config.js';
const logger = pino({ name: 'auth-middleware' });
/**
 * Bearer token authentication middleware
 */
export function bearerTokenAuth(req, res, next) {
    // Skip auth for health check endpoints
    if (req.path === '/health' || req.path === '/healthz' || req.path === '/readiness' || req.path === '/readyz') {
        return next();
    }
    if (!appConfig.serverToken) {
        logger.warn('SERVER_TOKEN not configured, skipping authentication');
        return next();
    }
    const authHeader = req.headers.authorization;
    if (!authHeader) {
        logger.warn('Missing Authorization header');
        res.status(401).json({
            error: 'Unauthorized',
            message: 'Authorization header is required'
        });
        return;
    }
    const [scheme, token] = authHeader.split(' ');
    if (scheme !== 'Bearer' || !token) {
        logger.warn('Invalid Authorization header format');
        res.status(401).json({
            error: 'Unauthorized',
            message: 'Invalid Authorization header format. Use: Bearer <token>'
        });
        return;
    }
    if (token !== appConfig.serverToken) {
        logger.warn('Invalid bearer token');
        res.status(401).json({
            error: 'Unauthorized',
            message: 'Invalid bearer token'
        });
        return;
    }
    // Optionally set user ID from token (for future use)
    req.userId = 'authenticated-user';
    next();
}
/**
 * CORS middleware configured for Le Chat and other allowed origins
 */
export function corsMiddleware(req, res, next) {
    const origin = req.headers.origin;
    if (origin && appConfig.allowedOrigins.includes(origin)) {
        res.header('Access-Control-Allow-Origin', origin);
    }
    res.header('Access-Control-Allow-Methods', 'GET, POST, PUT, DELETE, OPTIONS');
    res.header('Access-Control-Allow-Headers', 'Content-Type, Authorization, X-Requested-With');
    res.header('Access-Control-Allow-Credentials', 'true');
    res.header('Access-Control-Max-Age', '86400'); // 24 hours
    if (req.method === 'OPTIONS') {
        res.status(200).end();
        return;
    }
    next();
}
/**
 * Request logging middleware
 */
export function requestLogging(req, res, next) {
    const requestId = `${Date.now()}-${Math.random().toString(36).substr(2, 9)}`;
    req.requestId = requestId;
    const startTime = Date.now();
    logger.info({
        requestId,
        method: req.method,
        path: req.path,
        userAgent: req.headers['user-agent'],
        origin: req.headers.origin
    }, 'Incoming request');
    res.on('finish', () => {
        const duration = Date.now() - startTime;
        logger.info({
            requestId,
            method: req.method,
            path: req.path,
            statusCode: res.statusCode,
            duration
        }, 'Request completed');
    });
    next();
}
/**
 * Rate limiting middleware (simple in-memory implementation)
 */
export class RateLimiter {
    requests = new Map();
    maxRequests;
    windowMs;
    constructor(maxRequests = 60, windowMs = 60000) {
        this.maxRequests = maxRequests;
        this.windowMs = windowMs;
    }
    middleware = (req, res, next) => {
        const key = this.getClientKey(req);
        const now = Date.now();
        const client = this.requests.get(key);
        if (!client || now > client.resetTime) {
            this.requests.set(key, { count: 1, resetTime: now + this.windowMs });
            return next();
        }
        if (client.count >= this.maxRequests) {
            const retryAfter = Math.ceil((client.resetTime - now) / 1000);
            logger.warn(`Rate limit exceeded for ${key}`);
            res.status(429).json({
                error: 'Too Many Requests',
                message: 'Rate limit exceeded',
                retryAfter
            });
            return;
        }
        client.count++;
        next();
    };
    getClientKey(req) {
        // Use IP address as key (in production, consider using user ID if available)
        return req.ip || req.connection.remoteAddress || 'unknown';
    }
}
/**
 * Error handling middleware
 */
export function errorHandler(error, req, res, next) {
    const requestId = req.requestId;
    logger.error({
        requestId,
        error: error.message,
        stack: error.stack
    }, 'Unhandled error');
    if (res.headersSent) {
        return next(error);
    }
    let statusCode = 500;
    let message = 'Internal Server Error';
    if (error.name === 'ValidationError') {
        statusCode = 400;
        message = 'Invalid input data';
    }
    else if (error.name === 'RATE_LIMITED') {
        statusCode = 429;
        message = 'Rate limit exceeded';
    }
    else if (error.name === 'NOT_FOUND') {
        statusCode = 404;
        message = 'Resource not found';
    }
    res.status(statusCode).json({
        error: error.name || 'UnknownError',
        message,
        requestId
    });
}
//# sourceMappingURL=middleware.js.map