# Deployment Guide

## AWS CodeBuild Deployment

The project includes Docker configuration for deploying MCP servers to AWS Lambda using CodeBuild.

### Docker Files

- `dockerfiles/python3.13` - Dockerfile for Python-based MCP servers
- `dockerfiles/nodejs22` - Dockerfile for future Node.js HTTP MCP server
- `buildspec.yml` - CodeBuild configuration

### Environment Variables

The following environment variables need to be configured in your deployment environment:

#### Required for CodeBuild
- `RUNTIME` - Runtime type (`python3.13` or `nodejs22`)
- `PROJECT_BUILD_IMAGES_REPOSITORY_URI` - ECR repository URI
- `RESOLVED_SOURCE_VERSION` - Git commit hash or version tag
- `AWS_DEFAULT_REGION` - AWS region
- `AWS_ACCOUNT_ID` - AWS account ID

#### Required for MCP Servers
- `APIFY_TOKEN` - Apify API token for data fetching
- `MCP_SERVER_TYPE` - Server type (`x` or `linkedin`)

### Deployment Process

1. **CodeBuild Setup**: The build process uses the provided `buildspec.yml` to:
   - Build Docker image using the appropriate Dockerfile
   - Tag with both version and latest tags
   - Push to ECR repository

2. **Lambda Configuration**: Each MCP server can be deployed as a separate Lambda function:
   - **X/Twitter Server**: Use `lambda_handler.x_handler` as the handler
   - **LinkedIn Server**: Use `lambda_handler.linkedin_handler` as the handler

### Lambda Handler

The `lambda_handler.py` provides AWS Lambda integration:

```python
# For X/Twitter MCP server
handler = lambda_handler.x_handler

# For LinkedIn MCP server
handler = lambda_handler.linkedin_handler
```

### Build Commands

To build locally for testing:

```bash
# Build Python runtime
docker buildx build --platform linux/amd64 -f dockerfiles/python3.13 -t coldopen-coach:python .

# Build Node.js runtime (future)
docker buildx build --platform linux/amd64 -f dockerfiles/nodejs22 -t coldopen-coach:nodejs .
```

### Troubleshooting

#### Error: "/uv.lock": not found

This error occurs when the Docker build context doesn't include the required files. Ensure:

1. The build is run from the repository root directory
2. `coldopen-coach/uv.lock` and `coldopen-coach/pyproject.toml` exist
3. The Dockerfile paths are correct relative to the build context

#### CodeBuild Context

The CodeBuild process expects:
- Repository root as build context
- `dockerfiles/` directory with runtime-specific Dockerfiles
- `buildspec.yml` in repository root

### Current Limitation

The current MCP servers use `stdio` transport and may need adaptation for Lambda HTTP events. The Lambda handler provides a basic wrapper, but full HTTP MCP transport integration is planned for the future Node.js implementation.