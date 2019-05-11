from stackprinter import trace, TracePrinter

def a():
    b()

def b():
    c()

def c():
    raise Exception("FooError")


if __name__ == "__main__":
    with TracePrinter(style='plaintext'):
        a()