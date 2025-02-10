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
    def __repr__(self): return f"lex at: {self.lex.curr()}"
    def __init__(self, code: str): self.lex = Lex(code)
    def peek(self): return self.lex.peek()
    def right_associative(self,op): return op.value in ["=", "+=", "-="]
    def get_prec(self,input): return PREC_MAP[input.value if isinstance(input, Tok) else input]
    def next_is_consumable(self): return self.peek().value 
    def has_tokens(self): return self.lex.peek() and self.lex.peek().value not in [")", ";"]
    def next_precedence(self): return self.get_prec(self.peek())
    def is_type(self, st: str): return st in ["int"]

    def consume(self, *, val = "", type=""): 
        next_tok = next(self.lex)
        if val: assert next_tok.value == val, f"Expected '{val}', got '{next_tok.value}'"
        if type: assert next_tok.type == type, f"Expected '{type}', got '{next_tok.type}'"
        return next_tok

    def uop(self) -> UOp:
        if self.peek().value == "(": self.consume(); expr = self.expr(); self.consume(); return expr
        node = UOp(self.consume().value, None)
        while self.lex and self.lex.curr().value in UOPS: 
            node.operand = self.uop()

        if self.peek():
            match self.peek().type:
                case "NUM": return Const(self.consume().value) 
                case "ID": return Ref(self.consume().value) 
        return node

    def expr(self,left=None,prc=0):
        left = left if left else self.uop()
        while self.has_tokens() and self.next_precedence() >= prc:
            op = self.consume(type="OP")
            right = self.uop()
            if self.has_tokens() and (self.next_precedence() > self.get_prec(op) or self.right_associative(op)):
                left = BOp(op.value, left, self.expr(right, self.get_prec(self.peek())))
                continue
            left = BOp(op.value, left, right)
        return left

    def args(self): 
        args = []
        self.consume(val="(")
        while self.peek().value != ")":
            args.append(Arg(self.consume(type="KEYWORD").value, self.consume(type="ID").value))
            if self.peek().value != ")": self.consume(val=",")
        self.consume(val=")")
        return args

    def func(self, type, id):
        args = self.args()
        self.consume(val="{")
        body = self.parse()
        return Func(id, type, args, body)

    def variable(self, type, id): 
        self.consume(val="=")
        return Var(id, type, self.expr())

    def decl(self):
        type = self.consume(type="KEYWORD").value
        id = self.consume(type="ID").value
        res = self.func(type, id) if self.peek().value == "(" else self.variable(type,id)
        assert self.consume().value in [";", "}"]
        return res

    def parse(self):
        statements = []
        while self.has_tokens():
            if self.is_type(self.peek().value):
                statements.append(self.decl())
            elif self.peek().type == "ID":
                statements.append(self.expr())
            else: break
        return statements

# code = """
# int f(int a, int b) {
#     int a = 1;
#     int a = 2;
# }
# """
# prs = Prs(code)
# print(prs.parse())
# exit()