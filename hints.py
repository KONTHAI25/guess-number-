import math
import random
from typing import Optional, Callable, List, Dict, Any

# helper to safely extract the secret as an int (abs where useful)
def _get_secret(game: Dict[str, Any]) -> Optional[int]:
    try:
        # if secret missing or not int-like, this returns None
        return int(game.get("secret"))
    except Exception:
        return None


def _hint_parity(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    return "Number is even." if n % 2 == 0 else "Number is odd."


def _hint_digit_sum(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    s = sum(int(d) for d in str(abs(n)))
    return f"The sum of digits is {s}."


def _hint_first_last_digit(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    s = str(abs(n))
    return f"First digit is {s[0]}, last digit is {s[-1]}."


def _hint_prime_composite(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    if n < 2:
        return "This number is not a Prime number."
    if n == 2:
        return "This number is a Prime number."
    if n % 2 == 0:
        return "This number is Composite (divisible by 2)."
    r = int(math.isqrt(n))
    for p in range(3, r + 1, 2):
        if n % p == 0:
            return f"This number is Composite (divisible by {p})."
    return "This number is a Prime number."


def _hint_higher_lower_last(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    guesses = game.get("guesses") or []
    if not guesses:
        return "No guesses yet—try one!"
    last = guesses[-1]
    try:
        last = int(last)
    except Exception:
        return "Last guess is not a valid number."
    if last < n:
        return "Higher than your last guess."
    if last > n:
        return "Lower than your last guess."
    return "You already guessed it."


# Hint 1 & 4: Thai Provinces Range
def _hint_thai_provinces(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    if 1 <= abs(n) <= 77:
        return "ตัวเลขที่ถูกต้องอยู่ในช่วงจำนวนจังหวัดประเทศไทย"
    else:
        return "ตัวเลขที่ถูกต้องไม่อยู่ในช่วงจำนวนจังหวัดประเทศไทย"


# Hint 2: Fibonacci Number
def _hint_fibonacci(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    n = abs(n)
    a, b = 0, 1
    while a < n:
        a, b = b, a + b
    return "The number is in the Fibonacci sequence." if a == n else "The number is not in the Fibonacci sequence."


# Hint 3: "Hone Krasae" Episodes Range
def _hint_hone_krasae(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    n = abs(n)
    # keep the original date-specific message
    if 1 <= n <= 2017:
        return "ตัวเลขอยู่ในช่วง ep ของรายการโหนกระแส ณ วันที่ 12 กันยายน 2568"
    else:
        return "ตัวเลขไม่อยู่ในช่วง ep ของรายการโหนกระแส ณ วันที่ 12 กันยายน 2568"


# Hint 5: Digits from Pi (first 5 decimals: 1,4,1,5,9 -> unique {1,4,5,9})
def _hint_pi_digits(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    pi_decimals = {"1", "4", "5", "9"}  # unique digits in 14159
    secret_digits = set(str(abs(n)))
    common_digits = len(secret_digits.intersection(pi_decimals))
    return f"ตัวเลขที่คุณทายมีตัวเลข {common_digits} ตัวจากชุด {{1,4,5,9}} ซึ่งปรากฏในทศนิยม 5 ตำแหน่งแรกของ π ≈ 3.14159"


# Hint 6: Earth's Orbit Range
def _hint_earth_orbit(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    if 1 <= abs(n) <= 365:
        return "ตัวเลขอยู่ในช่วงวันที่ใช้ในการโคจรรอบดวงอาทิตย์ของโลก"
    else:
        return "ตัวเลขไม่อยู่ในช่วงวันที่ใช้ในการโคจรรอบดวงอาทิตย์ของโลก"


# Hint 7: Product of Digits
def _hint_product_of_digits(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    s = str(abs(n))
    nonzero_digits = [int(d) for d in s if d != "0"]
    if not nonzero_digits:
        return "The product of the non-zero digits = 0 (all digits were zero or only zeros remained)."
    product = 1
    for d in nonzero_digits:
        product *= d
    return f"The product of its non-zero digits is {product}."


# Hint 8: Difference Between Last Two Digits
def _hint_tens_units_diff(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    n = abs(n)
    if n < 10:
        return "มีเพียงหลักเดียว ไม่มีหลักสิบ"
    units = n % 10
    tens = (n // 10) % 10
    diff = abs(tens - units)
    return f"ความแตกต่างระหว่างหลักสิบและหลักหน่วยคือ {diff}."


# Hint 9: Palindrome Check
def _hint_palindrome(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    s = str(abs(n))
    return "ตัวเลขนี้เป็น palindrome (สามารถอ่านจากหน้าไปหลังเหมือนกัน)" if s == s[::-1] else "ตัวเลขนี้ไม่เป็น palindrome.(ไม่สามารถอ่านจากหน้าไปหลังเหมือนกัน)"


# Hint 10: Sum of Digits Parity
def _hint_sum_of_digits_parity(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    digit_sum = sum(int(d) for d in str(abs(n)))
    return "ผลรวมของตัวเลขเป็นเลขคู่" if digit_sum % 2 == 0 else "ผลรวมของตัวเลขเป็นเลขคี่"


# Hint 11: Repeated Digits
def _hint_has_repeated_digits(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    s = str(abs(n))
    return "ตัวเลขนี้ไม่มีหลักที่ซ้ำกัน." if len(s) == len(set(s)) else "ตัวเลขนี้มีหลักที่ซ้ำกันอย่างน้อย 1 หลัก."


# Hint 12: Prime check (simplified)
def _hint_is_prime_simple(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    n = abs(n)
    if n < 2:
        return "ตัวเลขนี้ไม่เป็นจำนวนเฉพาะ."
    if n == 2:
        return "ตัวเลขนี้เป็นจำนวนเฉพาะ."
    if n % 2 == 0:
        return "ตัวเลขนี้ไม่เป็นจำนวนเฉพาะ."
    for i in range(3, math.isqrt(n) + 1, 2):
        if n % i == 0:
            return "ตัวเลขนี้ไม่เป็นจำนวนเฉพาะ."
    return "ตัวเลขนี้เป็นจำนวนเฉพาะ."


# Hint 13: Perfect Power (improved detection)
def _hint_is_perfect_power(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    n = abs(n)
    if n == 1:
        return "1 can be expressed as 1^k (perfect power)."
    if n <= 0:
        return "The number cannot be expressed as a perfect power."  # keep negative/0 simple
    # max exponent to try: log2(n) is safe upper bound
    max_power = int(math.log2(n)) + 1
    for power in range(2, max_power + 1):
        root = round(n ** (1.0 / power))
        if root > 1 and root ** power == n:
            return f"The number is a perfect power: {root}^{power}."
    return "The number is not a perfect power."


# Hint 14: Perfect Square
def _hint_is_perfect_square(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    if n < 0:
        return "The number is not a perfect square (negative)."
    sqrt = math.isqrt(n)
    if sqrt * sqrt == n:
        return "The number is a perfect square. (perfect square meaning a number that can be expressed as the square of an integer.)"
    return "The number is not a perfect square. (perfect square meaning a number that can be expressed as the square of an integer.)"


# Hint 15: Power of Two
def _hint_is_power_of_two(game: Dict[str, Any]) -> str:
    n = _get_secret(game)
    if n is None:
        return "Secret not set yet."
    is_power_of_two = (n > 0) and ((n & (n - 1)) == 0)
    if is_power_of_two:
        return "The number has no odd divisors other than 1 (it is a power of 2)."
    else:
        return "The number has an odd divisor other than 1."


# List of hint functions
HINT_FUNCS: List[Callable[[Dict[str, Any]], str]] = [
    _hint_parity,
    _hint_digit_sum,
    _hint_first_last_digit,
    _hint_prime_composite,
    _hint_higher_lower_last,
    _hint_thai_provinces,
    _hint_fibonacci,
    _hint_hone_krasae,
    _hint_pi_digits,
    _hint_earth_orbit,
    _hint_product_of_digits,
    _hint_tens_units_diff,
    _hint_palindrome,
    _hint_sum_of_digits_parity,
    _hint_has_repeated_digits,
    _hint_is_prime_simple,
    _hint_is_perfect_power,
    _hint_is_perfect_square,
    _hint_is_power_of_two,
]


def get_hint(game: Dict[str, Any], record: bool = True) -> Optional[str]:
    """
    Return a hint not already given, or None when all hints exhausted.
    If record=True, append the hint text into game['hints'] (creates list if needed).
    Note: calling code should also call apply_hint_penalty(game) if you want scoring to change.
    """
    if game is None:
        return None

    used = set(game.get("hints") or [])
    shuffled = HINT_FUNCS.copy()
    random.shuffle(shuffled)

    for func in shuffled:
        try:
            text = func(game)
        except Exception:
            # skip broken hint function to keep game rolling
            continue
        # skip falsy results or duplicates
        if not text or text in used:
            continue
        if record:
            if "hints" not in game or not isinstance(game["hints"], list):
                game["hints"] = []
            game["hints"].append(text)
        return text

    # no new hint found
    return None