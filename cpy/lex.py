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

class Lex:
    def __init__(self, code: str): 
        self.it = (match for match in re.finditer(pattern, code) if match.lastgroup != "WHITESPACE")
    def __iter__(self): 
        return self
    def __next__(self): 
        match = next(self.it)
        return match.lastgroup, match.group(match.lastgroup)