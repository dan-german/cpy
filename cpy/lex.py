import re
from dataclasses import dataclass

RE_MAP = {
    'COMMENT': r'//.*?$|/\*[\s\S]*?\*/',
    'KEYWORD': r'\b(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)\b',
    'ID': r'\b[a-zA-Z_][a-zA-Z\d_]*\b',
    'NUM': r'\d+(\.\d*)?',
    'STR': r'"([^"\\]*(\\.[^"\\]*)*)"',
    'CHAR': r"'.'",
    'OP': r'(\+\+|\+=|-=|--|==|!=|<<=|>>=|<=|>=|->|\+|-|\*|/|%|=|<|>|\||\^|&|!|~|\?|:|\.\.\.)',
    'PUNCTUATION': r'[\(\)\{\}\[\];,]',
    'WHITESPACE': r'\s+',
}

pattern = "|".join(f"(?P<{name}>{rgx})" for name, rgx in RE_MAP.items())

@dataclass
class Tok: 
    type: str
    value: str

class Lex:
    def __init__(self, code: str): 
        self.it = (Tok(m.lastgroup, m.group(m.lastgroup)) for m in re.finditer(pattern, code) if m.lastgroup != "WHITESPACE")
        self._current = None
        self.temp = next(self.it)
    def __iter__(self): return self
    def __bool__(self): return self.temp != None
    def __next__(self): 
        self._prev = self._current
        self._current = self.temp
        self.temp = next(self.it, None)
        return self._current
    def prev(self): return self._prev
    def curr(self): return self._current if self._current else self.next()
    def peek(self): return self.temp if self.temp else self.next()
    def next(self): return next(self)