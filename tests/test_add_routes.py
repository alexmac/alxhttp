import logging
import unittest


from alxhttp.pydantic.route import add_route
from example.server import ExampleServer, validated_api

log = logging.getLogger()


class TestAddRoutes(unittest.IsolatedAsyncioTestCase):
  def test_add_route(self):
    s = ExampleServer()
    add_route(s, s.app.router, validated_api)
