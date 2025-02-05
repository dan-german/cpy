import unittest
from cpy.consts import Peeker

class TestUtils(unittest.TestCase):
  def test_peeker(self):
    p = Peeker("ab")
    assert(p)
    assert next(p) == "a"
    assert next(p) == "b"
    assert not p

if __name__ == '__main__':
  unittest.main(verbosity=2)