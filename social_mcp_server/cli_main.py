"""Main CLI entry point for Social MCP Server"""

import sys
import os
from .cli import parse_args, validate_environment, setup_logging
from .server import create_mcp_server
from .http_server import run_http_server
from .config import config


def main() -> None:
    """Main entry point for the CLI script"""
    try:
        # Parse arguments
        args = parse_args()

        # Setup logging
        setup_logging(debug=args.debug)

        # Override config with CLI arguments if provided
        if hasattr(args, 'host') and args.host:
            config.host = args.host
        if hasattr(args, 'port') and args.port:
            config.port = args.port

        # Validate environment (but don't exit - allow server to handle missing tokens)
        if not validate_environment():
            print("Warning: Server will return errors for API calls without proper environment setup")

        # Run server in appropriate mode
        if args.http:
            print(f"Starting HTTP MCP server on {config.host}:{config.port}")
            print(f"MCP endpoint: http://{config.host}:{config.port}/mcp")
            if config.server_token:
                print("Authentication: Enabled (Bearer token required)")
            else:
                print("Authentication: Disabled (set SERVER_TOKEN to enable)")

            run_http_server()
        else:
            print("Starting stdio MCP server...")
            mcp = create_mcp_server()
            mcp.run()

    except KeyboardInterrupt:
        print("\nServer stopped by user")
        sys.exit(0)
    except Exception as e:
        print(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()