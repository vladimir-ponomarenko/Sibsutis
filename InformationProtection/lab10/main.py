import hashlib
import random
import sys
import argparse
from typing import Tuple, list


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


def generate_gost_keys(bits: int = 32) -> Tuple[int, int, int, int]:
    """
    Генерирует ключи для подписи ГОСТ Р 34.10-94.
    Возвращает (p, q, a, x, y) где:
    - p - большое простое число
    - q - простое число, делитель p-1
    - a - элемент порядка q по модулю p
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
    
    # Находим a - элемент порядка q
    while True:
        a = random.randrange(2, p - 1)
        if mod_pow(a, q, p) == 1:
            break
    
    # Генерируем закрытый ключ
    x = random.randrange(1, q)
    
    # Вычисляем открытый ключ
    y = mod_pow(a, x, p)
    
    return p, q, a, x, y


def calculate_file_hash(filepath: str) -> bytes:
    """Вычисляет хеш SHA-256 для файла и возвращает его как байтовую строку."""
    sha256_hash = hashlib.sha256()
    with open(filepath, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.digest()


def gost_sign(hash_digest: bytes, p: int, q: int, a: int, x: int) -> list[Tuple[int, int]]:
    """
    Подписывает хеш по схеме ГОСТ Р 34.10-94 побайтово.
    Возвращает список пар (r, s) - подпись для каждого байта.
    """
    signature = []
    
    for byte in hash_digest:
        # Выбираем случайное k для каждого байта
        k = random.randrange(1, q)
        
        # Вычисляем r = (a^k mod p) mod q
        r = mod_pow(a, k, p) % q
        
        # Вычисляем s = (k*h + x*r) mod q (формула ГОСТ)
        h = byte % q
        s = (k * h + x * r) % q
        
        signature.append((r, s))
    
    return signature


def gost_verify(hash_digest: bytes, signature: list[Tuple[int, int]], p: int, q: int, a: int, y: int) -> bool:
    """
    Проверяет подпись ГОСТ Р 34.10-94 побайтово.
    Возвращает True, если подпись верна.
    """
    if len(signature) != len(hash_digest):
        return False
    
    for i, (r, s) in enumerate(signature):
        # Проверяем условия
        if r < 1 or r >= q or s < 1 or s >= q:
            return False
        
        # Получаем байт хеша
        h = hash_digest[i] % q
        
        # Вычисляем h^(-1) mod q
        h_inv = mod_inverse(h, q)
        
        # Вычисляем u1 = (s * h_inv) mod q
        u1 = (s * h_inv) % q
        
        # Вычисляем u2 = (-r * h_inv) mod q
        u2 = ((-r) * h_inv) % q
        
        # Вычисляем v = (a^u1 * y^u2 mod p) mod q
        v = (mod_pow(a, u1, p) * mod_pow(y, u2, p)) % p % q
        
        # Проверяем: v = r
        if v != r:
            return False
    
    return True


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


def save_signature(signature: list[Tuple[int, int]], filepath: str):
    """Сохраняет подпись в файл."""
    with open(filepath, 'w') as f:
        for r, s in signature:
            f.write(f"{r} {s}\n")


def load_signature(filepath: str) -> list[Tuple[int, int]]:
    """Загружает подпись из файла."""
    signature = []
    with open(filepath, 'r') as f:
        for line in f:
            line = line.strip()
            if line.startswith('(') and line.endswith(')'):
                # Формат (r, s)
                content = line[1:-1]  # Убираем скобки
                r, s = map(int, content.split(', '))
            else:
                # Формат r s
                r, s = map(int, line.split())
            signature.append((r, s))
    return signature


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="Электронная подпись ГОСТ Р 34.10-94")
    subparsers = parser.add_subparsers(dest="command", required=True)

    gen_parser = subparsers.add_parser("generate", help="Сгенерировать пару ключей ГОСТ")
    gen_parser.add_argument("--bits", type=int, default=256, help="Размер простого числа q в битах (p будет 1024 бита)")
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
            print(f"Генерация ключей ГОСТ Р 34.10-94 (q={args.bits} бит, p=1024 бита)...")
            p, q, a, x, y = generate_gost_keys(args.bits)
            
            public_key = (p, q, a, y)
            private_key = (p, q, a, x)
            
            save_key(public_key, args.pub)
            save_key(private_key, args.priv)
            print(f"Открытый ключ (p, q, a, y) сохранен в: {args.pub}")
            print(f"Закрытый ключ (p, q, a, x) сохранен в: {args.priv}")

        elif args.command == "sign":
            print(f"Подпись файла: {args.file}")
            private_key = load_key(args.key)
            p, q, a, x = private_key
            
            file_hash = calculate_file_hash(args.file)
            print(f"Хеш файла (SHA-256): {file_hash.hex()}")
            print(f"Размер хеша: {len(file_hash)} байт")
            
            signature = gost_sign(file_hash, p, q, a, x)
            
            output_file = args.out if args.out else args.file + ".sig"
            save_signature(signature, output_file)
            print(f"Подпись успешно создана и сохранена в: {output_file}")
            print(f"Размер подписи: {len(signature)} пар (r, s)")

        elif args.command == "verify":
            print(f"Проверка подписи для файла: {args.file}")
            public_key = load_key(args.key)
            p, q, a, y = public_key
            
            signature = load_signature(args.sig)
            file_hash = calculate_file_hash(args.file)
            print(f"Хеш файла (SHA-256): {file_hash.hex()}")
            print(f"Размер хеша: {len(file_hash)} байт")
            print(f"Размер подписи: {len(signature)} пар (r, s)")
            
            if gost_verify(file_hash, signature, p, q, a, y):
                print("\nРЕЗУЛЬТАТ: ПОДПИСЬ ПОДТВЕРЖДЕНА. Файл целостен и аутентичен.")
            else:
                print("\nРЕЗУЛЬТАТ: ПРОВЕРКА НЕ ПРОЙДЕНА. Подпись неверна или файл был изменен.")

    except FileNotFoundError as e:
        print(f"\nОшибка: Файл не найден - {e.filename}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"\nПроизошла ошибка: {e}", file=sys.stderr)
        sys.exit(1)
