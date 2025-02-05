SPACE = " "
TAB = SPACE * 4
NL = "\n"
OPERATORS = {
    "+": "addition",
    "-": "subtraction",
    "*": "multiplication",
    "/": "division",
    "%": "modulus",
    "++": "increment",
    "--": "decrement",
    "=": "assignment",
    "+=": "add and assign",
    "-=": "subtract and assign",
    "*=": "multiply and assign",
    "/=": "divide and assign",
    "%=": "modulus and assign",
    "==": "equal to",
    "!=": "not equal to",
    ">": "greater than",
    "<": "less than",
    ">=": "greater than or equal to",
    "<=": "less than or equal to",
    "&&": "logical AND",
    "||": "logical OR",
    "!": "logical NOT",
    "&": "bitwise AND",
    "|": "bitwise OR",
    "^": "bitwise XOR",
    "~": "bitwise NOT",
    "<<": "left shift",
    ">>": "right shift",
    "&=": "bitwise AND and assign",
    "|=": "bitwise OR and assign",
    "^=": "bitwise XOR and assign",
    "<<=": "left shift and assign",
    ">>=": "right shift and assign",
    "? :": "ternary conditional",
    ",": "comma",
    "->": "structure pointer",
    ".": "structure member access",
    "()": "function call",
    "[]": "array subscript",
    "* (dereference)": "pointer dereference",
    "& (address-of)": "address-of operator",
    "sizeof": "size of type/operator",
    "typeof": "type of (GCC extension)",
    "_Alignof": "alignment requirement of type",

    # end official operators
    "(": "begin argument list",
    ")": "end argument list",
    "{": "open scope",
    "}": "close scope",
    ";": "end of statement"
}

PRIMITIVES = [
    "int"
]