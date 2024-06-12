from aiohttp.typedefs import Handler
from aiohttp.web import Request, json_response, middleware, StreamResponse
from aiohttp.web_exceptions import HTTPClientError, HTTPServerError

from alxhttp.req_id import get_request_id


error_types = frozenset(
  [
    'HTTPBadGateway',
    'HTTPBadRequest',
    'HTTPClientError',
    'HTTPConflict',
    'HTTPExpectationFailed',
    'HTTPFailedDependency',
    'HTTPForbidden',
    'HTTPGatewayTimeout',
    'HTTPGone',
    'HTTPInsufficientStorage',
    'HTTPInternalServerError',
    'HTTPLengthRequired',
    'HTTPMethodNotAllowed',
    'HTTPMisdirectedRequest',
    'HTTPNetworkAuthenticationRequired',
    'HTTPNotAcceptable',
    'HTTPNotExtended',
    'HTTPNotFound',
    'HTTPNotImplemented',
    'HTTPPaymentRequired',
    'HTTPPreconditionFailed',
    'HTTPPreconditionRequired',
    'HTTPProxyAuthenticationRequired',
    'HTTPRequestEntityTooLarge',
    'HTTPRequestHeaderFieldsTooLarge',
    'HTTPRequestRangeNotSatisfiable',
    'HTTPRequestTimeout',
    'HTTPRequestURITooLong',
    'HTTPServerError',
    'HTTPServiceUnavailable',
    'HTTPTooManyRequests',
    'HTTPUnauthorized',
    'HTTPUnavailableForLegalReasons',
    'HTTPUnprocessableEntity',
    'HTTPUnsupportedMediaType',
    'HTTPUpgradeRequired',
    'HTTPVariantAlsoNegotiates',
    'HTTPVersionNotSupported',
  ]
)


@middleware
async def ensure_json_errors(request: Request, handler: Handler) -> StreamResponse:
  """
  Ensure that any of AioHTTP's 4XX/5XX exceptions become JSON
  responses. Note that this intentionally avoids messing around
  with subclasses of these exceptions.
  """
  try:
    return await handler(request)
  except (HTTPClientError, HTTPServerError) as e:
    if type(e).__name__ in error_types:
      # It's one of the native errors, not a subclass
      return json_response(
        {
          'error': e.reason,
          'request_id': get_request_id(request),
        },
        status=e.status_code,
      )
    raise
