from cpy.lex import Lex, Tok
from cpy.classes import *
from cpy.debug import *

UOPS = { "++", "--", "+", "-", "+=", "-=" }
PREC_MAP = { 
    "=": 1,
    "+=": 1,
    "-=": 1,
    "+": 1,
    "-": 1,
    "*": 2,
    "/": 2
}

class Prs:
    def peek(self): return self.l.peek()
    def next(self): return self.l.next()
    def curr(self): return self.l.curr()
    def right_asc(self,op): return op.value in ["=", "+=", "-="]
    def get_prec(self,input): return PREC_MAP[input.value if isinstance(input, Tok) else input]

    def __init__(self, code: str):
        self.l = Lex(code)
        Tok.priority = lambda self: PREC_MAP[self.value]

    def uop(self) -> UOp:
        if self.peek().value == "(": self.next(); expr = self.expr(); self.next(); return expr
        node = UOp(self.next().value, None)
        while self.l and self.curr().value in UOPS: 
            node.operand = self.uop()

        if self.peek():
            match self.peek().type:
                case "NUM": return Const(self.next().value) 
                case "ID": return Ref(self.next().value) 
        return node

    def expr(self,left=None,prc=0):
        left = left if left else self.uop()
        while self.peek() and self.peek().value != ")" and self.get_prec(self.peek()) >= prc:
            op = self.next()
            right = self.uop()
            if self.peek() and self.peek().value != ")" and (self.get_prec(self.peek()) > self.get_prec(op) or self.right_asc(op)):
                left = BOp(op.value, left, self.expr(right, self.get_prec(self.peek())))
                continue
            left = BOp(op.value, left, right)
        return left