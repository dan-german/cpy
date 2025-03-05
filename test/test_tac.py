import unittest
from cpy.prs import Prs
from cpy.sem import analyze
from cpy.tac import generate

class TestTac(unittest.TestCase):
    def code_to_tac(self,code:str):
        table=generate(analyze(list(Prs(code).parse())))
        return list(str(x) for x in table.values())
    def assert_helper(self,code:str, lst:list):
        self.assertEqual(self.code_to_tac(code),lst)

    # def test1(self):
    #     self.assert_helper(
    #         "int a(){return 2*3+1;}",
    #     [
    #         "a:",
    #         "G0 = 2 * 3",
    #         "G1 = G0 + 1",
    #         "return G1"
    #     ])

    def test2(self):
        self.assert_helper(
            """
            int a(){return 2*3+1;}
            int b(){return a();}
            """,
        [
            "a:",
            "G0 = 2 * 3",
            "G1 = G0 + 1",
            "return G1",
            "b:",
            "G0 = call a",
            "return G0"
        ])

    def test3(self):
        self.assert_helper(
            """
            void a(){}
            int b(){a();}
            """,
        [
            "a:",
            "b:",
            "call a",
        ])

if __name__ == "__main__":
  unittest.main(verbosity=1)