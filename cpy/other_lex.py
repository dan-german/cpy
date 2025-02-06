import re

TOKEN_RE_MAP = {
    'KEYWORD': r'''\b(auto|break|case|char|const|continue|default|do|double|else|enum|extern|float|for|goto|if|int|
                    long|register|return|short|signed|sizeof|static|struct|switch|typedef|union|unsigned|void|volatile|while)''',
    'IDENTIFIER': r'\b[a-zA-Z_][a-zA-Z0-9_]*\b',
    'NUMBER': r'\b\d+(\.\d+)?\b',
    'STRING': r'"([^"\\]*(\\.[^"\\]*)*)"',
    'CHAR': r"'.'",
    'OPERATOR': r'(\+\+|--|==|!=|<=|>=|->|\+|-|\*|/|%|=|<|>|\||\^|&|!|~|\?|:|\.\.\.)',
    'PUNCTUATION': r'[\(\)\{\}\[\];,]',
    'WHITESPACE': r'\s+',
    'COMMENT': r'//.*?$|/\*[\s\S]*?\*/'
}

class Lex:
    def __iter__(self): return self
    def __init__(self, program: str): 
        self.program = program
        pattern = "|".join(f"(?P<{name}>{regex})" for name, regex in TOKEN_RE_MAP.items())
        self.iterator = (match for match in re.finditer(pattern, program) if match.lastgroup != "WHITESPACE")
    def __next__(self):
        nxt = next(self.iterator)
        return nxt.lastgroup, nxt.group(nxt.lastgroup)