import unittest
import cpy.cmp as cmp
import subprocess

class TestE2E(unittest.TestCase):
    def run_code(self,code:str):
        arm64 = cmp.compile(code,True)
        args = ["clang", "-x", "assembler","-"]
        subprocess.run(args, input=arm64, text=True)
        cmd = """value=$(DISABLE_CONFIRM_QUIT=1 lldb a.out -o "b DBG" -o "run" -o "script print(int(lldb.frame.FindRegister('x0').GetValue(), 16))" -o "exit" | tail -2) && echo $value"""
        output = subprocess.run(cmd, shell=True, capture_output=True, text=True)
        return int(output.stdout.split()[0])

    def test_return_value_sanity(self):
        for i in range(0, 2**18+1, 2**16):
            self.assertEqual(i, int(self.run_code(f"int main(){{return {i};}}")))
            
    def test_simple_arith(self):
        for i in range(0, 200, 50):
            self.assertEqual(i*i, int(self.run_code(f"int main(){{return {i}*{i};}}")))
            self.assertEqual(i+i, int(self.run_code(f"int main(){{return {i}+{i};}}")))

if __name__ == "__main__":
  unittest.main(verbosity=1)