"""Main CLI entry point for Social MCP Server"""

import sys
from .cli import parse_args, validate_environment, setup_logging
from .server import create_mcp_server


def main() -> None:
    """Main entry point for the CLI script"""
    try:
        # Parse arguments
        args = parse_args()

        # Setup logging
        setup_logging(debug=args.debug)

        # Validate environment (but don't exit - allow server to handle missing tokens)
        if not validate_environment():
            print("Warning: Server will return errors for API calls without proper environment setup")

        # Create and run server
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