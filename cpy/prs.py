from cpy.lex import Lex, Tok

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

    def unary(self): 
        node = self.l.peek()
        while self.l and self.l.next().value in UOPS: node = (self.l.peek(), node)
        return node

    def parse(self, curr_priority: int = 0):
        node = self.unary()
        while self.l and self.l.peek().priority() >= curr_priority: node = (node, self.l.next(), self.parse(curr_priority))
        return node