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

if __name__ == "__main__":
    code = """
    int b() { return 4; }
    int a() { return b(); }
    int main(){
        return a() + 1;
    }"""
    # dump_llvmir(code)
    compile_asm(code)