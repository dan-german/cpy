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
    int main() {
        volatile int x = 2;
        if (x > 2 > 1) { 
            return 444;
        }
        return 999;
    }
    """
    # dump_ast(code)
    # run(code)
    # dump_llvmir(code)
    compile_asm(code)
    # dump_pp(code)


#             .section        __TEXT,__text,regular,pure_instructions
#         .build_version macos, 15, 0     sdk_version 15, 2
#         .globl  _main                           ; -- Begin function main
#         .p2align        2
# _main:                                  ; @main
# ; %bb.0:
#         sub     sp, sp, #16
#         str     wzr, [sp, #12]
#         mov     w8, #2                          ; =0x2
#         str     w8, [sp, #8]
#         ldr     w8, [sp, #8]
#         subs    w8, w8, #2
#         cset    w8, ne
#         tbnz    w8, #0, LBB0_2
#         b       LBB0_1
# LBB0_1:
#         ldr     w8, [sp, #8]
#         lsl     w8, w8, #3
#         str     w8, [sp, #8]
#         b       LBB0_2
# LBB0_2:
#         ldr     w0, [sp, #8]
#         add     sp, sp, #16
#         ret