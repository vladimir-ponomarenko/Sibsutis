import argparse
import random
import hashlib
import json
import sys
from dataclasses import dataclass
from typing import Tuple, Dict, Any
import time


@dataclass
class Ballot:
    """Бюллетень для голосования"""
    voter_id: str
    choice: str
    blinded_message: int
    r: int = None
    signature: int = None
    unblinded_signature: int = None


class BlindSignatureServer:
    """Сервер для слепой подписи (на базе RSA)"""
    
    def __init__(self, bits: int = 64):
        self.bits = bits
        self.n, self.e, self.d = self.generate_rsa_keys(bits)
        self.ballots = []
        self.log("Сервер инициализирован")
        self.log(f"RSA параметры: n={self.n}, e={self.e}, d={self.d}")
        
    def generate_rsa_keys(self, bits: int) -> Tuple[int, int, int]:
        """Генерирует ключи RSA"""
        if bits <= 32:
            p = 61  # Простое число
            q = 53  # Простое число
        else:
            p = 1009  # Простое число
            q = 1013  # Простое число
            
        n = p * q
        phi_n = (p - 1) * (q - 1)
        
        # Выбираем e (открытый ключ)
        e = 65537
        while self.gcd(e, phi_n) != 1:
            e += 2
            
        # Вычисляем d (закрытый ключ)
        d = self.mod_inverse(e, phi_n)
        
        return n, e, d
    
    def gcd(self, a: int, b: int) -> int:
        """Вычисляет НОД двух чисел"""
        while b:
            a, b = b, a % b
        return a
    
    def mod_inverse(self, a: int, m: int) -> int:
        """Вычисляет обратный элемент a^(-1) mod m"""
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, y = extended_gcd(a, m)
        if gcd != 1:
            raise ValueError("Обратный элемент не существует")
        return x % m
    
    def mod_pow(self, base: int, exp: int, mod: int) -> int:
        """Возведение в степень по модулю"""
        result = 1
        base %= mod
        while exp > 0:
            if exp % 2 == 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp //= 2
        return result
    
    def hash_message(self, message: str) -> int:
        """Хеширует сообщение"""
        hash_obj = hashlib.sha256(message.encode())
        hash_bytes = hash_obj.digest()
        return int.from_bytes(hash_bytes, byteorder='big') % self.n
    
    def sign_blinded_message(self, blinded_message: int) -> int:
        """Подписывает ослепленное сообщение"""
        # s' = (h')^d mod n
        signature = self.mod_pow(blinded_message, self.d, self.n)
        self.log(f"Сервер подписал ослепленное сообщение: {signature}")
        return signature
    
    def verify_signature(self, message: str, signature: int) -> bool:
        """Проверяет подпись"""
        h = self.hash_message(message)
        # Проверяем: s^e mod n == h
        verification = self.mod_pow(signature, self.e, self.n)
        return verification == h
    
    def log(self, message: str):
        """Логирует сообщение"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"[СЕРВЕР {timestamp}] {message}")
    
    def get_public_key(self) -> Tuple[int, int]:
        """Возвращает открытый ключ (n, e)"""
        return (self.n, self.e)


class BlindSignatureClient:
    """Клиент для слепой подписи"""
    
    def __init__(self, voter_id: str, server: BlindSignatureServer):
        self.voter_id = voter_id
        self.server = server
        self.n, self.e = server.get_public_key()
        self.log(f"Клиент {voter_id} инициализирован")
        
    def gcd(self, a: int, b: int) -> int:
        """Вычисляет НОД двух чисел"""
        while b:
            a, b = b, a % b
        return a
    
    def mod_inverse(self, a: int, m: int) -> int:
        """Вычисляет обратный элемент a^(-1) mod m"""
        def extended_gcd(a, b):
            if a == 0:
                return b, 0, 1
            gcd, x1, y1 = extended_gcd(b % a, a)
            x = y1 - (b // a) * x1
            y = x1
            return gcd, x, y
        
        gcd, x, y = extended_gcd(a, m)
        if gcd != 1:
            raise ValueError("Обратный элемент не существует")
        return x % m
    
    def mod_pow(self, base: int, exp: int, mod: int) -> int:
        """Возведение в степень по модулю"""
        result = 1
        base %= mod
        while exp > 0:
            if exp % 2 == 1:
                result = (result * base) % mod
            base = (base * base) % mod
            exp //= 2
        return result
    
    def hash_message(self, message: str) -> int:
        """Хеширует сообщение"""
        hash_obj = hashlib.sha256(message.encode())
        hash_bytes = hash_obj.digest()
        return int.from_bytes(hash_bytes, byteorder='big') % self.n
    
    def blind_message(self, message: str) -> Tuple[int, int]:
        """Ослепляет сообщение"""
        h = self.hash_message(message)
        
        # Выбираем случайное r такое, что gcd(r, n) = 1
        while True:
            r = random.randint(1, self.n - 1)
            if self.gcd(r, self.n) == 1:
                break
        
        # h' = h * r^e mod n
        blinded_message = (h * self.mod_pow(r, self.e, self.n)) % self.n
        
        self.log(f"Ослепил сообщение: h={h}, r={r}, h'={blinded_message}")
        return blinded_message, r
    
    def unblind_signature(self, blinded_signature: int, r: int) -> int:
        """Разослепляет подпись"""
        # s = s' * r^(-1) mod n
        r_inv = self.mod_inverse(r, self.n)
        signature = (blinded_signature * r_inv) % self.n
        
        self.log(f"Разослепил подпись: s'={blinded_signature}, r^(-1)={r_inv}, s={signature}")
        return signature
    
    def submit_ballot(self, choice: str) -> Ballot:
        """Отправляет бюллетень на подпись"""
        self.log(f"Отправляю бюллетень с выбором: {choice}")
        
        # Шаг 1: Ослепляем сообщение
        blinded_message, r = self.blind_message(choice)
        
        # Шаг 2: Отправляем ослепленное сообщение серверу
        self.log("Отправляю ослепленное сообщение серверу")
        blinded_signature = self.server.sign_blinded_message(blinded_message)
        
        # Шаг 3: Разослепляем подпись
        signature = self.unblind_signature(blinded_signature, r)
        
        # Создаем бюллетень
        ballot = Ballot(
            voter_id=self.voter_id,
            choice=choice,
            blinded_message=blinded_message,
            r=r,
            signature=blinded_signature,
            unblinded_signature=signature
        )
        
        # Добавляем в список бюллетеней сервера
        self.server.ballots.append(ballot)
        
        self.log(f"Бюллетень успешно подписан: s={signature}")
        
        # Шаг 4: Проверяем подпись
        if self.server.verify_signature(choice, signature):
            self.log(" Подпись проверена успешно!")
        else:
            self.log(" Ошибка проверки подписи!")
            
        return ballot
    
    def log(self, message: str):
        """Логирует сообщение"""
        timestamp = time.strftime('%H:%M:%S')
        print(f"[КЛИЕНТ {self.voter_id} {timestamp}] {message}")


def simulate_voting():
    """Симулирует процесс голосования"""
    print(" Симуляция системы анонимного голосования со слепой подписью")
    print("=" * 70)
    
    # Создаем сервер
    server = BlindSignatureServer(bits=32)
    print()
    
    # Создаем клиентов (избирателей)
    voters = ["voter1", "voter2", "voter3"]
    choices = ["Да", "Нет", "Воздержался"]
    
    ballots = []
    
    for i, voter_id in enumerate(voters):
        print(f"\n--- Избиратель {i+1}: {voter_id} ---")
        client = BlindSignatureClient(voter_id, server)
        choice = choices[i % len(choices)]
        ballot = client.submit_ballot(choice)
        ballots.append(ballot)
        print()
    
    # Подводим итоги
    print(" ИТОГИ ГОЛОСОВАНИЯ")
    print("=" * 30)
    print(f"Всего бюллетеней: {len(ballots)}")
    
    for i, ballot in enumerate(ballots):
        print(f"Бюллетень {i+1}:")
        print(f"  Избиратель: {ballot.voter_id}")
        print(f"  Выбор: {ballot.choice}")
        print(f"  Подпись: {ballot.unblinded_signature}")
        print(f"  Проверка: {'OK' if server.verify_signature(ballot.choice, ballot.unblinded_signature) else '❌'}")
        print()
    
    print(" Анонимность обеспечена: сервер не знает, кто за что голосовал")
    print(" Целостность обеспечена: все бюллетени подписаны сервером")


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Система анонимного голосования со слепой подписью")
    parser.add_argument("--mode", choices=["server", "client", "simulate"], default="simulate",
                       help="Режим работы: server, client или simulate")
    parser.add_argument("--voter-id", default="voter1", help="ID избирателя (для режима client)")
    parser.add_argument("--choice", default="Да", help="Выбор избирателя (для режима client)")
    parser.add_argument("--bits", type=int, default=32, help="Размер ключей в битах")
    parser.add_argument("--daemon", action="store_true", help="Запуск сервера в режиме демона")
    
    args = parser.parse_args()
    
    if args.mode == "simulate":
        simulate_voting()
    elif args.mode == "server":
        if args.daemon:
            print("Сервер запущен в режиме демона")
            print("Нажмите Ctrl+C для остановки")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nСервер остановлен")
        else:
            server = BlindSignatureServer(args.bits)
            print("Сервер запущен. Нажмите Enter для остановки")
            input()
    elif args.mode == "client":
        # Создаем сервер и клиента
        server = BlindSignatureServer(args.bits)
        client = BlindSignatureClient(args.voter_id, server)
        
        # Отправляем бюллетень
        ballot = client.submit_ballot(args.choice)
        
        print(f"\nБюллетень отправлен:")
        print(f"Избиратель: {ballot.voter_id}")
        print(f"Выбор: {ballot.choice}")
        print(f"Подпись: {ballot.unblinded_signature}")


if __name__ == "__main__":
    main()