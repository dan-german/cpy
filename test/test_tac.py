# import unittest
# from cpy.prs import Prs
# from cpy.sem import analyze
# from cpy.tac import to_tac

# class TestTac(unittest.TestCase):
#     def code_to_tac(self,code:str):
#         table=to_tac(analyze(list(Prs(code).parse())))
#         return list(str(x) for x in table.values())
#     def assert_helper(self,code:str, lst:list):
#         self.assertEqual(self.code_to_tac(code),lst)

#     def test1(self):
#         self.assert_helper(
#             """
#             int a(){return 2*3+1;}
#             int b(){return a();}
#             """,
#         [
#             "a:",
#             "store G0",
#             "G0 = 2 * 3",
#             "store G1",
#             "G1 = G0 + 1",
#             "return G1",
#             "b:",
#             "G0 = call a",
#             "return G0"
#         ])

#     def test2(self):
#         self.assert_helper(
#             """
#             void a(int a){}
#             int b(){a();}
#             """,
#         [
#             "a:",
#             "param a",
#             "b:",
#             "call a",
#         ])

# if __name__ == "__main__":
#   unittest.main(verbosity=1)