import hashlib
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


def generate_dsa_keys(bits: int = 32) -> Tuple[int, int, int, int, int]:
    """
    Генерирует ключи для подписи DSA (FIPS 186).
    Возвращает (p, q, g, x, y) где:
    - p - большое простое число
    - q - простое число, делитель p-1
    - g - элемент порядка q по модулю p
    - x - закрытый ключ
    - y - открытый ключ
    """
    # Генерируем q
    q = gen_probable_prime(bits // 2)
    
    # Генерируем p = k*q + 1 для некоторого k
    while True:
        k = random.randrange(2, 1000)
        p = k * q + 1
        if is_probable_prime(p):
            break
    
    # Находим g - элемент порядка q
    while True:
        h = random.randrange(2, p - 1)
        g = mod_pow(h, (p - 1) // q, p)
        if g != 1:
            break
    
    # Генерируем закрытый ключ
    x = random.randrange(1, q)
    
    # Вычисляем открытый ключ
    y = mod_pow(g, x, p)
    
    return p, q, g, x, y


def calculate_file_hash(filepath: str) -> bytes:
    """Вычисляет хеш SHA-256 для файла и возвращает его как байтовую строку."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.digest()


def dsa_sign(hash_digest: bytes, p: int, q: int, g: int, x: int) -> Tuple[int, int]:
    """
    Подписывает хеш по схеме DSA (FIPS 186).
    Возвращает (r, s) - подпись.
    """
    # Преобразуем хеш в число
    h = int.from_bytes(hash_digest, byteorder='big') % q
    
    # Выбираем случайное k
    k = random.randrange(1, q)
    
    # Вычисляем r = (g^k mod p) mod q
    r = mod_pow(g, k, p) % q
    
    # Вычисляем s = (k^(-1) * (h + x*r)) mod q
    k_inv = mod_inverse(k, q)
    s = (k_inv * (h + x * r)) % q
    
    return r, s


def dsa_verify(hash_digest: bytes, signature: Tuple[int, int], p: int, q: int, g: int, y: int) -> bool:
    """
    Проверяет подпись DSA (FIPS 186).
    Возвращает True, если подпись верна.
    """
    r, s = signature
    
    # Проверяем условия
    if r < 1 or r >= q or s < 1 or s >= q:
        return False
    
    # Преобразуем хеш в число
    h = int.from_bytes(hash_digest, byteorder='big') % q
    
    # Вычисляем w = s^(-1) mod q
    w = mod_inverse(s, q)
    
    # Вычисляем u1 = (h * w) mod q
    u1 = (h * w) % q
    
    # Вычисляем u2 = (r * w) mod q
    u2 = (r * w) % q
    
    # Вычисляем v = (g^u1 * y^u2 mod p) mod q
    v = (mod_pow(g, u1, p) * mod_pow(y, u2, p)) % p % q
    
    # Проверяем: v = r
    return v == r


def save_key(key: Tuple[int, int, int, int], filepath: str):
    """Сохраняет ключ в файл."""
    with open(filepath, 'w') as f:
        for value in key:
            f.write(f"{value}\n")


def load_key(filepath: str) -> Tuple[int, int, int, int]:
    """Загружает ключ из файла."""
    with open(filepath, 'r') as f:
        values = [int(line.strip()) for line in f]
    return tuple(values)


def save_signature(signature: Tuple[int, int], filepath: str):
    """Сохраняет подпись в файл."""
    with open(filepath, 'w') as f:
        f.write(f"{signature[0]}\n")
        f.write(f"{signature[1]}\n")


def load_signature(filepath: str) -> Tuple[int, int]:
    """Загружает подпись из файла."""
    with open(filepath, 'r') as f:
        r = int(f.readline().strip())
        s = int(f.readline().strip())
    return (r, s)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Электронная подпись DSA (FIPS 186)")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Сгенерировать пару ключей DSA")
    gen_parser.add_argument("--bits", type=int, default=32, help="Размер простого числа в битах")
    gen_parser.add_argument("--pub", default="public.key", help="Файл для сохранения открытого ключа")
    gen_parser.add_argument("--priv", default="private.key", help="Файл для сохранения закрытого ключа")
    
    sign_parser = subparsers.add_parser("sign", help="Подписать файл")
    sign_parser.add_argument("file", help="Файл, который нужно подписать")
    sign_parser.add_argument("--key", required=True, help="Файл с закрытым ключом")
    sign_parser.add_argument("--out", default=None, help="Файл для сохранения подписи")
    
    verify_parser = subparsers.add_parser("verify", help="Проверить подпись файла")
    verify_parser.add_argument("file", help="Файл, подпись которого нужно проверить")
    verify_parser.add_argument("--key", required=True, help="Файл с открытым ключом")
    verify_parser.add_argument("--sig", required=True, help="Файл с подписью")

    args = parser.parse_args()

    try:
        if args.command == "generate":
            print(f"Генерация {args.bits}-битных ключей DSA (FIPS 186)...")
            p, q, g, x, y = generate_dsa_keys(args.bits)
            
            public_key = (p, q, g, y)
            private_key = (p, q, g, x)
            
            save_key(public_key, args.pub)
            save_key(private_key, args.priv)
            print(f"Открытый ключ (p, q, g, y) сохранен в: {args.pub}")
            print(f"Закрытый ключ (p, q, g, x) сохранен в: {args.priv}")

        elif args.command == "sign":
            print(f"Подпись файла: {args.file}")
            private_key = load_key(args.key)
            p, q, g, x = private_key
            
            file_hash = calculate_file_hash(args.file)
            print(f"Хеш файла (SHA-256): {file_hash.hex()}")
            
            signature = dsa_sign(file_hash, p, q, g, x)
            
            output_file = args.out if args.out else args.file + ".sig"
            save_signature(signature, output_file)
            print(f"Подпись (r, s) успешно создана и сохранена в: {output_file}")

        elif args.command == "verify":
            print(f"Проверка подписи для файла: {args.file}")
            public_key = load_key(args.key)
            p, q, g, y = public_key
            
            signature = load_signature(args.sig)
            file_hash = calculate_file_hash(args.file)
            print(f"Хеш файла (SHA-256): {file_hash.hex()}")
            
            if dsa_verify(file_hash, signature, p, q, g, y):
                print("\nРЕЗУЛЬТАТ: ПОДПИСЬ ПОДТВЕРЖДЕНА. Файл целостен и аутентичен.")
            else:
                print("\nРЕЗУЛЬТАТ: ПРОВЕРКА НЕ ПРОЙДЕНА. Подпись неверна или файл был изменен.")

    except FileNotFoundError as e:
        print(f"\nОшибка: Файл не найден - {e.filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}", file=sys.stderr)
        sys.exit(1)
