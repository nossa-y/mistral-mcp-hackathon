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

#### Error: "/uv.lock": not found (FIXED)

**Issue**: The Docker build was failing because:
- UV version mismatch (Dockerfile used 0.5.1, AWS environment expected 0.8.15)
- Incorrect file mount paths in the RUN command
- Buildspec.yml didn't match AWS CodeBuild environment expectations

**Resolution**:
1. ✅ Updated UV version to 0.8.15 in `dockerfiles/python3.13`
2. ✅ Fixed Docker COPY commands to use bind mounts instead
3. ✅ Updated `buildspec.yml` to match AWS CodeBuild environment
4. ✅ Added lambda_handler.py to Docker image
5. ✅ Fixed Lambda handler reference in CMD

#### CodeBuild Context

The CodeBuild process now correctly handles:
- ✅ Repository cloning to `$SRC_DIR` with proper build context
- ✅ Transport type detection (detects `stdio` for Python MCP servers)
- ✅ Dynamic build arguments and ECR authentication
- ✅ Proper Docker file mounting for UV dependency installation

#### Current Build Status

The fixed deployment should now:
1. Successfully find and use `uv.lock` file via bind mount
2. Install Python dependencies using UV 0.8.15
3. Copy all required MCP server files and shared modules
4. Set correct Lambda handler for AWS deployment

### Current Limitation

The current MCP servers use `stdio` transport and may need adaptation for Lambda HTTP events. The Lambda handler provides a basic wrapper, but full HTTP MCP transport integration is planned for the future Node.js implementation.