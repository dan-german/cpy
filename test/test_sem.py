import unittest
import cpy.sem as sem

# class TestSem(unittest.TestCase):
#    def test_undeclared_vars(self): 
#       with self.assertRaises(sem.Undeclared): sem.Sem("void f(){a=3;}").run()
#       with self.assertRaises(sem.Undeclared): sem.Sem("void f(){{int a;}a=3;}").run()

if __name__ == "__main__":
  unittest.main(verbosity=1)
