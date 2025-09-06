import random
import sys
import argparse
import math
from typing import Tuple, Optional


def mod_pow(a: int, e: int, m: int) -> int:
    """Возведение a^e по модулю m — алгоритм быстрого возведения (square-and-multiply).

    Работает корректно для больших целых чисел (Python int — неограничен).
    """
    if m == 1:
        return 0
    a %= m
    result = 1
    base = a
    exp = e
    while exp > 0:
        if exp & 1:
            result = (result * base) % m
        base = (base * base) % m
        exp >>= 1
    return result


def is_probable_prime_fermat(n: int, k: int = 8) -> bool:
    """Проверка простоты тестом Ферма с k испытаниями.

    Возвращает True, если n вероятно простое; False — если точно составное.
    Для малого n делает детерминированную проверку.
    """
    if n <= 1:
        return False
    if n <= 3:
        return True
    if n % 2 == 0:
        return False

    for _ in range(k):
        a = random.randrange(2, n - 1)
        if mod_pow(a, n - 1, n) != 1:
            return False
    return True


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Обобщённый алгоритм Евклида.

    Возвращает (g, x, y) такие, что g = gcd(a, b) и a*x + b*y = g.
    Работает с отрицательными a, b корректно.
    """
    old_r, r = abs(a), abs(b)
    old_s, s = 1 if a >= 0 else -1, 0
    old_t, t = 0, 1 if b >= 0 else -1

    while r != 0:
        q = old_r // r
        old_r, r = r, old_r - q * r
        old_s, s = s, old_s - q * s
        old_t, t = t, old_t - q * t

    g = old_r
    x = old_s if a >= 0 else -old_s
    y = old_t if b >= 0 else -old_t
    return g, x, y


def gen_random_int(bits: int = 32) -> int:
    """Генерация случайного положительного целого с указанным числом битов."""
    if bits <= 0:
        raise ValueError("bits must be > 0")
    return random.getrandbits(bits)


def gen_random_in_range(low: int, high: int) -> int:
    """Генерация случайного целого в [low, high] (включительно)."""
    return random.randint(low, high)


def gen_probable_prime(bits: int = 32, k: int = 8) -> int:
    """Генерация вероятно-простого числа с указанным количеством битов."""
    if bits < 2:
        raise ValueError('bits must be >= 2')

    while True:
        candidate = random.getrandbits(bits) | 1
        candidate |= (1 << (bits - 1))
        if is_probable_prime_fermat(candidate, k=k):
            return candidate


def baby_step_giant_step(a: int, y: int, p: int) -> Optional[int]:
    """Решение дискретного логарифма y = a^x mod p с помощью алгоритма Шаг младенца, шаг великана.

    Возвращает x, если решение существует, иначе None.
    Трудоёмкость: O(sqrt(p) * log p).
    """
    if not is_probable_prime_fermat(p):
        print("Ошибка: p должно быть простым числом")
        return None
    if a % p == 0 or y % p == 0:
        print("Ошибка: a или y не должны быть кратны p")
        return None
    if y % p == 1 and a % p != 1:
        return 0

    m = math.ceil(math.sqrt(p - 1))
    k = m
    baby_steps = {}
    for j in range(m):
        baby_steps[mod_pow(a, j, p)] = j

    am = mod_pow(a, m, p)
    g, x, _ = extended_gcd(am, p)
    if g != 1:
        print("Ошибка: a^m и p не взаимно просты")
        return None
    am_inv = x % p
    for i in range(1, k + 1):
        giant_step = (y * mod_pow(am_inv, i, p)) % p
        if giant_step in baby_steps:
            j = baby_steps[giant_step]
            x = i * m + j
            if x < p - 1 and mod_pow(a, x, p) == y:
                return x
            print("Найдено x, но оно не удовлетворяет условию (возможно, a не первообразный корень)")
            return None

    print("Решение не найдено")
    return None


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Криптографическая библиотека')
    parser.add_argument('--mode', choices=['input', 'rand', 'primes'], default='input',
                        help='Способ получения a и b: input — с клавиатуры, rand — случайные числа, primes — случайные вероятно-простые')
    parser.add_argument('--bits', type=int, default=32, help='Число бит для генерации случайных значений (только для rand/primes)')
    parser.add_argument('--fermat-k', type=int, default=8, help='Число испытаний для теста Ферма')
    args = parser.parse_args()

    print("=== Лабораторная работа №1 ===")
    if args.mode == 'input':
        try:
            a = int(input('Введите a: ').strip())
            b = int(input('Введите b: ').strip())
        except Exception as e:
            print('Ошибка ввода:', e)
            sys.exit(1)
    elif args.mode == 'rand':
        a = gen_random_int(args.bits)
        b = gen_random_int(args.bits)
        print(f'Сгенерированы случайные a={a}, b={b} (bits={args.bits})')
    elif args.mode == 'primes':
        a = gen_probable_prime(args.bits, k=args.fermat_k)
        b = gen_probable_prime(args.bits, k=args.fermat_k)
        print(f'Сгенерированы вероятно-простые a={a}, b={b} (bits={args.bits}, fermat_k={args.fermat_k})')
    else:
        raise RuntimeError('Неподдерживаемый режим')

    print('\n--- РЕЗУЛЬТАТЫ ---')
    print('a =', a)
    print('b =', b)

    g, x, y = extended_gcd(a, b)
    print(f'НОД(a,b) = {g}\nНайденные x, y: x = {x}, y = {y}')
    print(f'Проверка: a*x + b*y = {a * x + b * y}')

    e = 13
    m = b if b != 0 else (a + 1)
    y = mod_pow(a, e, m)
    print(f'Пример: y = a^{e} mod m = {y} (использован модуль m={m})')

    print('\nТест простоты Ферма (вероятностный):')
    for value in (a, b):
        print(f'  {value}:', 'Вероятно простое' if is_probable_prime_fermat(value, k=args.fermat_k) else 'Составное')

    print('\n=== Лабораторная работа №2 ===')
    print("Решение дискретного логарифма y = a^x mod p")
    mode = input("Выберите режим (input — ввод с клавиатуры, rand — случайные числа): ").strip().lower()
    if mode == 'input':
        try:
            a = int(input('Введите a (основание): ').strip())
            y = int(input('Введите y (результат): ').strip())
            p = int(input('Введите p (простой модуль): ').strip())
        except Exception as e:
            print('Ошибка ввода:', e)
            sys.exit(1)
    elif mode == 'rand':
        p = gen_probable_prime(args.bits, k=args.fermat_k)
        a = gen_random_in_range(2, p - 2)
        x = gen_random_in_range(1, p - 2)
        y = mod_pow(a, x, p)
        print(f'Сгенерированы p={p}, a={a}, y={y} (bits={args.bits}, истинное x={x} для проверки)')
    else:
        print("Неподдерживаемый режим")
        sys.exit(1)

    print('\n--- РЕЗУЛЬТАТЫ ---')
    print(f'a = {a}')
    print(f'y = {y}')
    print(f'p = {p}')
    x = baby_step_giant_step(a, y, p)
    if x is not None:
        print(f'Найдено x = {x}')
        print(f'Проверка: a^x mod p = {mod_pow(a, x, p)} (должно быть равно y = {y})')
    else:
        print('Решение не найдено')

    print('\nГотово.')