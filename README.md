# cpy  

**cpy** is a minimal, naive C to Apple Silicon ARM64 compiler.  

## Example  

```python
from cpy import compile

code = """
int main() {
    return 2 * 3;
}
"""
print(compile(code))
```

### Output (ARM64 Assembly)  

```assembly
.global _main
.align 2

_main:
    str lr, [sp, #-32]!

    // G0 = Const(2)
    mov w8, #2
    str w8, [sp, #4]  // store G0

    // G1 = Const(3)
    mov w8, #3
    str w8, [sp, #8]  // store G1

    // G2 = G0 * G1
    ldr w8, [sp, #4]  // load G0
    ldr w9, [sp, #8]  // load G1
    mul w8, w8, w9
    str w8, [sp, #12] // store G2

    // return G2
    ldr w0, [sp, #12] // load G2
    ldr lr, [sp]

    add sp, sp, #32
    ret
```

## Running the Compiled Code  

If you're on an Apple Silicon Mac, you can run the generated assembly using:  

```python
from test.test_e2e import debug

print(debug(code))  # Outputs: 6
```

## Features  

✅ Stack-based loads and stores  
✅ Integer arithmetic  
✅ Function prologue/epilogue  
🔜 More features coming soon!  

