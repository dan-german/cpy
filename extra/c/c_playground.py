import subprocess

def cmd(c: str): subprocess.run(c,shell=True)

def compile_asm(code): 
    args = ["clang", "-x", "c", "-", "-S", "-o", "-", "-Xclang", "-funwind-tables=0"]
    subprocess.run(args, input=code, text=True)

def dump_ast(code):
    args = ["clang", "-Xclang", "-ast-dump", "-fsyntax-only", "-x", "c", "-"]
    subprocess.run(args, input=code, text=True)

if __name__ == "__main__": 
    code = """

    int a() {
        {
           {
               int b = 10;
               b += 1; 
           }
           b += 2;
        }
    }

    """

    compile_asm(code)
    # dump_ast(code)