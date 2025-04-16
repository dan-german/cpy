from cpy.lex import Lex, Tok
from cpy.ast_models import *
from cpy.dbg import *

ASSIGN_OPS = ["=", "+=", "-=", "*="]
UOPS = { "++", "--", "+", "-", "*", "&" }
PREC_MAP = { 
    "=": 1, "+=": 1, "-=": 1, "*=": 1, "==": 1, ">=": 1, "<=": 1, "!=": 1, "<": 1, ">": 1,
    "+": 3, "-": 3, 
    "*": 4, "/": 4,
    "++": 5, "--": 5
}

class Prs:
    def __repr__(self): return f"lex at: {self.lex.curr()}"
    def __init__(self, code: str): self.lex = Lex(code)
    def peek(self): return self.lex.peek()
    def eatable(self): return self.lex.peek() and self.lex.peek().value not in [")", ";", ",", "}"] #TODO: what's eatable changes depending on context so it's best refactoring this

    def eat(self, *, value = "", type=""): 
        next_tok = next(self.lex)
        if value: assert next_tok.value == value, f"Expected '{value}', got '{next_tok.value}'"
        if type: assert next_tok.type == type, f"Expected '{type}', got '{next_tok.type}'"
        return next_tok

    def uop(self) -> UOp:
        match self.peek().type:
            case "NUM": return Const(self.eat().value) 
            case "ID": 
                id = self.eat().value
                if self.peek() and self.peek().value == "(": 
                    return self.call(id)
                return Ref(id)

        if self.peek().value == "(": self.eat(); expr = self.expr(); self.eat(); return expr
        if not self.eatable(): return None
        node = UOp(self.eat().value, None)
        while self.lex and self.lex.curr().value in UOPS: 
            node.operand = self.uop()
        return node

    def expr(self,left=None,precedence=0):
        def get_precedence(input): return PREC_MAP[input.value if isinstance(input, Tok) else input]
        def next_precedence(): return get_precedence(self.peek())
        def right_associative(op): return op.value in ["=", "+=", "-="]

        left = left if left else self.uop()
        while self.eatable() and next_precedence() >= precedence:
            op = self.eat(type="OP")
            right = self.uop()
            if self.eatable() and (next_precedence() > get_precedence(op) or right_associative(op)):
                left = BOp(op.value, left, self.expr(right, get_precedence(self.peek())))
                continue
            left = BOp(op.value, left, right)
        return left

    def args(self): # TODO - Support function pointers
        args = []
        self.eat(value="(")
        while self.peek().value != ")":
            args.append(Arg(self.eat(type="KEYWORD").value, self.eat(type="ID").value))
            if self.peek().value != ")": self.eat(value=",")
        self.eat(value=")")
        return args

    def fn(self, type, id):
        args = self.args()
        body = self.scope()
        return Fn(id, type, args, body)

    def var_(self, type, id): 
        if self.peek().value == "=": self.eat(value="=")
        vr = Var(id, type, self.expr())
        self.eat(value=";")
        return vr

    def decl(self):
        type = self.eat(type="KEYWORD").value
        if self.peek().value == "*": 
            type += self.eat().value
        id = self.eat(type="ID").value
        res = self.fn(type, id) if self.peek().value == "(" else self.var_(type,id)
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
        r = Ret(self.expr())
        self.eat(value=";")
        return r

    def id_(self): 
        id = self.eat(type="ID").value
        if self.peek() and self.peek().value == "(":
            call = self.call(id)
            self.eat(value=";")
            return call
        elif self.peek() and self.peek().value in ASSIGN_OPS:
            exp = self.expr(Ref(id))
            self.eat(value=";")
            return exp
        ref=self.expr(Ref(id))
        self.eat(value=";")
        return ref

    def if_(self):
        self.eat(value="if")
        self.eat(value="(")
        test = self.expr()
        self.eat(value=")")
        if_stmnt = If(test, self.scope())
        if self.peek() and self.peek().value == "else":
            self.eat(value="else")
            if self.peek().value == "if": 
                if_stmnt.else_ = self.if_()
            elif self.peek().value == "{":
                if_stmnt.else_ = self.scope()
            else: 
                if_stmnt.else_ = list(self.parse("}"))
        return if_stmnt

    def scope(self): 
        self.eat(value="{")
        return Scope(list(self.parse("}")))

    def stmnt(self):
        def is_type(st: str): return st in {"int", "float", "void"}
        while self.eatable():
            match self.peek():
                case token if is_type(token.value): return self.decl()
                case token if token.value == "return": return self.ret()
                case token if token.type == "ID": return self.id_()
                case token if token.value == "if": return self.if_()
                case token if token.value == "{": return self.scope()
            return self.expr()

    def parse(self, terminal_value: str = None): 
        while self.peek() and self.peek().value != terminal_value: 
            yield self.stmnt()
        if terminal_value: self.eat(value=terminal_value)

if __name__ == "__main__":
    code =\
    """
    if (true) {}
    """
    res = list(Prs(code).parse())
    import dbg
    dbg.pn(res)
    
    print(res)