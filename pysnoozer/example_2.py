import pysnooper

class Plus:
    def __init__(self, a):
        self.a = a

    @pysnooper.snoop(variables=('self.a'))
    def plus(self, b):
        c = self.a + b

        return c

if __name__ == "__main__":
    result = Plus(2).plus(3)
    print(result)