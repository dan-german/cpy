"""
Left recursion occurs when any of the production rule's alternatives begin with the same nonterminal as on the left hand side:

                        A -> A + 1 | 1

(this rule produces addition expressions with 1s as operands (1+1 | (1+1)+1 etc))
"""

class LeftRecursive: 
    """Top-down parser"""
    def __init__(self): self.i = 0
    def parse(self, tokens):
        def consumable(): return self.i < len(tokens)
        def plus():
            if tokens[self.i] != "+": raise Exception(f"Expected +, got {tokens[self.i]}")
            self.i += 1

        def digit(): 
            if tokens[self.i] != "1": raise Exception(f"Expected 1, got {tokens[self.i]}")
            self.i += 1

        def A():  
            if consumable(): A() # ❌ LEFT RECURSION ❌
            if consumable(): plus()
            if consumable(): digit()

        A()

"""
As shown above, top-down parsing cannot handle left recursive production rules. 
But we can make it work by rewriting the grammar rules:

                        A -> 1 + A | 1

"""

class RightRecursive: 
    """Top-down parser"""
    def __init__(self): self.i = 0
    def parse(self, tokens):
        def consumable(): return self.i < len(tokens)
        def plus():
            if tokens[self.i] != "+": raise Exception(f"Expected +, got {tokens[self.i]}")
            self.i += 1

        def digit(): 
            if tokens[self.i] != "1": raise Exception(f"Expected 1, got {tokens[self.i]}")
            self.i += 1

        def A(): 
            if consumable(): digit()
            if consumable(): plus()
            if consumable(): A() # ✅ RIGHT RECURSION ✅ 

        A()


"""
The only problem now is that it makes addition right-associative, i.e. 1+(1+1)
But we can fix that easily:
"""

class RightRecursiveLeftAssociative: 
    """Top-down parser"""
    def __init__(self): self.i = 0
    def parse(self, tokens):
        def consumable(): return self.i < len(tokens)
        def plus():
            if not consumable(): return
            if tokens[self.i] != "+": raise Exception(f"Expected +, got {tokens[self.i]}")
            self.i += 1
            return tokens[self.i - 1]

        def digit(): 
            if not consumable(): return
            if tokens[self.i] != "1": raise Exception(f"Expected 1, got {tokens[self.i]}")
            self.i += 1
            return tokens[self.i - 1]

        def A():
            left = digit()
            while consumable(): 
                left = (left, plus(), digit())
            return left

        return A()

if __name__ == '__main__': 
    try: 
        LeftRecursive().parse("1+1+1")
    except RecursionError:
        print("Left recursion will never halt 😭")

    RightRecursive().parse("1+1+1")
    print("Right recursion is ok ️👍")
    print(f"Right recursive but left associative: {RightRecursiveLeftAssociative().parse("1+1+1")}")