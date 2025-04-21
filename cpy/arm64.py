import cpy.sem as sem
from cpy.prs import Prs
from cpy.tac import *
from cpy.dbg import *

cmp_mnemonics = {"==": "b.eq", "!=": "b.ne", ">": "b.gt", ">=": "b.ge", "<": "b.lt", "<=": "b.le"}

# debug=True adds a call to _DBG in _main only!
def lower(tac: TACTable,debug=False):
    res = f".global {",".join([f"_{x.id}" for x in tac.functions])}\n"
    res += ".align 2\n\n"

    if debug: tac.functions.append(TACFn("DBG"))

    type_to_bytes = { "int": 4 }

    def prepare_prologue(fn: TACFn):
        ids = fn.id_map.values()
        stack_size = 4 * len(ids) + 8 # 8 for link register
        contains_call = any([isinstance(tac,TACCall) for tac in fn.code])
        if contains_call: stack_size += 8
        address_map = {}
        counter = 4
        for id in ids: 
            address_map[id] = counter
            counter += type_to_bytes["int"]
        stack_size = (stack_size + 15) // 16 * 16 # ensure 16 byte alignment
        return stack_size, address_map

    def process_fn(fn: TACFn):
        nonlocal res
        res += f"_{fn.id}:\n"

        stack_size, stack_address_map = prepare_prologue(fn)
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
            if msg == "b0 = a0":
                pass
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
            if isinstance(left,Const): move("w8", left.value)
            else: load("w8", left)
            if isinstance(right,Const): move("w9", right.value)
            else: load("w9", right)

            if op in cmp_mnemonics:
                res += f"  cmp w8, w9"
            else:
                mnemonic = {"+":"add","*":"mul","-":"sub", "/": "sdiv"}[op]
                res += f"  {mnemonic} w8, w8, w9\n"
                res += f"  str w8, [sp, #{stack_address_map[id]}]\n"

        def assign(tac:TACAssign):
            match tac.value:
                case Const(value=const_val):
                    match tac.op:
                        case "=":
                            move("w8", const_val)
                            store("w8", tac.id)
                        case _: alu(ASSIGN_OPS[tac.op], tac.id, tac.value, tac.id)
                case _:
                    match tac.op:
                        case "=":
                            load("w8", tac.value)
                            store("w8", tac.id)
                        case _: alu(ASSIGN_OPS[tac.op], tac.value, tac.id, tac.id)

        res += f"  str lr, [sp, #-{stack_size}]!\n" # prepare stack and save link register for later

        # load args
        arg_regs = [f"w{x}" for x in range(8)]
        for arg in fn.args: 
            reg = arg_regs.pop(0)
            res += f"  str {reg}, [sp, #{stack_address_map[arg.value]}]; load arg {arg.value}\n\n"
        
        applied_ret = False
        for tac in fn.code:
            comment(str(tac))
            print(type(tac),"\n\n")
            match tac:
                case TACLabel(label=label):
                    res += f"  {label}:"
                case TACJump(target=target):
                    res += f"  b {target}"
                case TACCondJump(value=_,target=target,last_test_op=op):
                    print("taccondtjump", op)
                    res += f"  {cmp_mnemonics[op]} {target}"
                case TACAssign(): assign(tac)
                case TACOp(op=op, left=left, right=right, id=res_id):
                    alu(op, left, right, res_id)
                case TACRet(value=ret_val):
                    if isinstance(ret_val,Const): move("w0", ret_val.value)
                    else: load("w0", ret_val)
                    ret()
                    applied_ret = True
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
        if not applied_ret: ret()

    for fn in tac.functions:
        process_fn(fn)
    return res.strip()

if __name__ == "__main__":
    code =\
    """
    int main() {
        int a = 1;
        int b = 2;
        b = a;
        return b;
    }
    """

    # code = """
    # int main(){if(1!=1){return 1;}return 2;}
    # """

    ast = list(Prs(code).parse())
    sem_res=sem.analyze(ast)
    t = to_tac(sem_res)
    print(t)
    # print(t.functions[0].code)
    asm = lower(t,True)
    print(asm)