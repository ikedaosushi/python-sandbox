def fizzbuzz(start,stop):
  for i in range(start,stop):
    if (i%15) == 0:
      print('FizzBuzz')
    elif (i%5) == 0:
      print('Buzz')
    elif (i%3) == 0:
      print('Fizz')
    else:
      print(i)

def main():
  fizzbuzz(1, 20)

if __name__ == '__main__':
  main()