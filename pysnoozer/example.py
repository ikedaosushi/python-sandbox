import pysnooper

@pysnooper.snoop(prefix='MyPrefix ')
def plus_with_power(a, b):
    a = a * a
    b = b * b
    c = a + b

    return c

if __name__ == "__main__":
    result = plus_with_power(2, 3)
    print(result)