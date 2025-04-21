import unittest
import cpy.compiler as compiler
import subprocess
import random

def debug(code:str):
    arm64 = compiler.compile(code,debug=True)
    print(arm64)
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
            x = random.randint(1,MAX)
            self.assertEqual(int(x/x), int(debug(f"int main(){{return {x}/{x};}}")))

    def test_assign(self):
        code1 = """
        int main() { 
            int x = 2;
            int y = 4;
            x = 4;
            return x;
        }
        """
        self.assertEqual(4, int(debug(code1)))

        code2 = """
        int main() { 
            int x = 3;
            x *= 3;
            return x;
        }
        """
        self.assertEqual(9, int(debug(code2)))

        code3 = """
        int main() { 
            int x = 1;
            x += 3;
            return x;
        }
        """
        self.assertEqual(4, int(debug(code3)))
        
        code4 = """
        int main() { 
            int x = 10;
            x /= 2;
            return x;
        }
        """
        self.assertEqual(5, int(debug(code4)))

    def test_reassignment(self): 
        code = """
        int main() { 
            int x = 0;
            x = 2;
            int y = x;
            y = x;
            return x + y;
        }
        """
        self.assertEqual(int(debug(code)),4)

    def test_if_statement(self):
        def run_condition(condition:str,ret_value_then:int, ret_value_else:int):
            code=f"""int main(){{if({condition}){{return {ret_value_then};}}return {ret_value_else};}}"""
            print(code)
            return int(debug(code))
        self.assertEqual(run_condition("1==1", 1, 2), 1) 
        self.assertEqual(run_condition("1!=1", 1, 2), 2) 
        self.assertEqual(run_condition("1<1", 1, 2), 2) 
        self.assertEqual(run_condition("1<=1", 1, 2), 1) 

        code = """
        int main() {
            int x = 1;
            if (x < 1) { 
                x = 2;
            } else { 
                x = 3;
            }
            return x;
        }"""
        self.assertEqual(int(debug(code)), 3)

        code = """
        int main() {
            int x = 1;
            if (x == 1) { 
                x = 2;
            } else { 
                x = 3;
            }
            return x;
        }"""
        self.assertEqual(int(debug(code)), 2)

        code = """
        int main() {
            int x = 0;
            if (x < 2) { 
                if (x == 0) { 
                    x = 1;
                } else { 
                    x = 2;
                }
            } else { 
                x = 3;
            }
            return x;
        }"""
        self.assertEqual(int(debug(code)), 1)

    def test_while(self):
        code = """
        int main() { 
            int x = 1;
            int i = 0;
            int j = 0;
            while (i < 2) { 
                i += 1;
                x *= 3;
            }
            return x;
        }
        """
        self.assertEqual(int(debug(code)),9)
        code =\
        """
        int main() { 
            int x = 1;
            int i = 0;
            while (i < 2) { 
                int j = 3;
                x *= 2;
                while (j != 0) { 
                    x *= 2;
                    j -= 1;
                }
                i+=1;
            }
            return x;
        }
        """
        self.assertEqual(int(debug(code)),256)
    
    def test_climbing_stairs(self):
        def generate_code(n:int):
            return f"""
            int main() {{
                int n = {n};
                if (n <= 2) {{
                    return n;
                }}
                int prev = 1;
                int curr = 2;
                int i = 2;
                while (i < n) {{
                    int temp = curr;
                    curr = curr + prev;
                    prev = temp;
                    i += 1;
                }}
                return curr;
            }}
            """
        self.assertEqual(int(debug(generate_code(1))),1)
        self.assertEqual(int(debug(generate_code(2))),2)
        self.assertEqual(int(debug(generate_code(3))),3)
        self.assertEqual(int(debug(generate_code(4))),5)
        self.assertEqual(int(debug(generate_code(5))),8)
        self.assertEqual(int(debug(generate_code(6))),13)
    

if __name__ == "__main__":
  unittest.main(verbosity=1)