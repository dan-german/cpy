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

def run(code, output="a.out"):
    subprocess.run(["clang", "-x", "c", "-", "-o", output], input=code, text=True, check=True)
    subprocess.run(["./" + output], check=True)

if __name__ == "__main__":
    code = r"""
    #include <stdio.h>
    char globalString[] = "Hello, World!";
    int main() { 
        printf("String: %s\n", globalString);
    }
    """
    # run(code)
    dump_llvmir(code)
    # compile_asm(code)
    # dump_pp(code)