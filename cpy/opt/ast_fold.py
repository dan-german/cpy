from cpy.prs import *
import cpy.dbg as dbg

def fold(bop: BOp):
    if not isinstance(bop, BOp): return bop
    bop.left = fold(bop.left)
    bop.right = fold(bop.right)
    if isinstance(bop.left, Const) and isinstance(bop.right, Const):
        match bop.op: 
            case "+": return Const(str(int(bop.left.value) + int(bop.right.value)))
            case "*": return Const(str(int(bop.left.value) * int(bop.right.value)))
            case "-": return Const(str(int(bop.left.value) - int(bop.right.value)))
            case "/": return Const(str(int(bop.left.value) / int(bop.right.value)))
            case "==": return Const(str(bop.left.value == bop.right.value))
            case "!=": return Const(str(bop.left.value != bop.right.value))
            case "&&": return Const(str(bop.left.value and bop.right.value))
    return bop

if __name__ == "__main__": 
    code = """
    void x() {
        int a = 2;
        int b = 2;
        if (a == b) {
        }
    }
    """
    tree = Prs(code).expr()
    folded = fold(tree)
    dbg.print_ast(folded)