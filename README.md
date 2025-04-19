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
    mov w8, #2
    str w8, [sp, #4]
    mov w8, #3
    str w8, [sp, #8]
    ldr w8, [sp, #4]
    ldr w9, [sp, #8]
    mul w8, w8, w9
    str w8, [sp, #12]
    ldr w0, [sp, #12]
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

✅ Functions  
✅ Integer arithmetic  
✅ If/else statements
✅ While statements
🔜 More features coming soon!  