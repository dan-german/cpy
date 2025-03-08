# import unittest
# import cpy.cmp as cmp

# class TestARM64(unittest.TestCase):
#     def test1(self):
#         expected = [ 
#             ".global _a",
#             "_a:",
#             # "  ret"
#         ]
#         self.assertEqual(cmp.compile("int a(){}"), "\n".join(expected))

#     def test2(self): 
#         expected = [
#             ".global _a",
#             "_a:",
#             "  sub sp, sp, #16", # stack must be 16 bytes aligned
#             "  add sp, sp, #16", # return stack space
#             "  ret"
#         ]
#         self.assertEqual(cmp.compile("void a(){int a;}"),expected)

#     def test3(self):
#         expected = [
#             ".global _a",
#             "_a:",
#             "  sub sp, sp, #32", # stack must be 16 bytes aligned
#             "  add sp, sp, #32", # return stack space
#             "  ret"
#         ]
#         self.assertEqual(cmp.compile("void a(){int a;int b; int c; int d; int e;}"),expected)

#     def test4(self): 
#         expected = [
#             ".global _a",
#             "_a:",
#             "  sub sp, sp, #16",# stack must be 16 bytes aligned
#             "  str w0, [sp, #12]",# store param
#             "  add sp, sp, #16",# return stack space
#             "  ret"
#         ]
#         self.assertEqual(cmp.compile("void a(int a){}"),expected)


#     def test5(self): 
#         expected = [
#             ".global _a",
#             "_a:",
#             "  sub sp, sp, #16", # stack must be 16 bytes aligned
#             "  mov w8, #1",      # stack must be 16 bytes aligned
#             "  str w8, [sp, #12]",
#             "  add sp, sp, #16", # return stack space
#             "  ret"
#         ]
#         self.assertEqual(cmp.compile("void a(){int a = 1;}"),expected)

# if __name__ == "__main__":
#     unittest.main(verbosity=1)


# # ; %bb.0:
# #         sub     sp, sp, #16
# #         mov     w8, #1                          ; =0x1
# #         str     w8, [sp, #12]
# #         add     sp, sp, #16
# #         ret