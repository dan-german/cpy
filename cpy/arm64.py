import cpy.sem as sem
from cpy.prs import Prs
from cpy.tac import *
from cpy.dbg import *

def lower(tac: TACTable):
    res = f".global {",".join([f"_{x.id}" for x in tac.functions])}\n"
    res += ".align 2\n\n"

    alu = { "+": "add", "*": "mul", "-": "sub" }
    type_to_bytes = { "int": 4 }

    def handle_allocations(fn: TACFn):
        ids = fn.ids.values()
        stack_size = 4 * len(ids)
        contains_call = any([isinstance(tac,TACCall) for tac in fn.block])
        if contains_call: stack_size += 8
        address_map = {}
        counter = 0
        for id in ids: 
            address_map[id] = counter
            counter += type_to_bytes["int"]
        stack_size = (stack_size + 15) // 16 * 16 # ensure 16 byte alignment
        return stack_size, address_map

    def process_fn(fn: TACFn):
        nonlocal res
        res += f"_{fn.id}:\n"

        ids = fn.ids.values()
        stack_size, address_map = handle_allocations(fn)

        if stack_size > 0: 
            res += f"  sub sp, sp, #{stack_size}\n\n"

        for tac in fn.block:
            if isinstance(tac,TACAssign):
                if tac.value in ids:
                    res += f"  ldr w8, [sp, #{address_map[tac.value]}]\n"
                    res += f"  str w8, [sp, #{address_map[tac.id]}]\n\n"
                else:
                    res += f"  mov w8, #{tac.value}\n"
                    res += f"  str w8, [sp, #{address_map[tac.id]}]\n\n"
            elif isinstance(tac,TACOp):
                res += f"  ldr w8, [sp, #{address_map[tac.left]}]\n"
                res += f"  ldr w9, [sp, #{address_map[tac.right]}]\n"
                res += f"  {alu[tac.op]} w8, w8, w9\n"
                res += f"  str w8, [sp, #{address_map[tac.id]}]\n\n"
            elif isinstance(tac,TACRet):
                res += f"  ldr w0, [sp, #{address_map[tac.value]}]\n"
            elif isinstance(tac,TACCall):
                res += f"  str lr, [sp]\n"
                res += f"  bl _{tac.fn}\n"
                res += f"  ldr lr, [sp]\n"

        if stack_size > 0:
            res += f"\n  add sp, sp, #{stack_size}\n\n"

        res += "  ret\n"

    for fn in tac.functions:
        process_fn(fn)

    print()
    return res.strip()

if __name__ == "__main__":
    code = """
    int b() {
        return 2 + 3;
    }
    int main(){
        int a = b();
    }"""

    ast = list(Prs(code).parse())
    a,b,c,sym_table=sem.analyze(ast)
    # pn(d)

    t = to_tac((a,b,c,sym_table))
    print(t)
    print()
    print(lower(t))