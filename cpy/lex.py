from cpy.consts import *

class Peeker():
    def peek(self): return self.iterable[self.pos] if self.pos < len(self.iterable) else None
    def __repr__(self): return self.peek()
    def __iter__(self): return self
    def __bool__(self): return self.pos < len(self.iterable)
    def __init__(self, iterable: str):
        self.iterable = iterable
        self.pos = 0
    def __next__(self): 
        if self.pos >= len(self.iterable): raise StopIteration
        value = self.iterable[self.pos]
        self.pos += 1
        return value
    
class Lex:
    def __init__(self, input): self.peeker = Peeker(input)
    def __iter__(self): return self
    def __next__(self):
        if not self.peeker: raise StopIteration

        self.skip_whitespace()
    
        while self.peeker:
            next_char = self.peeker.peek()
            if next_char.isdigit(): return self.collect_num()
            elif next_char in OPERATORS: return self.collect_while(lambda char: char in OPERATORS), "op"
            elif next_char.isalpha(): 
                token = self.collect_while(lambda char: char.isalnum())
                if token in PRIMITIVES: return token, "type"
                elif token == "return": return token, "op"
                return token, "id"
            next(self.peeker)
        return None
    
    def collect_while(self, action):
        buffer = ""
        while self.peeker and action(self.peeker.peek()): 
            buffer += next(self.peeker)
        return buffer

    def collect_num(self): 
        buffer = ""
        type = "int"
        while self.peeker and self.peeker.peek().isdigit() or self.peeker.peek() == ".": 
            buffer += next(self.peeker)
            if self.peeker.peek() == ".": type = "double"
        if self.peeker.peek() == "f": 
            type = "float"
            next(self.peeker)
        return buffer, f"{type}_literal"

    def skip_whitespace(self): 
        while self.peeker.peek() == SPACE: next(self.peeker)