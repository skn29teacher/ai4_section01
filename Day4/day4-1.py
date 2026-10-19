import random
print("Welcome to the Number Guessing Game!")
numbers = [random.randint(1, 100) for i in range(10)]
numbers[0] = numbers[-1]
print(numbers[100])