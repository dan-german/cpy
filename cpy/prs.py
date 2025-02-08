from cpy.lex import Lex, Tok
from cpy.classes import *

UOPS = { "++", "--", "+", "-" }
BINOP_PRIORITY = { 
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2
}

class Prs: 
    def __init__(self, code: str): 
        self.l = Lex(code)
        Tok.priority = lambda self: BINOP_PRIORITY[self.value]
    
    def parse(self):
        def curr(): return self.l.curr()
        def next(): return self.l.next()
        def peek(): return self.l.peek()

        def uop() -> UOp:
            if peek().type == "NUM": 
                return Const(next().value)

            node = UOp(next().value, None)
            while self.l and curr().value in UOPS: 
                node.operand = uop()

            return node

        def body(): 
            print("funcy func")
            pass

        def peek_priority_greater(priority):
            return peek().value in BINOP_PRIORITY and peek().priority() > priority

        def expr(curr_priority: int = 0):
            if peek().value == "(":
                next(); left = expr(); next()
            else: 
                left = uop() 
            while self.l and peek().value not in [";", ")"] and peek_priority_greater(curr_priority):
                op = next()
                if peek().value == "(": 
                    next(); right = expr(); next()
                else: 
                    right = expr(BINOP_PRIORITY[op.value])
                left = BinOp(op.value, left, right)
            return left

        def decl(): 
            type = curr().value
            id = next().value
            if peek().value == "=":
                next()
                return VarDecl(id, type, expr())
            elif peek().value == "(":
                return body()
            else:
                raise Exception("Invalid syntax")

        return decl()