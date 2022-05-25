import random

max_number = 25000
attempts = 0
answer = -1
done = False

max_number = int(input("Угадайте число от 1 до (введите число): "))
answer = random.randint(0, max_number)
while not done:
    guess = int(input(f"Попытка {attempts+1}: "))
    if guess == answer:
        print(f"Верно, ответ {answer}")
        done = True
    elif guess > answer:
        print("Нет, оно меньше")
    elif guess < answer:
        print("Нет, оно больше")
    attempts += 1
