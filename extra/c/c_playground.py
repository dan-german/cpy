import subprocess

def cmd(c: str): subprocess.run(c,shell=True)

def compile_asm(code): 
    args = ["clang", "-x", "c", "-", "-S", "-o", "-", "-Xclang", "-funwind-tables=0"]
    subprocess.run(args, input=code, text=True)

def dump_ast(code):
    args = ["clang", "-Xclang", "-ast-dump", "-fsyntax-only", "-x", "c", "-"]
    subprocess.run(args, input=code, text=True)

def dump_llvmir(code): 
    args = ["clang", "-Xclang", "-emit-llvm", "-S", "-x", "c", "-", "-o", "-", "-O0"]
    subprocess.run(args, input=code, text=True)

if __name__ == "__main__": 
    # void a(int a = 3) {} not allowed
    # int a(){int b(){}} not allowed
    code = """
    int main() { 
    }
"""

    compile_asm(code)
    # dump_ast(code)
    # dump_llvmir(code)