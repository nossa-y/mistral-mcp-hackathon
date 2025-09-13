"""
Lambda handler wrapper for MCP servers.
This module provides AWS Lambda integration for the MCP servers.
"""

import json
import os
import asyncio
from typing import Dict, Any, Optional
import logging

# Import the consolidated MCP server
from social_mcp_server.server import app as social_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Single consolidated server that handles both X and LinkedIn
SERVER_APP = social_app

async def handle_mcp_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle MCP request through the social MCP server."""
    try:
        # Extract MCP request from Lambda event
        body = event.get('body', '{}')
        if isinstance(body, str):
            try:
                mcp_request = json.loads(body)
            except json.JSONDecodeError as e:
                logger.error(f"Invalid JSON in request body: {e}")
                return create_error_response(-32700, "Parse error", f"Invalid JSON: {e}")
        else:
            mcp_request = body

        logger.info(f"Processing MCP request: {mcp_request.get('method', 'unknown')}")

        # Validate MCP request structure
        if not isinstance(mcp_request, dict):
            return create_error_response(-32600, "Invalid Request", "Request must be a JSON object")

        request_id = mcp_request.get('id')
        method = mcp_request.get('method')

        if not method:
            return create_error_response(-32600, "Invalid Request", "Missing method field", request_id)

        # Handle different MCP methods
        if method == 'tools/list':
            return handle_tools_list(request_id)
        elif method == 'tools/call':
            return await handle_tool_call(mcp_request, request_id)
        elif method == 'initialize':
            return handle_initialize(request_id)
        else:
            return create_error_response(-32601, "Method not found", f"Unknown method: {method}", request_id)

    except Exception as e:
        logger.error(f"Unexpected error handling MCP request: {str(e)}", exc_info=True)
        request_id = None
        try:
            if isinstance(event.get('body'), dict):
                request_id = event['body'].get('id')
            elif isinstance(event.get('body'), str):
                parsed = json.loads(event['body'])
                request_id = parsed.get('id')
        except:
            pass

        return create_error_response(-32603, "Internal error", str(e), request_id)

def create_error_response(code: int, message: str, data: Optional[str] = None, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized MCP error response."""
    error_response = {
        'statusCode': 200,  # MCP errors are still HTTP 200
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'jsonrpc': '2.0',
            'id': request_id,
            'error': {
                'code': code,
                'message': message,
                'data': data
            }
        })
    }
    logger.error(f"MCP Error Response: {code} - {message}" + (f" - {data}" if data else ""))
    return error_response

def create_success_response(result: Any, request_id: Optional[str] = None) -> Dict[str, Any]:
    """Create a standardized MCP success response."""
    return {
        'statusCode': 200,
        'headers': {
            'Content-Type': 'application/json',
            'Access-Control-Allow-Origin': '*'
        },
        'body': json.dumps({
            'jsonrpc': '2.0',
            'id': request_id,
            'result': result
        })
    }

def handle_initialize(request_id: Optional[str]) -> Dict[str, Any]:
    """Handle MCP initialize method."""
    logger.info("Handling initialize request")
    return create_success_response({
        'protocolVersion': '2024-11-05',
        'capabilities': {
            'tools': {}
        },
        'serverInfo': {
            'name': 'Social MCP Server',
            'version': '1.0.0'
        }
    }, request_id)

def handle_tools_list(request_id: Optional[str]) -> Dict[str, Any]:
    """Handle MCP tools/list method."""
    logger.info("Handling tools/list request")
    tools = [
        {
            'name': 'get_x_posts',
            'description': 'Fetch recent posts from X/Twitter using Apify',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'handle': {
                        'type': 'string',
                        'description': 'Twitter handle (without @)'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Maximum number of posts to fetch (default: 20)',
                        'default': 20
                    }
                },
                'required': ['handle']
            }
        },
        {
            'name': 'get_linkedin_posts',
            'description': 'Fetch recent posts from LinkedIn using Apify',
            'inputSchema': {
                'type': 'object',
                'properties': {
                    'profile_url': {
                        'type': 'string',
                        'description': 'LinkedIn profile URL (e.g., https://linkedin.com/in/username)'
                    },
                    'limit': {
                        'type': 'integer',
                        'description': 'Maximum number of posts to fetch (default: 10)',
                        'default': 10
                    }
                },
                'required': ['profile_url']
            }
        }
    ]

    return create_success_response({'tools': tools}, request_id)

async def handle_tool_call(mcp_request: Dict[str, Any], request_id: Optional[str]) -> Dict[str, Any]:
    """Handle MCP tools/call method."""
    try:
        params = mcp_request.get('params', {})
        tool_name = params.get('name')
        arguments = params.get('arguments', {})

        logger.info(f"Calling tool: {tool_name} with arguments: {arguments}")

        if tool_name == 'get_x_posts':
            # Import and call the function from the social server
            from social_mcp_server.server import get_x_posts
            # FastMCP decorates functions as FunctionTool objects, need to access .fn
            actual_function = get_x_posts.fn if hasattr(get_x_posts, 'fn') else get_x_posts
            result = actual_function(**arguments)

            return create_success_response({
                'content': [
                    {
                        'type': 'text',
                        'text': result
                    }
                ]
            }, request_id)

        elif tool_name == 'get_linkedin_posts':
            # Import and call the function from the social server
            from social_mcp_server.server import get_linkedin_posts
            # FastMCP decorates functions as FunctionTool objects, need to access .fn
            actual_function = get_linkedin_posts.fn if hasattr(get_linkedin_posts, 'fn') else get_linkedin_posts
            result = actual_function(**arguments)

            return create_success_response({
                'content': [
                    {
                        'type': 'text',
                        'text': result
                    }
                ]
            }, request_id)

        else:
            return create_error_response(-32601, "Method not found", f"Unknown tool: {tool_name}", request_id)

    except Exception as e:
        logger.error(f"Error calling tool: {str(e)}", exc_info=True)
        return create_error_response(-32603, "Internal error", f"Tool execution failed: {str(e)}", request_id)

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler entry point."""
    return asyncio.run(handle_mcp_request(event, context))

# Default handler for the consolidated social MCP server
handler = lambda_handler