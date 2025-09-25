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


def generate_rsa_keys(bits: int = 32) -> Tuple[Tuple[int, int], Tuple[int, int]]:
    """
    Генерирует пару RSA ключей.
    Возвращает ((n, e), (n, d)), где (n, e) - открытый ключ, (n, d) - закрытый ключ.
    """
    p = gen_probable_prime(bits)
    q = gen_probable_prime(bits)
    while p == q:
        q = gen_probable_prime(bits)

    n = p * q
    phi_n = (p - 1) * (q - 1)

    # Выбираем e = 65537 (стандартное значение)
    e = 65537
    if extended_gcd(e, phi_n)[0] != 1:
        # Если 65537 не подходит, ищем другое e
        e = 3
        while extended_gcd(e, phi_n)[0] != 1:
            e += 2
    
    d = mod_inverse(e, phi_n)
    public_key = (n, e)
    private_key = (n, d)
    
    return public_key, private_key


def rsa_encrypt(data: bytes, public_key: Tuple[int, int]) -> bytes:
    """Шифрует данные по схеме RSA."""
    n, e = public_key
    result = bytearray()
    
    for byte in data:
        # Шифрование: C = M^e mod n
        encrypted_byte = mod_pow(byte, e, n)
        
        # Сохраняем как два байта (для простоты)
        result.append((encrypted_byte >> 8) & 0xFF)
        result.append(encrypted_byte & 0xFF)
    
    return bytes(result)


def rsa_decrypt(encrypted_data: bytes, private_key: Tuple[int, int]) -> bytes:
    """Расшифровывает данные по схеме RSA."""
    n, d = private_key
    result = bytearray()
    
    # Обрабатываем данные парами
    for i in range(0, len(encrypted_data), 2):
        if i + 1 >= len(encrypted_data):
            break
            
        # Восстанавливаем зашифрованное значение
        encrypted_byte = (encrypted_data[i] << 8) | encrypted_data[i + 1]
        
        # Расшифрование: M = C^d mod n
        decrypted_byte = mod_pow(encrypted_byte, d, n)
        
        result.append(decrypted_byte % 256)
    
    return bytes(result)


def process_file(input_path: str, output_path: str, public_key: Tuple[int, int], 
                private_key: Tuple[int, int], encrypt: bool):
    """Обрабатывает файл с помощью шифра RSA."""
    action = "Шифрование" if encrypt else "Расшифрование"
    print(f"{action} файла: {input_path}")
    print(f"Открытый ключ (n, e): {public_key}")
    print(f"Закрытый ключ (n, d): {private_key}")
    
    try:
        with open(input_path, 'rb') as f:
            data = f.read()
        
        print(f"Размер файла: {len(data)} байт")
        
        if encrypt:
            processed_data = rsa_encrypt(data, public_key)
        else:
            processed_data = rsa_decrypt(data, private_key)
        
        with open(output_path, 'wb') as f:
            f.write(processed_data)
        
        print(f"Результат сохранен в: {output_path}")
        
    except FileNotFoundError:
        print(f"Ошибка: Файл не найден - {input_path}")
    except Exception as e:
        print(f"Ошибка при обработке файла: {e}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Шифр RSA для шифрования файлов")
    parser.add_argument("input_file", help="Входной файл")
    parser.add_argument("output_file", help="Выходной файл")
    parser.add_argument("--action", choices=['encrypt', 'decrypt'], required=True,
                        help="Действие: encrypt или decrypt")
    parser.add_argument("--mode", choices=['input', 'generate'], default='generate',
                        help="Режим: input - ввод параметров, generate - генерация")
    parser.add_argument("--bits", type=int, default=32, help="Размер простых чисел в битах")
    
    args = parser.parse_args()
    
    print("=== Лабораторная работа №6: Шифр RSA ===")
    
    if args.mode == 'input':
        try:
            n = int(input("Введите модуль n: "))
            e = int(input("Введите открытую экспоненту e: "))
            d = int(input("Введите закрытую экспоненту d: "))
            
            public_key = (n, e)
            private_key = (n, d)
            
            # Проверка корректности ключей
            test_byte = 42
            encrypted = mod_pow(test_byte, e, n)
            decrypted = mod_pow(encrypted, d, n)
            
            if decrypted != test_byte:
                print("Ошибка: ключи не корректны")
                sys.exit(1)
                
        except ValueError as e:
            print(f"Ошибка ввода: {e}")
            sys.exit(1)
    else:
        print("Генерация ключей...")
        public_key, private_key = generate_rsa_keys(args.bits)
        print(f"Сгенерированы ключи:")
        print(f"Открытый ключ (n, e): {public_key}")
        print(f"Закрытый ключ (n, d): {private_key}")
    
    encrypt = args.action == 'encrypt'
    process_file(args.input_file, args.output_file, public_key, private_key, encrypt)
    print("Готово.")
