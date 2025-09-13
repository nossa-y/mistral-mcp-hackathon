"""CLI configuration and setup for Social MCP Server"""

import argparse
import sys
from typing import List, Optional


def create_parser() -> argparse.ArgumentParser:
    """Create argument parser for the CLI"""
    parser = argparse.ArgumentParser(
        description="Social MCP Server - Fetch social media data via MCP protocol",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  social-mcp-server                    # Start server in stdio mode (default)
  social-mcp-server --http             # Start HTTP server on localhost:8000
  social-mcp-server --http --port 9000 # Start HTTP server on port 9000
  social-mcp-server --debug --http     # Start HTTP server with debug logging

Environment Variables:
  APIFY_TOKEN                          # Required: Your Apify API token
  APIFY_TWITTER_ACTOR                  # Optional: Custom Twitter actor ID
  APIFY_LINKEDIN_POSTS_ACTOR           # Optional: Custom LinkedIn actor ID
  SERVER_TOKEN                         # Optional: Bearer token for HTTP auth
  ALLOWED_ORIGINS                      # Optional: CORS origins (default: chat.mistral.ai)
        """,
    )

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )

    parser.add_argument(
        "--http",
        action="store_true",
        help="Run in HTTP mode (default: stdio)",
    )

    parser.add_argument(
        "--host",
        default="127.0.0.1",
        help="HTTP server host (default: 127.0.0.1)",
    )

    parser.add_argument(
        "--port",
        type=int,
        default=8000,
        help="HTTP server port (default: 8000)",
    )

    parser.add_argument(
        "--version",
        action="version",
        version="Social MCP Server 0.1.0",
    )

    return parser


def parse_args(args: Optional[List[str]] = None) -> argparse.Namespace:
    """Parse command line arguments"""
    parser = create_parser()
    return parser.parse_args(args)


def validate_environment() -> bool:
    """Validate required environment variables"""
    import os

    required_vars = ["APIFY_TOKEN"]
    missing_vars = []

    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)

    if missing_vars:
        print(f"Error: Missing required environment variables: {', '.join(missing_vars)}")
        print("Please set these variables before starting the server.")
        return False

    return True


def setup_logging(debug: bool = False) -> None:
    """Setup logging configuration"""
    import logging

    level = logging.DEBUG if debug else logging.INFO
    format_string = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"

    logging.basicConfig(
        level=level,
        format=format_string,
        handlers=[logging.StreamHandler(sys.stderr)]
    )

    # Reduce noise from some libraries
    if not debug:
        logging.getLogger("httpx").setLevel(logging.WARNING)
        logging.getLogger("apify_client").setLevel(logging.WARNING)