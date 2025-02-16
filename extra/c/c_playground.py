import subprocess


code = """
int f(int a) { return 3 * a; }
"""

def cmd(c: str): 
    print(subprocess.run(c,shell=True))

def compile_asm(code): 
    args = ["clang", "-x", "c", "-", "-S", "-o", "-", "-Xclang", "-funwind-tables=0"]
    subprocess.run(args, input=code, text=True)

if __name__ == "__main__": 

    n = 1
    code = """
    void a() {
        int a = 1;
        {   
            int a = 2; 
        }
    }
    """

    compile_asm(code)