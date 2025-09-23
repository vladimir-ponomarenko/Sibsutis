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
    """Тест простоты Миллера-Рабина (надежнее, чем тест Ферма)."""
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

    e = 65537
    if extended_gcd(e, phi_n)[0] != 1:        
        raise RuntimeError("Не удалось подобрать e=65537, попробуйте сгенерировать ключи заново.")
        
    d = mod_inverse(e, phi_n)
    public_key = (n, e)
    private_key = (n, d)
    
    return public_key, private_key

def calculate_file_hash(filepath: str) -> bytes:
    """Вычисляет хеш SHA-256 для файла и возвращает его как байтовую строку."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.digest()

def sign_hash(hash_digest: bytes, private_key: Tuple[int, int]) -> list[int]:
    """
    Подписывает каждый байт хеша отдельно, используя закрытый ключ RSA.
    Возвращает список чисел - подпись.
    """
    n, d = private_key
    signature = [mod_pow(byte, d, n) for byte in hash_digest]
    return signature

def verify_signature(hash_digest: bytes, signature: list[int], public_key: Tuple[int, int]) -> bool:
    """
    Проверяет подпись, "расшифровывая" каждый ее компонент открытым ключом.
    Сравнивает результат с исходным хешем.
    """
    n, e = public_key
    decrypted_hash_bytes = [mod_pow(sig_part, e, n) for sig_part in signature]
    original_hash_bytes = list(hash_digest)
    return decrypted_hash_bytes == original_hash_bytes

def save_key(key: Tuple[int, int], filepath: str):
    """Сохраняет ключ (n, e/d) в файл."""
    with open(filepath, 'w') as f:
        f.write(f"{key[0]}\n")
        f.write(f"{key[1]}\n")

def load_key(filepath: str) -> Tuple[int, int]:
    """Загружает ключ из файла."""
    with open(filepath, 'r') as f:
        n = int(f.readline().strip())
        e_or_d = int(f.readline().strip())
    return (n, e_or_d)

def save_signature(signature: list[int], filepath: str):
    """Сохраняет подпись в файл, каждое число на новой строке."""
    with open(filepath, 'w') as f:
        for part in signature:
            f.write(f"{part}\n")

def load_signature(filepath: str) -> list[int]:
    """Загружает подпись из файла."""
    with open(filepath, 'r') as f:
        signature = [int(line.strip()) for line in f]
    return signature


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Реализация электронной подписи RSA.")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Сгенерировать пару ключей RSA.")
    gen_parser.add_argument("--bits", type=int, default=32, help="Размер простых чисел в битах для генерации ключей.")
    gen_parser.add_argument("--pub", default="public.key", help="Файл для сохранения открытого ключа.")
    gen_parser.add_argument("--priv", default="private.key", help="Файл для сохранения закрытого ключа.")
    
    sign_parser = subparsers.add_parser("sign", help="Подписать файл.")
    sign_parser.add_argument("file", help="Файл, который нужно подписать.")
    sign_parser.add_argument("--key", required=True, help="Файл с закрытым ключом.")
    sign_parser.add_argument("--out", default=None, help="Файл для сохранения подписи (по умолчанию file.sig).")
    
    verify_parser = subparsers.add_parser("verify", help="Проверить подпись файла.")
    verify_parser.add_argument("file", help="Файл, подпись которого нужно проверить.")
    verify_parser.add_argument("--key", required=True, help="Файл с открытым ключом.")
    verify_parser.add_argument("--sig", required=True, help="Файл с подписью.")

    args = parser.parse_args()

    try:
        if args.command == "generate":
            print(f"Генерация {args.bits*2}-битных RSA ключей...")
            public_key, private_key = generate_rsa_keys(args.bits)
            save_key(public_key, args.pub)
            save_key(private_key, args.priv)
            print(f"Открытый ключ сохранен в: {args.pub}")
            print(f"Закрытый ключ сохранен в: {args.priv}")

        elif args.command == "sign":
            print(f"Подпись файла: {args.file}")
            private_key = load_key(args.key)
            file_hash = calculate_file_hash(args.file)
            print(f"Хеш файла (SHA-256): {file_hash.hex()}")
            signature = sign_hash(file_hash, private_key)
            
            output_file = args.out if args.out else args.file + ".sig"
            save_signature(signature, output_file)
            print(f"Подпись успешно создана и сохранена в: {output_file}")

        elif args.command == "verify":
            print(f"Проверка подписи для файла: {args.file}")
            public_key = load_key(args.key)
            signature = load_signature(args.sig)
            file_hash = calculate_file_hash(args.file)
            print(f"Хеш файла (SHA-256): {file_hash.hex()}")
            if verify_signature(file_hash, signature, public_key):
                print("\nРЕЗУЛЬТАТ: ПОДПИСЬ ПОДТВЕРЖДЕНА. Файл целостен и аутентичен.")
            else:
                print("\nРЕЗУЛЬТАТ: ПРОВЕРКА НЕ ПРОЙДЕНА. Подпись неверна или файл был изменен.")

    except FileNotFoundError as e:
        print(f"\nОшибка: Файл не найден - {e.filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}", file=sys.stderr)
        sys.exit(1)