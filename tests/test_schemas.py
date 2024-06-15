import logging
import unittest

from alxhttp.schemas import gen_prefixed_id


log = logging.getLogger()


class TestSchemas(unittest.IsolatedAsyncioTestCase):
  async def test_gen_prefixed_id(self):
    r = gen_prefixed_id('foo_')
    assert r.startswith('foo_')
    assert len(r) == 28
