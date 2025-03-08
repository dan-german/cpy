import cpy.sem as sem
from cpy.prs import Prs
from cpy.tac import *
from cpy.dbg import *

def lower(tac: TACTable,sym_table:dict):
    res = ""

    def process_fn(fn: TACFn):
        nonlocal res
        res += f"_{fn.id}:\n"
        stores = list(filter(lambda x: isinstance(x, TACStore),fn.block))
        stack_size = 4 * len(stores) # int is 4 bytes
        res += f"sub sp, sp, #{stack_size}"
        return res


    for fn in tac.functions:
        print(process_fn(fn))

if __name__ == "__main__":
    code = """
    int a(){
        int a=1+2;
    }"""

    ast = list(Prs(code).parse())
    a,b,c,sym_table=sem.analyze(ast)
    # pn(d)

    t = to_tac((a,b,c,sym_table))
    lower(t,sym_table)
    # print(str(t))


        # sub     sp, sp, #16
        # mov     w8, #1                          ; =0x1
        # str     w8, [sp, #12]
        # mov     w8, #2                          ; =0x2
        # str     w8, [sp, #8]
        # ldr     w8, [sp, #12]
        # ldr     w9, [sp, #8]
        # add     w8, w8, w9
        # str     w8, [sp, #4]
        # ldr     w0, [sp, #4]
        # add     sp, sp, #16
        # ret

#a:
#   store G0
#   assign G0, 1
#   store G1
#   assign G1, 2
#   store G2
#   load G0
#   load G1
#   G2 = G0 + G1
#   store a0
#   assign a0, G2