import random
import sys
import math
from typing import Tuple


def mod_pow(base: int, exp: int, mod: int) -> int:
    """Возведение в степень по модулю (base^exp) % mod."""
    res = 1
    base %= mod
    while exp > 0:
        if exp % 2 == 1:
            res = (res * base) % mod
        base = (base * base) % mod
        exp //= 2
    return res

def is_probable_prime_fermat(n: int, k: int = 8) -> bool:
    """Тест простоты Ферма."""
    if n <= 1: return False
    if n <= 3: return True
    if n % 2 == 0: return False
    for _ in range(k):
        a = random.randrange(2, n - 1)
        if mod_pow(a, n - 1, n) != 1:
            return False
    return True

def gen_probable_prime(bits: int = 64, k: int = 8) -> int:
    """Генерация вероятно-простого числа."""
    while True:
        candidate = random.getrandbits(bits) | 1
        candidate |= (1 << (bits - 1))
        if is_probable_prime_fermat(candidate, k=k):
            return candidate

def gen_safe_prime(bits: int = 64, k: int = 8) -> Tuple[int, int]:
    """Генерация безопасного простого p = 2*q + 1."""
    while True:
        q = gen_probable_prime(bits - 1, k)
        p = 2 * q + 1
        if is_probable_prime_fermat(p, k=k):
            return p, q

def find_primitive_root(p: int, q: int) -> int:
    """Поиск первообразного корня для безопасного простого p."""
    g = 2
    while g < p:
        if mod_pow(g, 2, p) != 1 and mod_pow(g, q, p) != 1:
            return g
        g += 1
    raise ValueError("Не удалось найти первообразный корень")


def get_dh_shared_key(bits: int = 64) -> int:
    """
    Выполняет протокол Диффи-Хеллмана и возвращает общий секретный ключ.
    """
    print("-> Запуск протокола Диффи-Хеллмана для генерации ключа...")
    
    # 1. Генерация общих параметров p и g
    p, q = gen_safe_prime(bits)
    g = find_primitive_root(p, q)
    print(f"   Общие параметры: p={p}, g={g}")

    # 2. Генерация секретных ключей Алисы (xa) и Боба (xb)
    xa = random.randrange(2, p - 2)
    xb = random.randrange(2, p - 2)
    print(f"   Секретный ключ Алисы (xa): {xa}")
    print(f"   Секретный ключ Боба (xb): {xb}")
    
    # 3. Вычисление открытых ключей
    ya = mod_pow(g, xa, p)
    yb = mod_pow(g, xb, p)
    print(f"   Открытый ключ Алисы (ya): {ya}")
    print(f"   Открытый ключ Боба (yb): {yb}")
    
    # 4. Вычисление общего секретного ключа
    shared_key = mod_pow(yb, xa, p)
    print(f"-> Протокол завершен. Общий секретный ключ K: {shared_key}\n")
    
    return shared_key

def process_vernam_file(input_path: str, output_path: str, key: int):
    """
    Шифрует или расшифровывает файл, используя ключ как seed для PRNG.
    Операция полностью симметрична.
    """
    print(f"-> Обработка файла: '{input_path}'")
    print(f"   Ключ (seed): {key}")
    
    random.seed(key)

    try:
        with open(input_path, 'rb') as f_in, open(output_path, 'wb') as f_out:
            while chunk := f_in.read(1024):
                keystream = bytearray(random.getrandbits(8) for _ in range(len(chunk)))                
                processed_chunk = bytearray(a ^ b for a, b in zip(chunk, keystream))
                f_out.write(processed_chunk)
        
        print(f"-> Успех! Результат сохранен в файл: '{output_path}'")

    except FileNotFoundError:
        print(f"-> Ошибка: Файл не найден по пути '{input_path}'")
    except Exception as e:
        print(f"-> Произошла непредвиденная ошибка: {e}")
        

if __name__ == '__main__':
    print("=== Лабораторная работа №7: Шифр Вернама с ключом Диффи-Хеллмана ===")
    
    try:
        
        action = input("Выберите действие: (E)ncrypt / (D)ecrypt: ").strip().lower()
        if action not in ['e', 'd']:
            raise ValueError("Неверное действие. Выберите 'E' или 'D'.")
            
        key_source = input("Источник ключа: (D)H-generate / (M)anual input: ").strip().lower()
        encryption_key = 0
        if key_source == 'd':
            encryption_key = get_dh_shared_key(bits=64)
        elif key_source == 'm':
            encryption_key = int(input("Введите числовой ключ (seed): ").strip())
        else:
            raise ValueError("Неверный источник ключа. Выберите 'D' или 'M'.")
            
        input_file = input("Введите путь к исходному файлу: ").strip()
        if action == 'e':
            output_file = input_file + ".vernam"
            process_vernam_file(input_file, output_file, encryption_key)
        else: 
            
            if input_file.endswith(".vernam"):
                output_file = input_file[:-7] 
            else:
                output_file = input_file + ".decrypted"
            process_vernam_file(input_file, output_file, encryption_key)

    except (ValueError, KeyboardInterrupt) as e:
        print(f"\nОшибка: {e}. Программа завершена.")
        sys.exit(1)
    
    print("\nГотово.")