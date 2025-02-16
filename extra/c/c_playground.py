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
        # for i in range(n): 
        params = ",".join(f"int a{x}" for x in range(n))
        code = f"""
        int f({params}) {{}}
        """

        # print(code)
        compile_asm(code)