import unittest
import cpy.cpy as cpy
import subprocess
import random

def debug(code:str):
    arm64 = cpy.compile(code,debug=True)
    args = ["clang", "-x", "assembler","-"]
    subprocess.run(args, input=arm64, text=True)
    # This places a breakpoint at DBG label and prints out x0's content to stdout
    cmd = """value=$(lldb a.out -o "b DBG" -o "run" -o "script print(int(lldb.frame.FindRegister('x0').GetValue(), 16))" -o "exit" | tail -2) && echo $value"""
    output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    return int(output.stdout.split()[0])

class TestE2E(unittest.TestCase): # TODO - make fast

    def test_return_value_sanity(self):
        for i in range(0, 2**32, 2**29):
            self.assertEqual(i, int(debug(f"int main(){{return {i};}}")))
            
    def test_arith(self):
        MAX = (2^32-1)//2
        for _ in range(0, 2):
            x = random.randint(0,MAX)
            self.assertEqual(x*x, int(debug(f"int main(){{return {x}*{x};}}")))
            x = random.randint(0,MAX)
            self.assertEqual(x*x+x, int(debug(f"int main(){{return {x}*{x}+{x};}}")))
            x = random.randint(0,MAX)
            self.assertEqual(x+x*x, int(debug(f"int main(){{return {x}+{x}*{x};}}")))
            x = random.randint(0,MAX)
            self.assertEqual(x-x+x, int(debug(f"int main(){{return {x}-{x}+{x};}}")))
            # TODO - add division
            # x = random.randint(0,max_operand)
            # self.assertEqual(x//x, int(self.run_code(f"int main(){{return {x}/{x};}}")))

if __name__ == "__main__":
  unittest.main(verbosity=1)