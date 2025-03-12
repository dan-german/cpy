import subprocess

def compile_asm(code): 
    args = ["clang", "-x", "c", "-", "-S", "-o", "-", "-Xclang", "-funwind-tables=0"]
    subprocess.run(args, input=code, text=True)

def dump_ast(code):
    args = ["clang", "-Xclang", "-ast-dump", "-fsyntax-only", "-x", "c", "-"]
    subprocess.run(args, input=code, text=True)

def dump_llvmir(code): 
    args = ["clang", "-Xclang", "-emit-llvm", "-S", "-x", "c", "-", "-o", "-", "-O0"]
    subprocess.run(args, input=code, text=True)

# dump post preprocessor
def dump_pp(code): 
    subprocess.run("clang -E -", input=code, shell=True,text=True)

if __name__ == "__main__":
    code = """
    int b(int a, int c) {return a * 2 * c;}
    int main() {int sh = 4; b(1,sh);}
    """
    # dump_llvmir(code)
    compile_asm(code)
    # dump_pp(code)