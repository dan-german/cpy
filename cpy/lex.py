import re

RE_MAP = {
    'COMMENT': r'//.*?$|/\*[\s\S]*?\*/',
    'KEYWORD': r'\b(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)\b',
    'ID': r'\b[a-zA-Z_][a-zA-Z\d_]*\b',
    'NUM': r'\d+(\.\d*)?',
    'STR': r'"([^"\\]*(\\.[^"\\]*)*)"',
    'CHAR': r"'.'",
    'OP': r'(\+\+|--|==|!=|<<=|>>=|<=|>=|->|\+|-|\*|/|%|=|<|>|\||\^|&|!|~|\?|:|\.\.\.)',
    'PUNCTUATION': r'[\(\)\{\}\[\];,]',
    'WHITESPACE': r'\s+',
}

pattern = "|".join(f"(?P<{name}>{rgx})" for name, rgx in RE_MAP.items())

class Tok: 
    def __repr__(self): return f"{self.category, self.value}"
    def __init__(self, match: re.Match[str]): 
        self.category = match.lastgroup
        self.value = match.group(match.lastgroup)

class Lex:
    def __init__(self, code: str): 
        self.it = (Tok(match) for match in re.finditer(pattern, code) if match.lastgroup != "WHITESPACE")
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
    def current(self): return self._current if self._current else self.next()
    def peek(self): return self.temp if self.temp else self.next()
    def next(self): return next(self)