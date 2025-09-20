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


def generate_shamir_keys(p: int) -> Tuple[int, int, int, int]:
    """
    Генерирует ключи для шифра Шамира.
    Возвращает (Ca, Cb, Da, Db) где:
    - Ca, Cb - открытые ключи Алисы и Боба
    - Da, Db - закрытые ключи Алисы и Боба
    """
    while True:
        Ca = random.randrange(1, p - 1)
        if extended_gcd(Ca, p - 1)[0] == 1:
            break
    
    while True:
        Cb = random.randrange(1, p - 1)
        if extended_gcd(Cb, p - 1)[0] == 1:
            break
    
    Da = mod_inverse(Ca, p - 1)
    Db = mod_inverse(Cb, p - 1)
    
    return Ca, Cb, Da, Db


def shamir_encrypt_decrypt(data: bytes, p: int, key1: int, key2: int) -> bytes:
    """
    Шифрует или расшифровывает данные по схеме Шамира.
    Операция симметрична: encrypt(encrypt(data)) = data
    """
    result = bytearray()
    
    for byte in data:
        # Шаг 1: x1 = M^key1 mod p
        x1 = mod_pow(byte, key1, p)
        
        # Шаг 2: x2 = x1^key2 mod p  
        x2 = mod_pow(x1, key2, p)
        
        # Шаг 3: x3 = x2^key1 mod p
        x3 = mod_pow(x2, key1, p)
        
        # Шаг 4: M = x3^key2 mod p
        decrypted_byte = mod_pow(x3, key2, p)
        
        result.append(decrypted_byte)
    
    return bytes(result)


def process_file(input_path: str, output_path: str, p: int, Ca: int, Cb: int, Da: int, Db: int):
    """Обрабатывает файл с помощью шифра Шамира."""
    print(f"Обработка файла: {input_path}")
    print(f"Параметры: p={p}, Ca={Ca}, Cb={Cb}, Da={Da}, Db={Db}")
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
        
        print(f"Размер файла: {len(data)} байт")
        
        # Шифрование: M -> Ca -> Cb -> Da -> Db
        encrypted = shamir_encrypt_decrypt(data, p, Ca, Cb)
        encrypted = shamir_encrypt_decrypt(encrypted, p, Da, Db)
        
        with open(output_path, 'wb') as f:
            f.write(encrypted)
        
        print(f"Результат сохранен в: {output_path}")
        
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден - {input_path}")
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Шифр Шамира для шифрования файлов")
    parser.add_argument("input_file", help="Входной файл")
    parser.add_argument("output_file", help="Выходной файл")
    parser.add_argument("--mode", choices=['input', 'generate'], default='generate',
                        help="Режим: input - ввод параметров, generate - генерация")
    parser.add_argument("--bits", type=int, default=32, help="Размер простого числа в битах")
    
    args = parser.parse_args()
    
    print("=== Лабораторная работа №4: Шифр Шамира ===")
    
    if args.mode == 'input':
        try:
            p = int(input("Введите простое число p: "))
            Ca = int(input("Введите Ca: "))
            Cb = int(input("Введите Cb: "))
            Da = int(input("Введите Da: "))
            Db = int(input("Введите Db: "))
            
            # Проверка корректности ключей
            if not is_probable_prime(p):
                print("Ошибка: p должно быть простым числом")
                sys.exit(1)
            
            if (Ca * Da) % (p - 1) != 1 or (Cb * Db) % (p - 1) != 1:
                print("Ошибка: ключи не удовлетворяют условиям Ca*Da ≡ 1 (mod p-1) и Cb*Db ≡ 1 (mod p-1)")
                sys.exit(1)
                
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
            sys.exit(1)
    else:
        print("Генерация параметров...")
        p = gen_probable_prime(args.bits)
        Ca, Cb, Da, Db = generate_shamir_keys(p)
        print(f"Сгенерированы параметры:")
        print(f"p = {p}")
        print(f"Ca = {Ca}, Cb = {Cb}")
        print(f"Da = {Da}, Db = {Db}")
    
    process_file(args.input_file, args.output_file, p, Ca, Cb, Da, Db)
    print("Готово.")
