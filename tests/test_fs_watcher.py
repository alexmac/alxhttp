from asyncio import sleep
import logging
from pathlib import Path
import tempfile
import unittest


from alxhttp.file_watcher import register_file_listener, unregister_file_listener, watch_dir

log = logging.getLogger()


class TestFSWatcher(unittest.IsolatedAsyncioTestCase):
  def test_fs_watcher_empty(self):
    with watch_dir():
      pass

  async def test_fs_watcher(self):
    with tempfile.TemporaryDirectory() as td, watch_dir(Path(td)):
      root = Path(td)
      test_file = (root / 'test.txt').resolve()
      test_file2 = (root / 'test2.txt').resolve()
      test_file3 = (root / 'test3.txt').resolve()

      def cb():
        pass

      def cb3():
        raise ValueError

      # watched file
      register_file_listener(test_file, cb)
      with open(test_file, 'w+') as f:
        f.write('hello')
        f.flush()
      await sleep(1)
      with open(test_file, 'a') as f:
        f.write('world')
        f.flush()
      unregister_file_listener(test_file)

      # unwatched file
      with open(test_file2, 'w+') as f:
        f.write('hello')
        f.flush()
      await sleep(1)
      with open(test_file2, 'a') as f:
        f.write('world')
        f.flush()

      # watched file with error
      register_file_listener(test_file3, cb3)
      with open(test_file3, 'w+') as f:
        f.write('hello')
        f.flush()
      await sleep(1)
      with open(test_file3, 'a') as f:
        f.write('world')
        f.flush()
      unregister_file_listener(test_file3)
