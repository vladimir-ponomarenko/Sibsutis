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

def gen_safe_prime(bits: int = 32, k: int = 8) -> Tuple[int, int]:
    """Генерация безопасного простого p = 2*q + 1.

    Возвращает (p, q), где p и q — вероятно-простые.
    """
    if bits < 3:
        raise ValueError('bits must be >= 3 для генерации безопасного простого')

    while True:
        q = gen_probable_prime(bits - 1, k)
        p = 2 * q + 1
        if is_probable_prime_fermat(p, k=k):
            return p, q


def find_primitive_root(p: int, q: int) -> int:
    """Поиск первообразного корня g по модулю безопасного простого p.

    Используется тот факт, что для безопасного простого p = 2q + 1,
    число g является первообразным корнем, если g^2 != 1 (mod p) и g^q != 1 (mod p).
    """
    g = 2
    while g < p:
        if mod_pow(g, 2, p) != 1 and mod_pow(g, q, p) != 1:
            return g
        g += 1
    raise ValueError("Не удалось найти первообразный корень")


def diffie_hellman_protocol(p: Optional[int] = None, g: Optional[int] = None,
                           xa: Optional[int] = None, xb: Optional[int] = None,
                           bits: int = 32, fermat_k: int = 8):
    """Выполнение протокола Диффи-Хеллмана для двух абонентов."""
    if p is None or g is None or xa is None or xb is None:
        print("--- Генерация общих параметров ---")
        p, q = gen_safe_prime(bits, fermat_k)
        g = find_primitive_root(p, q)
        print(f"Сгенерировано безопасное простое p = {p}")
        print(f"Сгенерирован первообразный корень g = {g}\n")

        print("--- Генерация закрытых ключей абонентов ---")
        xa = gen_random_in_range(2, p - 2)
        xb = gen_random_in_range(2, p - 2)
        print(f"Закрытый ключ Алисы XA = {xa}")
        print(f"Закрытый ключ Боба XB = {xb}\n")
    else:
        print("--- Использование введенных параметров ---")
        print(f"p = {p}, g = {g}, XA = {xa}, XB = {xb}\n")

    print("--- Вычисление и обмен открытыми ключами ---")
    ya = mod_pow(g, xa, p)
    yb = mod_pow(g, xb, p)
    print(f"Открытый ключ Алисы YA (g^XA mod p) = {ya}")
    print(f"Открытый ключ Боба YB (g^XB mod p) = {yb}\n")

    print("--- Вычисление общего секретного ключа ---")
    ka = mod_pow(yb, xa, p)
    kb = mod_pow(ya, xb, p)

    print(f"Общий ключ, вычисленный Алисой: KA = {ka}")
    print(f"Общий ключ, вычисленный Бобом: KB = {kb}\n")

    if ka == kb:
        print(f"УСПЕХ: Ключи совпадают! Общий секретный ключ: {ka}")
    else:
        print("ОШИБКА: Ключи не совпадают!")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Криптографическая библиотека для ЛР №3')
    parser.add_argument('--bits', type=int, default=32, help='Число бит для генерации случайных значений')
    parser.add_argument('--fermat-k', type=int, default=8, help='Число испытаний для теста Ферма')
    args = parser.parse_args()

    print('=== Лабораторная работа №3: Построение общего ключа по схеме Диффи-Хеллмана ===')
    mode_lab3 = input("Выберите режим (input — ввод с клавиатуры, rand — генерация параметров): ").strip().lower()

    if mode_lab3 == 'input':
        try:
            p_dh = int(input('Введите безопасное простое p: ').strip())
            g_dh = int(input('Введите первообразный корень g: ').strip())
            xa_dh = int(input('Введите закрытый ключ Алисы XA: ').strip())
            xb_dh = int(input('Введите закрытый ключ Боба XB: ').strip())
            print()
            diffie_hellman_protocol(p=p_dh, g=g_dh, xa=xa_dh, xb=xb_dh)
        except Exception as e:
            print('Ошибка ввода:', e)
            sys.exit(1)
    elif mode_lab3 == 'rand':
        diffie_hellman_protocol(bits=args.bits, fermat_k=args.fermat_k)
    else:
        print("Неподдерживаемый режим, выход.")
        sys.exit(1)

    print('\nГотово.')