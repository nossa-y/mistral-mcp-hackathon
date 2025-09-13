"""
Lambda handler wrapper for MCP servers.
This module provides AWS Lambda integration for the MCP servers.
"""

import json
import os
import asyncio
from typing import Dict, Any, Optional
import logging

# Import your MCP servers
from mcp_servers.mcp_x.server import app as x_app
from mcp_servers.mcp_linkedin.server import app as linkedin_app

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Server mapping based on environment variable
SERVERS = {
    'x': x_app,
    'linkedin': linkedin_app,
}

def get_server_type() -> str:
    """Get the server type from environment variable."""
    return os.environ.get('MCP_SERVER_TYPE', 'x')

async def handle_mcp_request(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handle MCP request through the appropriate server."""
    try:
        server_type = get_server_type()

        if server_type not in SERVERS:
            raise ValueError(f"Unknown server type: {server_type}")

        app = SERVERS[server_type]

        # Extract MCP request from Lambda event
        # This assumes the event contains the MCP request in the body
        body = event.get('body', '{}')
        if isinstance(body, str):
            mcp_request = json.loads(body)
        else:
            mcp_request = body

        logger.info(f"Processing MCP request for {server_type}: {mcp_request.get('method', 'unknown')}")

        # Process the request through the MCP server
        # Note: This is a simplified handler - you may need to adapt based on
        # your specific MCP server implementation and transport needs

        # For now, return a basic response structure
        return {
            'statusCode': 200,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'jsonrpc': '2.0',
                'id': mcp_request.get('id'),
                'result': {
                    'message': f'MCP {server_type} server is running',
                    'server_type': server_type
                }
            })
        }

    except Exception as e:
        logger.error(f"Error handling MCP request: {str(e)}")
        return {
            'statusCode': 500,
            'headers': {
                'Content-Type': 'application/json',
                'Access-Control-Allow-Origin': '*'
            },
            'body': json.dumps({
                'jsonrpc': '2.0',
                'id': event.get('body', {}).get('id') if isinstance(event.get('body'), dict) else None,
                'error': {
                    'code': -32603,
                    'message': 'Internal error',
                    'data': str(e)
                }
            })
        }

def lambda_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """AWS Lambda handler entry point."""
    return asyncio.run(handle_mcp_request(event, context))

# For backwards compatibility, create specific handlers for each server
def x_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handler specifically for X/Twitter MCP server."""
    os.environ['MCP_SERVER_TYPE'] = 'x'
    return lambda_handler(event, context)

def linkedin_handler(event: Dict[str, Any], context: Any) -> Dict[str, Any]:
    """Handler specifically for LinkedIn MCP server."""
    os.environ['MCP_SERVER_TYPE'] = 'linkedin'
    return lambda_handler(event, context)

# Default handler
handler = lambda_handler