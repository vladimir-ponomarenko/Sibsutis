import random
import sys
import argparse
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


def extended_gcd(a: int, b: int) -> Tuple[int, int, int]:
    """Расширенный алгоритм Евклида. Возвращает (НОД, x, y)."""
    if a == 0:
        return b, 0, 1
    d, x1, y1 = extended_gcd(b % a, a)
    x = y1 - (b // a) * x1
    y = x1
    return d, x, y


def mod_inverse(a: int, m: int) -> int:
    """Вычисление модульного обратного элемента a⁻¹ mod m."""
    d, x, y = extended_gcd(a, m)
    if d != 1:
        raise ValueError(f"Обратный элемент не существует для a={a}, m={m}")
    return x % m


def is_probable_prime(n: int, k: int = 10) -> bool:
    """Тест простоты Миллера-Рабина."""
    if n < 2: return False
    if n == 2 or n == 3: return True
    if n % 2 == 0: return False
    
    d, s = n - 1, 0
    while d % 2 == 0:
        d //= 2
        s += 1
    
    for _ in range(k):
        a = random.randrange(2, n - 1)
        x = mod_pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = mod_pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True


def gen_probable_prime(bits: int = 32) -> int:
    """Генерация вероятно-простого числа с заданным количеством битов."""
    while True:
        candidate = random.getrandbits(bits)
        candidate |= (1 << (bits - 1)) | 1
        if is_probable_prime(candidate):
            return candidate


def find_primitive_root(p: int) -> int:
    """Поиск первообразного корня по модулю p."""
    if p == 2:
        return 1
    
    phi = p - 1
    factors = []
    temp = phi
    
    # Разложение phi на простые множители
    d = 2
    while d * d <= temp:
        if temp % d == 0:
            factors.append(d)
            while temp % d == 0:
                temp //= d
        d += 1
    if temp > 1:
        factors.append(temp)
    
    # Поиск первообразного корня
    for g in range(2, p):
        is_primitive = True
        for factor in factors:
            if mod_pow(g, phi // factor, p) == 1:
                is_primitive = False
                break
        if is_primitive:
            return g
    
    raise ValueError("Первообразный корень не найден")


def generate_elgamal_keys(bits: int = 32) -> Tuple[int, int, int, int]:
    """
    Генерирует ключи для шифра Эль-Гамаля.
    Возвращает (p, g, Cb, Db) где:
    - p - большое простое число
    - g - первообразный корень по модулю p
    - Cb - открытый ключ Боба
    - Db - закрытый ключ Боба
    """
    p = gen_probable_prime(bits)
    g = find_primitive_root(p)
    
    Db = random.randrange(1, p - 1)
    Cb = mod_pow(g, Db, p)
    
    return p, g, Cb, Db


def elgamal_encrypt(data: bytes, p: int, g: int, Cb: int) -> bytes:
    """Шифрует данные по схеме Эль-Гамаля."""
    result = bytearray()
    
    for byte in data:
        # Выбор случайного k
        k = random.randrange(1, p - 1)
        
        # Шифрование: (a, b) = (g^k mod p, M * Cb^k mod p)
        a = mod_pow(g, k, p)
        b = (byte * mod_pow(Cb, k, p)) % p
        
        # Сохраняем a и b как два байта (для простоты)
        result.append(a % 256)
        result.append(b % 256)
    
    return bytes(result)


def elgamal_decrypt(encrypted_data: bytes, p: int, Db: int) -> bytes:
    """Расшифровывает данные по схеме Эль-Гамаля."""
    result = bytearray()
    
    # Обрабатываем данные парами (a, b)
    for i in range(0, len(encrypted_data), 2):
        if i + 1 >= len(encrypted_data):
            break
            
        a = encrypted_data[i]
        b = encrypted_data[i + 1]
        
        # Расшифрование: M = b * a^(-Db) mod p
        a_power = mod_pow(a, p - 1 - Db, p)
        decrypted_byte = (b * a_power) % p
        
        result.append(decrypted_byte % 256)
    
    return bytes(result)


def process_file(input_path: str, output_path: str, p: int, g: int, Cb: int, Db: int, encrypt: bool):
    """Обрабатывает файл с помощью шифра Эль-Гамаля."""
    action = "Шифрование" if encrypt else "Расшифрование"
    print(f"{action} файла: {input_path}")
    print(f"Параметры: p={p}, g={g}, Cb={Cb}, Db={Db}")
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
        
        print(f"Размер файла: {len(data)} байт")
        
        if encrypt:
            processed_data = elgamal_encrypt(data, p, g, Cb)
        else:
            processed_data = elgamal_decrypt(data, p, Db)
        
        with open(output_path, 'wb') as f:
            f.write(processed_data)
        
        print(f"Результат сохранен в: {output_path}")
        
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден - {input_path}")
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Шифр Эль-Гамаля для шифрования файлов")
    parser.add_argument("input_file", help="Входной файл")
    parser.add_argument("output_file", help="Выходной файл")
    parser.add_argument("--action", choices=['encrypt', 'decrypt'], required=True,
                        help="Действие: encrypt или decrypt")
    parser.add_argument("--mode", choices=['input', 'generate'], default='generate',
                        help="Режим: input - ввод параметров, generate - генерация")
    parser.add_argument("--bits", type=int, default=32, help="Размер простого числа в битах")
    
    args = parser.parse_args()
    
    print("=== Лабораторная работа №5: Шифр Эль-Гамаля ===")
    
    if args.mode == 'input':
        try:
            p = int(input("Введите простое число p: "))
            g = int(input("Введите первообразный корень g: "))
            Cb = int(input("Введите открытый ключ Cb: "))
            Db = int(input("Введите закрытый ключ Db: "))
            
            # Проверка корректности ключей
            if not is_probable_prime(p):
                print("Ошибка: p должно быть простым числом")
                sys.exit(1)
            
            if mod_pow(g, Db, p) != Cb:
                print("Ошибка: Cb должно равняться g^Db mod p")
                sys.exit(1)
                
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
            sys.exit(1)
    else:
        print("Генерация параметров...")
        p, g, Cb, Db = generate_elgamal_keys(args.bits)
        print(f"Сгенерированы параметры:")
        print(f"p = {p}")
        print(f"g = {g}")
        print(f"Cb = {Cb}")
        print(f"Db = {Db}")
    
    encrypt = args.action == 'encrypt'
    process_file(args.input_file, args.output_file, p, g, Cb, Db, encrypt)
    print("Готово.")
