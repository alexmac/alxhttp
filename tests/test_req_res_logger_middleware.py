import json
import logging
import unittest
from io import StringIO
from typing import override

from aiohttp import web
from aiohttp.test_utils import make_mocked_request
from aiohttp.web_exceptions import HTTPBadRequest

from alxhttp.middleware.req_res_logger import req_res_logger
from alxhttp.req_id import set_request_id


class TestReqResLoggerMiddleware(unittest.IsolatedAsyncioTestCase):
  @override
  def setUp(self) -> None:
    """Set up test fixtures"""
    self.app: web.Application = web.Application()
    # Assign request ID for testing
    self.req_id = 'test-req-id-123'

    # Create a string buffer to capture log output
    self.log_buffer = StringIO()
    self.log_handler = logging.StreamHandler(self.log_buffer)

    # Configure logger
    self.logger = logging.getLogger('alxhttp.req_res_logger')
    self.logger.setLevel(logging.INFO)
    self.logger.addHandler(self.log_handler)

  def tearDown(self) -> None:
    """Clean up test fixtures"""
    self.logger.removeHandler(self.log_handler)

  async def test_logs_400_status_by_default(self) -> None:
    """Test that 400 status codes are logged by default"""

    async def handler_that_returns_400(request):
      return web.json_response({'error': 'Bad request'}, status=400)

    # Create request and assign ID
    request = make_mocked_request('POST', '/test', app=self.app)
    set_request_id(request)

    # Create middleware with default settings and run it
    middleware = req_res_logger()
    response = await middleware(request, handler_that_returns_400)

    # Check response is correct
    assert response.status == 400

    # Check that log was written
    log_output = self.log_buffer.getvalue()
    assert 'Status 400 - Request/Response:' in log_output
    assert '"req_id":' in log_output  # Check that some req_id is present
    assert '"error": "Bad request"' in log_output

  async def test_does_not_log_200_status_by_default(self) -> None:
    """Test that 200 status codes are not logged by default"""

    async def handler_that_returns_200(request):
      return web.json_response({'success': True}, status=200)

    # Create request and assign ID
    request = make_mocked_request('GET', '/test', app=self.app)
    set_request_id(request)

    # Create middleware with default settings and run it
    middleware = req_res_logger()
    response = await middleware(request, handler_that_returns_200)

    # Check response is correct
    assert response.status == 200

    # Check that no log was written
    log_output = self.log_buffer.getvalue()
    assert 'Status 200 - Request/Response:' not in log_output

  async def test_configurable_status_codes(self) -> None:
    """Test that status codes can be configured"""

    async def handler_that_returns_404(request):
      return web.json_response({'error': 'Not found'}, status=404)

    # Create request and assign ID
    request = make_mocked_request('GET', '/missing', app=self.app)
    set_request_id(request)

    # Run middleware with custom status codes
    middleware = req_res_logger([404, 500])
    response = await middleware(request, handler_that_returns_404)

    # Check response is correct
    assert response.status == 404

    # Check that log was written for 404
    log_output = self.log_buffer.getvalue()
    assert 'Status 404 - Request/Response:' in log_output
    assert '"error": "Not found"' in log_output

  async def test_logs_http_exceptions(self) -> None:
    """Test that HTTP exceptions are logged when they match configured status codes"""

    async def handler_that_raises_400(request):
      raise HTTPBadRequest(text=json.dumps({'error': 'Invalid input'}), content_type='application/json')

    # Create request and assign ID
    request = make_mocked_request('POST', '/test', app=self.app)
    set_request_id(request)

    # Run middleware and expect exception to be re-raised
    middleware = req_res_logger()
    with self.assertRaises(HTTPBadRequest):
      await middleware(request, handler_that_raises_400)

    # Check that log was written for the exception
    log_output = self.log_buffer.getvalue()
    assert 'Status 400 - Request/Exception:' in log_output
    assert '"req_id":' in log_output  # Check that some req_id is present
    assert '"error": "Invalid input"' in log_output

  async def test_logs_request_data(self) -> None:
    """Test that request data is properly logged"""

    async def handler_that_returns_400(request):
      return web.json_response({'error': 'Bad request'}, status=400)

    # Create request with data and assign ID
    request = make_mocked_request('POST', '/test?param1=value1&param2=value2', headers={'Content-Type': 'application/json', 'Authorization': 'Bearer token123'}, app=self.app)
    set_request_id(request)

    # Mock request.text() to return JSON body
    async def mock_text():
      return '{"field": "value"}'

    request.text = mock_text

    # Run middleware
    middleware = req_res_logger()
    response = await middleware(request, handler_that_returns_400)

    # Check that log contains request details
    log_output = self.log_buffer.getvalue()
    assert '"req_id":' in log_output  # Check that some req_id is present
    assert '"method": "POST"' in log_output
    assert '"param1": "value1"' in log_output
    assert '"param2": "value2"' in log_output
    assert '"Authorization": "Bearer token123"' in log_output
    assert '"field": "value"' in log_output

  async def test_handles_invalid_json_gracefully(self) -> None:
    """Test that invalid JSON in request/response doesn't crash the middleware"""

    async def handler_that_returns_400(request):
      return web.Response(text='Invalid JSON: {broken', status=400, content_type='application/json')

    # Create request and assign ID
    request = make_mocked_request('POST', '/test', app=self.app)
    set_request_id(request)

    # Mock request.text() to return invalid JSON
    async def mock_text():
      return 'invalid json {'

    request.text = mock_text

    # Run middleware - should not raise exception
    middleware = req_res_logger()
    response = await middleware(request, handler_that_returns_400)

    # Check response is correct
    assert response.status == 400

    # Check that log was still written (with string fallback)
    log_output = self.log_buffer.getvalue()
    assert 'Status 400 - Request/Response:' in log_output

  async def test_empty_status_codes_list(self) -> None:
    """Test that empty status codes list disables logging"""

    async def handler_that_returns_400(request):
      return web.json_response({'error': 'Bad request'}, status=400)

    # Create request and assign ID
    request = make_mocked_request('POST', '/test', app=self.app)
    set_request_id(request)

    # Run middleware with empty status codes list
    middleware = req_res_logger([])
    response = await middleware(request, handler_that_returns_400)

    # Check response is correct
    assert response.status == 400

    # Check that no log was written
    log_output = self.log_buffer.getvalue()
    assert 'Status 400 - Request/Response:' not in log_output


if __name__ == '__main__':
  unittest.main()
