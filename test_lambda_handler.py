#!/usr/bin/env python3
"""
Test script for the Lambda handler to validate MCP functionality.
This script tests the lambda handler without requiring actual AWS deployment.
"""

import json
import os
import sys
import asyncio
from typing import Dict, Any
from unittest.mock import Mock, patch

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the lambda handler
from lambda_handler import lambda_handler, handle_mcp_request

class LambdaTester:
    """Test class for Lambda handler MCP functionality."""

    def __init__(self):
        self.test_results = []

    async def run_test(self, test_name: str, event: Dict[str, Any], expected_status: int = 200):
        """Run a single test and capture results."""
        print(f"\n=== Running Test: {test_name} ===")

        try:
            # Create mock Lambda context
            context = Mock()
            context.function_name = "social-mcp-server"
            context.function_version = "$LATEST"
            context.memory_limit_in_mb = 512
            context.remaining_time_in_millis = lambda: 30000

            # Call the lambda handler
            result = await handle_mcp_request(event, context)

            # Parse response
            status_code = result.get('statusCode', 500)
            body = result.get('body', '{}')

            try:
                parsed_body = json.loads(body)
            except json.JSONDecodeError:
                parsed_body = {'error': 'Invalid JSON response'}

            # Print results
            print(f"Status Code: {status_code}")
            print(f"Response Body: {json.dumps(parsed_body, indent=2)}")

            # Check if test passed
            test_passed = status_code == expected_status

            if test_passed:
                print("✅ TEST PASSED")
            else:
                print(f"❌ TEST FAILED - Expected status {expected_status}, got {status_code}")

            self.test_results.append({
                'name': test_name,
                'passed': test_passed,
                'status_code': status_code,
                'response': parsed_body
            })

            return result

        except Exception as e:
            print(f"❌ TEST FAILED with exception: {str(e)}")
            self.test_results.append({
                'name': test_name,
                'passed': False,
                'error': str(e)
            })
            return None

    def create_mcp_request(self, method: str, params: Dict[str, Any] = None, request_id: str = "test-1") -> Dict[str, Any]:
        """Create a properly formatted MCP request."""
        request = {
            'jsonrpc': '2.0',
            'id': request_id,
            'method': method
        }
        if params:
            request['params'] = params
        return request

    def create_lambda_event(self, mcp_request: Dict[str, Any]) -> Dict[str, Any]:
        """Create a Lambda event with MCP request in body."""
        return {
            'body': json.dumps(mcp_request),
            'headers': {
                'Content-Type': 'application/json'
            },
            'httpMethod': 'POST',
            'isBase64Encoded': False
        }

    async def test_initialize(self):
        """Test MCP initialize method."""
        mcp_request = self.create_mcp_request('initialize', {
            'protocolVersion': '2024-11-05',
            'capabilities': {},
            'clientInfo': {
                'name': 'test-client',
                'version': '1.0.0'
            }
        })
        event = self.create_lambda_event(mcp_request)
        return await self.run_test("MCP Initialize", event)

    async def test_tools_list(self):
        """Test MCP tools/list method."""
        mcp_request = self.create_mcp_request('tools/list')
        event = self.create_lambda_event(mcp_request)
        return await self.run_test("MCP Tools List", event)

    async def test_invalid_json(self):
        """Test invalid JSON handling."""
        event = {
            'body': '{"invalid": json}',  # Invalid JSON
            'headers': {'Content-Type': 'application/json'},
            'httpMethod': 'POST'
        }
        return await self.run_test("Invalid JSON", event)

    async def test_missing_method(self):
        """Test missing method field."""
        mcp_request = {
            'jsonrpc': '2.0',
            'id': 'test-1',
            # Missing 'method' field
        }
        event = self.create_lambda_event(mcp_request)
        return await self.run_test("Missing Method", event)

    async def test_unknown_method(self):
        """Test unknown method handling."""
        mcp_request = self.create_mcp_request('unknown/method')
        event = self.create_lambda_event(mcp_request)
        return await self.run_test("Unknown Method", event)

    @patch.dict(os.environ, {'APIFY_TOKEN': 'mock-token'})
    async def test_x_posts_tool_call(self):
        """Test calling get_x_posts tool."""
        # Mock the Apify client and response
        with patch('social_mcp_server.server.ApifyClient') as mock_apify_client:
            # Setup mock
            mock_client = Mock()
            mock_apify_client.return_value = mock_client

            mock_run = {'defaultDatasetId': 'mock-dataset-id'}
            mock_client.actor.return_value.call.return_value = mock_run

            # Mock dataset items
            mock_items = [
                {
                    'id': '12345',
                    'url': 'https://twitter.com/testuser/status/12345',
                    'text': 'Test tweet content',
                    'createdAt': '2024-01-15T10:30:00Z',
                    'likeCount': 10,
                    'retweetCount': 5,
                    'replyCount': 2,
                    'quoteCount': 1,
                    'entities': {
                        'hashtags': [{'text': 'test'}],
                        'user_mentions': [{'screen_name': 'mentioned_user'}]
                    }
                }
            ]
            mock_client.dataset.return_value.iterate_items.return_value = mock_items

            mcp_request = self.create_mcp_request('tools/call', {
                'name': 'get_x_posts',
                'arguments': {
                    'handle': 'testuser',
                    'limit': 10
                }
            })
            event = self.create_lambda_event(mcp_request)
            return await self.run_test("X Posts Tool Call", event)

    @patch.dict(os.environ, {'APIFY_TOKEN': 'mock-token'})
    async def test_linkedin_posts_tool_call(self):
        """Test calling get_linkedin_posts tool."""
        # Mock the Apify client and response
        with patch('social_mcp_server.server.ApifyClient') as mock_apify_client:
            # Setup mock
            mock_client = Mock()
            mock_apify_client.return_value = mock_client

            mock_run = {'defaultDatasetId': 'mock-dataset-id'}
            mock_client.actor.return_value.call.return_value = mock_run

            # Mock dataset items
            mock_items = [
                {
                    'postId': 'linkedin-post-123',
                    'postUrl': 'https://linkedin.com/posts/testuser_activity-123',
                    'text': 'Test LinkedIn post content #professional',
                    'postedAt': '2024-01-15T10:30:00Z',
                    'likesCount': 25,
                    'commentsCount': 5,
                    'sharesCount': 3
                }
            ]
            mock_client.dataset.return_value.iterate_items.return_value = mock_items

            mcp_request = self.create_mcp_request('tools/call', {
                'name': 'get_linkedin_posts',
                'arguments': {
                    'profile_url': 'https://linkedin.com/in/testuser',
                    'limit': 10
                }
            })
            event = self.create_lambda_event(mcp_request)
            return await self.run_test("LinkedIn Posts Tool Call", event)

    async def test_tool_call_unknown_tool(self):
        """Test calling an unknown tool."""
        mcp_request = self.create_mcp_request('tools/call', {
            'name': 'unknown_tool',
            'arguments': {}
        })
        event = self.create_lambda_event(mcp_request)
        return await self.run_test("Unknown Tool Call", event)

    async def test_tool_call_missing_args(self):
        """Test calling a tool with missing required arguments."""
        mcp_request = self.create_mcp_request('tools/call', {
            'name': 'get_x_posts',
            'arguments': {}  # Missing 'handle' argument
        })
        event = self.create_lambda_event(mcp_request)
        return await self.run_test("Tool Call Missing Args", event)

    def print_summary(self):
        """Print test summary."""
        print("\n" + "="*60)
        print("TEST SUMMARY")
        print("="*60)

        total_tests = len(self.test_results)
        passed_tests = sum(1 for test in self.test_results if test.get('passed', False))
        failed_tests = total_tests - passed_tests

        print(f"Total Tests: {total_tests}")
        print(f"Passed: ✅ {passed_tests}")
        print(f"Failed: ❌ {failed_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%" if total_tests > 0 else "N/A")

        if failed_tests > 0:
            print("\nFailed Tests:")
            for test in self.test_results:
                if not test.get('passed', False):
                    print(f"  ❌ {test['name']}")
                    if 'error' in test:
                        print(f"     Error: {test['error']}")

        print("\n" + "="*60)

async def main():
    """Run all tests."""
    print("🚀 Starting Lambda Handler MCP Tests...")

    tester = LambdaTester()

    # Run all tests
    await tester.test_initialize()
    await tester.test_tools_list()
    await tester.test_invalid_json()
    await tester.test_missing_method()
    await tester.test_unknown_method()
    await tester.test_x_posts_tool_call()
    await tester.test_linkedin_posts_tool_call()
    await tester.test_tool_call_unknown_tool()
    await tester.test_tool_call_missing_args()

    # Print summary
    tester.print_summary()

if __name__ == "__main__":
    asyncio.run(main())