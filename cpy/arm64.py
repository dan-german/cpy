import cpy.sem as sem
from cpy.prs import Prs
from cpy.tac import *
from cpy.dbg import *

def lower(tac: TACTable,debug=False):
    res = f".global {",".join([f"_{x.id}" for x in tac.functions])}\n"
    res += ".align 2\n\n"

    if debug: tac.functions.append(TACFn("DBG"))

    type_to_bytes = { "int": 4 }

    def handle_allocations(fn: TACFn):
        ids = fn.ids.values()
        stack_size = 4 * len(ids) + 8 # 8 for link register
        contains_call = any([isinstance(tac,TACCall) for tac in fn.block])
        if contains_call: stack_size += 8
        address_map = {}
        counter = 4
        for id in ids: 
            print(f"id: {id}")
            address_map[id] = counter
            counter += type_to_bytes["int"]
        stack_size = (stack_size + 15) // 16 * 16 # ensure 16 byte alignment
        return stack_size, address_map

    def process_fn(fn: TACFn):
        nonlocal res
        res += f"_{fn.id}:\n"

        ids = fn.ids.values()
        stack_size, stack_address_map = handle_allocations(fn)
        print(f"stack size: {stack_size}")
        indent = " "*2
        
        def store(register:str,id:str):
            nonlocal res
            stack_id = stack_address_map[id]
            res += f"{indent}str {register}, [sp, #{stack_id}]{f"; store {id}"}\n"

        def load(register:str,id:str):
            nonlocal res
            stack_id = stack_address_map[id]
            res += f"{indent}ldr {register}, [sp, #{stack_id}]{f"; load {id}"}\n"

        def move(register:str,immediate:str):
            nonlocal res
            res += f"{indent}mov {register},  #{immediate}{f"; ={immediate}"}\n"

        def comment(msg:str):
            nonlocal res
            res += f"\n{indent}// {msg}\n\n"

        def alu(op:str,left,right,id):
            nonlocal res
            load("w8", left)
            load("w9", right)
            mnemonic = {"+":"add","*":"mul","-":"sub"}[op]
            res += f"  {mnemonic} w8, w8, w9\n"
            res += f"  str w8, [sp, #{stack_address_map[id]}]\n"

        res += f"  str lr, [sp, #-{stack_size}]!\n" # prepare stack and save link register for later

        # load args
        arg_regs = [f"w{x}" for x in range(8)]
        for arg in fn.args: 
            reg = arg_regs.pop(0)
            res += f"  str {reg}, [sp, #{stack_address_map[arg]}]; load arg {arg}\n\n"

        for tac in fn.block:
            comment(str(tac))
            if isinstance(tac,TACAssign):
                if isinstance(tac.value, TACRef): 
                    load("w8",tac.value.id)
                    store("w8",tac.id)
                elif isinstance(tac.value, Const): 
                    move("w8",tac.value.value)
                    store("w8",tac.id)
            elif isinstance(tac,TACOp): alu(tac.op,tac.left,tac.right,tac.id)
            elif isinstance(tac,TACRet): load("w0",tac.value)
            elif isinstance(tac,TACCall):
                # set args
                arg_regs = [f"w{x}" for x in range(8)]
                for arg in tac.args:
                    reg = arg_regs.pop(0)
                    if isinstance(arg,Const):
                        res += f"  mov {reg}, #{arg.value}; set arg {arg.value}\n"
                    else:
                        res += f"  mov {reg}, [sp,#{stack_address_map[arg.id]}]; set arg {arg.id}\n"
                res += f"  bl _{tac.fn}\n"
                if tac.return_value_id:
                    store("w0",tac.return_value_id)

        if debug and fn.id == "main": res += "  bl _DBG\n"
        res += f"  ldr lr, [sp]\n"
        res += f"\n  add sp, sp, #{stack_size}\n\n"
        res += "  ret\n"

    for fn in tac.functions:
        process_fn(fn)
    return res.strip()

"""
_b:                        
        sub     sp, sp, #16

        str     w0, [sp, #12]
        ldr     w8, [sp, #12]
        lsl     w0, w8, #1
        add     sp, sp, #16
        ret
_a:     
        sub     sp, sp, #32
        stp     x29, x30, [sp, #16]             ; 16-byte Folded Spill
        add     x29, sp, #16
        mov     w0, #1                          ; =0x1
        bl      _b
        ldur    w0, [x29, #-4]
        ldp     x29, x30, [sp, #16]             ; 16-byte Folded Reload
        add     sp, sp, #32
        ret
"""

# TODO: params
if __name__ == "__main__":
    code = """
    void bp() {}
    void main(){
        int x = 2;
        int a = x * x;
        bp();
    }
    """

    ast = list(Prs(code).parse())
    a,b,c,sym_table=sem.analyze(ast)
    # pn(d)

    t = to_tac((a,b,c,sym_table))
    print(t)
    print()
    asm = lower(t,True)
    print()
    print(asm)