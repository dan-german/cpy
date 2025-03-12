asm =\
"""
.global _b,_main
.align 2

_b:
  sub sp, sp, #16

  mov w8, #2
  str w8, [sp, #0]

  mov w8, #3
  str w8, [sp, #4]

  ldr w8, [sp, #0]
  ldr w9, [sp, #4]
  add w8, w8, w9
  str w8, [sp, #8]

  ldr w0, [sp, #8]

  add sp, sp, #16

  ret
_main:
  sub sp, sp, #16

  str lr, [sp]
  bl _b
  ldr lr, [sp]
  ldr w8, [sp, #0]
  str w8, [sp, #4]

  add sp, sp, #16

  ret
"""

# import subprocess

# def compile_assembly_to_object(assembly_file, output_file):
#     """Compile ARM64 assembly to an object file using clang."""
#     try:
#         subprocess.run([
#             "clang",
#             #"-target", "aarch64",  # Target ARM64 architecture
#             "-c", assembly_file,   # Compile to object file
#             "-o", output_file
#         ], check=True)
#     except subprocess.CalledProcessError as e:
#         print(f"Error compiling assembly: {e}")
#         return False
#     return True