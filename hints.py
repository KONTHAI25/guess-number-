import random

def get_hint(secret_number):
    hints = [
        f"The number is {'even' if secret_number % 2 == 0 else 'odd'}.",
        f"The number is divisible by 3: {'Yes' if secret_number % 3 == 0 else 'No'}.",
        f"The number is greater than {secret_number // 2}.",
        f"The last digit of the number is {secret_number % 10}.",
        f"The number is a multiple of 5: {'Yes' if secret_number % 5 == 0 else 'No'}.",
        f"The number is between {max(1, secret_number - 50)} and {secret_number + 50}.",
        f"The number has {len(str(secret_number))} digits.",
        f"The sum of digits is {sum(int(d) for d in str(secret_number))}.",
        f"The number is a perfect square: {'Yes' if int(secret_number**0.5)**2 == secret_number else 'No'}.",
        f"The number is prime: {'Yes' if is_prime(secret_number) else 'No'}.",
        f"The number is less than {secret_number * 2 if secret_number * 2 <= 500000 else 500000}.",
        f"The number's first digit is {str(secret_number)[0]}.",
        f"The number is divisible by 7: {'Yes' if secret_number % 7 == 0 else 'No'}.",
        f"The number ends in 0 or 5: {'Yes' if str(secret_number).endswith(('0', '5')) else 'No'}.",
        f"The number modulo 100 is {secret_number % 100}."
    ]
    return random.choice(hints)

def is_prime(n):
    if n < 2:
        return False
    for i in range(2, int(n ** 0.5) + 1):
        if n % i == 0:
            return False
    return True