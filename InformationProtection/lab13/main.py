import hashlib
import random
import sys
import argparse
import json
import threading
import time
from typing import Tuple, Dict, List
from dataclasses import dataclass


@dataclass
class Ballot:
    """Бюллетень для голосования"""
    voter_id: str
    choice: str
    blinded_message: int
    r: int = None
    signature: int = None
    unblinded_signature: int = None


class BlindSignatureSystem:
    """Система слепой подписи для анонимного голосования"""
    
    def __init__(self, p: int, g: int, x: int, y: int):
        self.p = p
        self.g = g
        self.x = x  # Закрытый ключ сервера
        self.y = y  # Открытый ключ сервера
        self.ballots: List[Ballot] = []
        self.voted_voters: set = set()
        
    def generate_blinding_factor(self) -> int:
        """Генерирует случайный фактор ослепления"""
        return random.randint(1, self.p - 1)
    
    def blind_message(self, message: int, r: int) -> int:
        """Ослепляет сообщение для подписи"""
        return (message * pow(self.y, r, self.p)) % self.p
    
    def sign_blinded_message(self, blinded_message: int) -> int:
        """Подписывает ослепленное сообщение"""
        return pow(blinded_message, self.x, self.p)
    
    def unblind_signature(self, signature: int, r: int) -> int:
        """Снимает ослепление с подписи"""
        r_inv = pow(r, -1, self.p - 1)
        return (signature * pow(r_inv, 1, self.p)) % self.p
    
    def verify_signature(self, message: int, signature: int) -> bool:
        """Проверяет подпись сообщения"""
        return pow(self.g, message, self.p) == pow(self.y, signature, self.p)
    
    def submit_ballot(self, voter_id: str, choice: str) -> bool:
        """Подает бюллетень на голосование"""
        if voter_id in self.voted_voters:
            print(f"Ошибка: Избиратель {voter_id} уже голосовал")
            return False
        
        # Генерируем хеш выбора
        choice_hash = int(hashlib.sha256(choice.encode()).hexdigest(), 16) % self.p
        
        # Генерируем фактор ослепления
        r = self.generate_blinding_factor()
        
        # Ослепляем сообщение
        blinded_message = self.blind_message(choice_hash, r)
        
        # Создаем бюллетень
        ballot = Ballot(
            voter_id=voter_id,
            choice=choice,
            blinded_message=blinded_message,
            r=r
        )
        
        self.ballots.append(ballot)
        self.voted_voters.add(voter_id)
        
        print(f"Бюллетень от {voter_id} принят")
        return True
    
    def sign_ballot(self, ballot: Ballot) -> bool:
        """Подписывает бюллетень"""
        if ballot.signature is not None:
            print(f"Бюллетень от {ballot.voter_id} уже подписан")
            return False
        
        # Подписываем ослепленное сообщение
        ballot.signature = self.sign_blinded_message(ballot.blinded_message)
        
        # Снимаем ослепление
        ballot.unblinded_signature = self.unblind_signature(ballot.signature, ballot.r)
        
        print(f"Бюллетень от {ballot.voter_id} подписан")
        return True
    
    def verify_ballot(self, ballot: Ballot) -> bool:
        """Проверяет подпись бюллетеня"""
        if ballot.unblinded_signature is None:
            print(f"Бюллетень от {ballot.voter_id} не подписан")
            return False
        
        choice_hash = int(hashlib.sha256(ballot.choice.encode()).hexdigest(), 16) % self.p
        return self.verify_signature(choice_hash, ballot.unblinded_signature)
    
    def count_votes(self) -> Dict[str, int]:
        """Подсчитывает голоса"""
        results = {}
        for ballot in self.ballots:
            if self.verify_ballot(ballot):
                choice = ballot.choice
                results[choice] = results.get(choice, 0) + 1
            else:
                print(f"Недействительный бюллетень от {ballot.voter_id}")
        
        return results


class VotingServer:
    """Сервер для анонимного голосования"""
    
    def __init__(self, p: int, g: int, x: int, y: int):
        self.blind_system = BlindSignatureSystem(p, g, x, y)
        self.running = False
        
    def start_server(self):
        """Запускает сервер"""
        self.running = True
        print("Сервер голосования запущен")
        print(f"Параметры: p={self.blind_system.p}, g={self.blind_system.g}")
        print(f"Открытый ключ: y={self.blind_system.y}")
        
    def stop_server(self):
        """Останавливает сервер"""
        self.running = False
        print("Сервер голосования остановлен")
        
    def process_ballots(self):
        """Обрабатывает все бюллетени"""
        print("Обработка бюллетеней...")
        for ballot in self.blind_system.ballots:
            if ballot.signature is None:
                self.blind_system.sign_ballot(ballot)
        
        print("Все бюллетени обработаны")
        
    def get_results(self):
        """Получает результаты голосования"""
        results = self.blind_system.count_votes()
        print("Результаты голосования:")
        for choice, count in results.items():
            print(f"  {choice}: {count} голосов")
        return results


class VotingClient:
    """Клиент для голосования"""
    
    def __init__(self, voter_id: str, server: VotingServer):
        self.voter_id = voter_id
        self.server = server
        
    def vote(self, choice: str) -> bool:
        """Голосует за выбранный вариант"""
        if not self.server.running:
            print("Сервер не запущен")
            return False
        
        return self.server.blind_system.submit_ballot(self.voter_id, choice)


def generate_parameters(bits: int = 32) -> Tuple[int, int, int, int]:
    """Генерирует криптографические параметры"""
    p = 1009  # Простое число
    g = 2     # Первообразный корень
    
    x = random.randint(1, p - 1)
    y = pow(g, x, p)
    
    return p, g, x, y


def main():
    """Главная функция"""
    parser = argparse.ArgumentParser(description="Система анонимного голосования со слепой подписью")
    parser.add_argument("--mode", choices=['server', 'client'], required=True,
                        help="Режим работы: server или client")
    parser.add_argument("--voter-id", help="ID избирателя (только для клиента)")
    parser.add_argument("--choice", help="Выбор избирателя (только для клиента)")
    parser.add_argument("--bits", type=int, default=32, help="Размер параметров в битах")
    parser.add_argument("--daemon", action='store_true', help="Запуск сервера в режиме демона (без интерактивного ввода)")
    
    args = parser.parse_args()
    
    print("=== Система анонимного голосования со слепой подписью ===")
    
    # Генерируем параметры
    p, g, x, y = generate_parameters(args.bits)
    
    if args.mode == 'server':
        # Запускаем сервер
        server = VotingServer(p, g, x, y)
        server.start_server()
        
        if args.daemon:
            # Режим демона - сервер работает без интерактивного ввода
            print("Сервер запущен в режиме демона.")
            print("Используйте Ctrl+C для остановки.")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                print("\nСервер остановлен")
                server.stop_server()
        else:
            # Интерактивный режим
            try:
                while True:
                    try:
                        command = input("\nВведите команду (help для справки): ").strip().lower()
                    except EOFError:
                        print("\nСервер работает в фоновом режиме. Используйте Ctrl+C для остановки.")
                        print("Доступные команды:")
                        print("  process - обработать бюллетени")
                        print("  results - показать результаты")
                        print("  status - показать статус")
                        print("  quit - выйти")
                        break
                    
                    if command == 'help':
                        print("Доступные команды:")
                        print("  process - обработать бюллетени")
                        print("  results - показать результаты")
                        print("  status - показать статус")
                        print("  quit - выйти")
                        
                    elif command == 'process':
                        server.process_ballots()
                        
                    elif command == 'results':
                        server.get_results()
                        
                    elif command == 'status':
                        print(f"Бюллетеней: {len(server.blind_system.ballots)}")
                        print(f"Проголосовало: {len(server.blind_system.voted_voters)}")
                        
                    elif command == 'quit':
                        break
                        
                    else:
                        print("Неизвестная команда")
                        
            except KeyboardInterrupt:
                print("\nСервер остановлен пользователем")
            finally:
                server.stop_server()
            
    elif args.mode == 'client':
        # Запускаем клиент
        if not args.voter_id or not args.choice:
            print("Ошибка: необходимо указать --voter-id и --choice")
            sys.exit(1)
            
        server = VotingServer(p, g, x, y)
        server.start_server()
        
        client = VotingClient(args.voter_id, server)
        
        if client.vote(args.choice):
            print(f"Голосование успешно: {args.voter_id} проголосовал за {args.choice}")
        else:
            print("Ошибка при голосовании")
            
        server.stop_server()


if __name__ == '__main__':
    main()
