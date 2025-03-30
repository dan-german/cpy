import cpy.sem as sem
from cpy.prs import Prs
from cpy.tac import *
from cpy.dbg import *

cmp_mnemonics = {"==": "beq", "!=": "bne", ">": "bgt", ">=": "bge", "<": "blt", "<=": "ble"}

def lower(tac: TACTable,debug=False):
    res = f".global {",".join([f"_{x.id}" for x in tac.functions])}\n"
    res += ".align 2\n\n"

    if debug: tac.functions.append(TACFn("DBG"))

    type_to_bytes = { "int": 4 }

    def prepare_prologue(fn: TACFn):
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

        stack_size, stack_address_map = prepare_prologue(fn)
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
        
        def ret(): 
            nonlocal res
            if debug and fn.id == "main": res += "  bl _DBG\n"
            res += f"  ldr lr, [sp]\n"
            res += f"\n  add sp, sp, #{stack_size}\n\n"
            res += "  ret\n"

        def alu(op:str,left,right,id):
            nonlocal res
            load("w8", left)
            load("w9", right)

            if op in cmp_mnemonics:
                res += f"  cmp w8, w9"
            else:
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
            print(tac)
            match tac:
                case TACLabel(label=label):
                    res += f"  {label}:"
                case TACGoto(label=label):
                    res += f"  b {label}"
                case TACIf(value=_,label=label,last_test_op=op):
                    print("last", op)
                    res += f"  {cmp_mnemonics[op]} {label}"
                case TACAssign(value=TACRef(id=ref_id)):
                    load("w8", ref_id)
                    store("w8", tac.id)
                case TACAssign(value=Const(value=const_val)):
                    move("w8", const_val)
                    store("w8", tac.id)
                case TACOp(op=op, left=left, right=right, id=res_id):
                    alu(op, left, right, res_id)
                case TACRet(value=ret_val):
                    load("w0", ret_val)
                    ret()
                case TACCall(fn=fn_name, args=args, return_value_id=ret_id):
                    arg_regs = [f"w{x}" for x in range(8)]
                    for arg in args:
                        reg = arg_regs.pop(0)
                        if isinstance(arg, Const):
                            res += f"  mov {reg}, #{arg.value}; set arg {arg.value}\n"
                        else:
                            res += f"  mov {reg}, [sp,#{stack_address_map[arg.id]}]; set arg {arg.id}\n"
                    res += f"  bl _{fn_name}\n"
                    if ret_id:
                        store("w0", ret_id)

        ret()

    for fn in tac.functions:
        process_fn(fn)
    return res.strip()

if __name__ == "__main__":
        # if (3>2>1) { return 1; }
    code = """
    int main() { 
    int x = 
        return 2;
    }
    """
    ast = list(Prs(code).parse())
    a,b,c,sym_table=sem.analyze(ast)
    t = to_tac((a,b,c,sym_table))
    # print(t)
    # print()
    asm = lower(t,True)
    # print()
    print(asm)