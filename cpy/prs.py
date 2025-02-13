from cpy.lex import Lex, Tok
from cpy.classes import *
from cpy.debug import *

UOPS = { "++", "--", "+", "-" }
PREC_MAP = { 
    "=": 1,
    "+=": 1,
    "-=": 1,
    "+": 3,
    "-": 3,
    "*": 4,
    "/": 4,
    "++": 5, 
    "--": 5,
}

class Prs:
    def __repr__(self): return f"lex at: {self.lex.curr()}"
    def __init__(self, code: str): self.lex = Lex(code)
    def peek(self): return self.lex.peek()
    def right_associative(self,op): return op.value in ["=", "+=", "-="]
    def is_assignment(self): return self.peek().value in ["=", "+=", "-="] 
    def get_prec(self,input): return PREC_MAP[input.value if isinstance(input, Tok) else input]
    def eatable(self): return self.lex.peek() and self.lex.peek().value not in [")", ";", ",", "}"]
    def next_precedence(self): return self.get_prec(self.peek())
    def is_type(self, st: str): return st in ["int"]

    def eat(self, *, value = "", type=""): 
        next_tok = next(self.lex)
        if value: assert next_tok.value == value, f"Expected '{value}', got '{next_tok.value}'"
        if type: assert next_tok.type == type, f"Expected '{type}', got '{next_tok.type}'"
        return next_tok

    def uop(self) -> UOp:
        match self.peek().type:
            case "NUM": return Const(self.eat().value) 
            case "ID": 
                id = Ref(self.eat().value)
                if self.peek() and self.peek().value == "(": 
                    return self.call(id)
                return id

        if self.peek().value == "(": self.eat(); expr = self.expr(); self.eat(); return expr
        node = UOp(self.eat().value, None)
        while self.lex and self.lex.curr().value in UOPS: 
            node.operand = self.uop()
        return node

    def expr(self,left=None,prc=0):
        left = left if left else self.uop()
        p = self.peek()
        while self.eatable() and self.next_precedence() >= prc:
            op = self.eat(type="OP")
            right = self.uop()
            if self.eatable() and (self.next_precedence() > self.get_prec(op) or self.right_associative(op)):
                left = BOp(op.value, left, self.expr(right, self.get_prec(self.peek())))
                continue
            left = BOp(op.value, left, right)
        return left

    def args(self): 
        args = []
        self.eat(value="(")
        while self.peek().value != ")":
            args.append(Arg(self.eat(type="KEYWORD").value, self.eat(type="ID").value))
            if self.peek().value != ")": self.eat(value=",")
        self.eat(value=")")
        return args

    def fn(self, type, id):
        args = self.args()
        self.eat(value="{")
        body = []
        while self.eatable(): body.append(self.stmnt())
        self.eat(value="}")
        func = Func(id, type, args, body)
        return func

    def variable(self, type, id): 
        self.eat(value="=")
        vr = Var(id, type, self.expr())
        self.eat(value=";")
        return vr

    def decl(self):
        type = self.eat(type="KEYWORD").value
        id = self.eat(type="ID").value
        res = self.fn(type, id) if self.peek().value == "(" else self.variable(type,id)
        return res

    def call(self, id): 
        args = []
        self.eat(value="(")
        while self.eatable():
            args.append(self.expr())
            if self.peek().value == ",": self.eat()
        self.eat(value=")")
        return Call(id, args)

    def ret(self): 
        self.eat(value="return")
        r = Return(self.expr())
        self.eat(value=";")
        return r

    def stmnt(self):
        while self.eatable():
            if self.is_type(self.peek().value): return self.decl()
            elif self.peek().value == "return": return self.ret()
            elif self.peek().type == "ID":
                id = Ref(self.eat().value)
                if self.peek() and self.peek().value == "(":
                    call = self.call(id)
                    self.eat(value=";")
                    return call
                elif self.peek() and self.is_assignment():
                    exp = self.expr(id)
                    self.eat(value=";")
                    return exp
                return self.expr(id)
            return self.expr()

    def parse(self): 
        stmnts = []
        while self.lex: 
            stmnts.append(self.stmnt())
        return stmnts