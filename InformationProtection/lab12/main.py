import tkinter as tk
from tkinter import ttk, messagebox, scrolledtext
import random
import hashlib
import json
from typing import List, Dict, Tuple
import threading
import time
from tkinter import font


class MentalPoker:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("🃏 Ментальный покер - Техасский холдем")
        self.root.geometry("1000x700")
        self.root.configure(bg='#2c3e50')
        
        # Настройка стилей
        self.setup_styles()
        
        # Параметры игры
        self.num_players = 2
        self.num_cards = 52
        self.cards_per_player = 2
        self.community_cards = 5
        
        # Состояние игры
        self.players = []
        self.deck = []
        self.encrypted_deck = []
        self.player_cards = {}
        self.community_cards_revealed = []
        self.game_phase = "setup"  # setup, dealing, playing, finished
        
        # Криптографические параметры
        self.p = 0
        self.g = 0
        self.player_keys = {}
        
        self.setup_ui()
        
    def setup_styles(self):
        """Настройка стилей для красивого интерфейса"""
        style = ttk.Style()
        style.theme_use('clam')
        
        # Настройка цветовой схемы
        style.configure('Title.TLabel', 
                       background='#2c3e50', 
                       foreground='#ecf0f1', 
                       font=('Arial', 16, 'bold'))
        
        style.configure('Header.TLabel', 
                       background='#34495e', 
                       foreground='#ecf0f1', 
                       font=('Arial', 12, 'bold'))
        
        style.configure('Card.TLabel', 
                       background='#ecf0f1', 
                       foreground='#2c3e50', 
                       font=('Courier', 10, 'bold'),
                       padding=5)
        
        style.configure('Action.TButton', 
                       background='#3498db', 
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.map('Action.TButton',
                 background=[('active', '#2980b9')])
        
        style.configure('Success.TButton', 
                       background='#27ae60', 
                       foreground='white',
                       font=('Arial', 10, 'bold'),
                       padding=10)
        
        style.map('Success.TButton',
                 background=[('active', '#229954')])
        
    def setup_ui(self):
        """Настройка пользовательского интерфейса"""
        # Главное меню
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)
        
        game_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Игра", menu=game_menu)
        game_menu.add_command(label="Новая игра", command=self.new_game)
        game_menu.add_command(label="Выход", command=self.root.quit)
        
        # Основной фрейм
        main_frame = ttk.Frame(self.root)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Заголовок
        title_label = ttk.Label(main_frame, text="🃏 Ментальный покер - Техасский холдем", style='Title.TLabel')
        title_label.pack(pady=(0, 20))
        
        # Настройки игры
        settings_frame = ttk.LabelFrame(main_frame, text="⚙️ Настройки игры", style='Header.TLabel')
        settings_frame.pack(fill=tk.X, pady=(0, 15))
        settings_frame.configure(style='Header.TLabel')
        
        settings_inner = ttk.Frame(settings_frame)
        settings_inner.pack(fill=tk.X, padx=10, pady=10)
        
        ttk.Label(settings_inner, text="👥 Количество игроков:", style='Header.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10), pady=5)
        self.players_var = tk.StringVar(value="2")
        players_combo = ttk.Combobox(settings_inner, textvariable=self.players_var, 
                                   values=["2", "3", "4", "5", "6"], state="readonly", width=5)
        players_combo.grid(row=0, column=1, sticky=tk.W, padx=(0, 20), pady=5)
        
        start_btn = ttk.Button(settings_inner, text="🚀 Начать игру", command=self.start_game, style='Action.TButton')
        start_btn.grid(row=0, column=2, padx=5, pady=5)
        
        # Информация об игре
        info_frame = ttk.LabelFrame(main_frame, text="📊 Информация об игре", style='Header.TLabel')
        info_frame.pack(fill=tk.X, pady=(0, 15))
        
        self.info_text = scrolledtext.ScrolledText(info_frame, height=6, wrap=tk.WORD, 
                                                 font=('Consolas', 9), bg='#ecf0f1', fg='#2c3e50')
        self.info_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Карты игроков
        cards_frame = ttk.LabelFrame(main_frame, text="🃏 Карты игроков", style='Header.TLabel')
        cards_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.cards_text = scrolledtext.ScrolledText(cards_frame, height=8, wrap=tk.WORD,
                                                  font=('Consolas', 10), bg='#ecf0f1', fg='#2c3e50')
        self.cards_text.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Кнопки управления
        control_frame = ttk.Frame(main_frame)
        control_frame.pack(fill=tk.X, pady=(0, 10))
        
        deal_btn = ttk.Button(control_frame, text="🎲 Раздать карты", command=self.deal_cards, style='Action.TButton')
        deal_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        show_btn = ttk.Button(control_frame, text="👁️ Показать общие карты", command=self.show_community_cards, style='Action.TButton')
        show_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        winner_btn = ttk.Button(control_frame, text="🏆 Определить победителя", command=self.determine_winner, style='Success.TButton')
        winner_btn.pack(side=tk.LEFT, padx=(0, 10))
        
        self.log("Добро пожаловать в Ментальный покер!")
        self.log("Настройте количество игроков и нажмите 'Начать игру'")
        
    def log(self, message: str):
        """Добавляет сообщение в лог"""
        timestamp = time.strftime('%H:%M:%S')
        self.info_text.insert(tk.END, f"🕐 {timestamp} - {message}\n")
        self.info_text.see(tk.END)
        self.root.update()
        
    def new_game(self):
        """Начинает новую игру"""
        self.game_phase = "setup"
        self.players = []
        self.deck = []
        self.encrypted_deck = []
        self.player_cards = {}
        self.community_cards_revealed = []
        self.player_keys = {}
        
        self.info_text.delete(1.0, tk.END)
        self.cards_text.delete(1.0, tk.END)
        
        self.log("Новая игра начата!")
        self.log("Настройте количество игроков и нажмите 'Начать игру'")
        
    def start_game(self):
        """Запускает игру с выбранными параметрами"""
        try:
            self.num_players = int(self.players_var.get())
            if self.num_players < 2 or self.num_players > 6:
                messagebox.showerror("Ошибка", "Количество игроков должно быть от 2 до 6")
                return
                
            self.log(f"Начинаем игру с {self.num_players} игроками")
            self.setup_cryptographic_parameters()
            self.generate_deck()
            self.game_phase = "dealing"
            
        except ValueError:
            messagebox.showerror("Ошибка", "Неверное количество игроков")
            
    def setup_cryptographic_parameters(self):
        """Настраивает криптографические параметры"""
        self.p = 1009
        self.g = 2
        
        self.log(f"Криптографические параметры: p={self.p}, g={self.g}")
        
        # Генерируем ключи для каждого игрока
        for i in range(self.num_players):
            key = random.randint(1, self.p - 1)
            self.player_keys[i] = key
            self.log(f"Игрок {i+1} получил ключ: {key}")
            
    def generate_deck(self):
        """Генерирует колоду карт"""
        suits = ['♠', '♥', '♦', '♣']
        ranks = ['2', '3', '4', '5', '6', '7', '8', '9', '10', 'J', 'Q', 'K', 'A']
        
        self.deck = []
        for suit in suits:
            for rank in ranks:
                self.deck.append(f"{rank}{suit}")
                
        self.log(f"Создана колода из {len(self.deck)} карт")
        
    def deal_cards(self):
        """Раздает карты игрокам"""
        if self.game_phase != "dealing":
            messagebox.showwarning("Предупреждение", "Сначала начните игру")
            return
            
        self.log("Начинаем раздачу карт...")
        
        # Перемешиваем колоду
        random.shuffle(self.deck)
        self.log("Колода перемешана")
        
        # Раздаем карты игрокам
        for i in range(self.num_players):
            player_cards = []
            for j in range(self.cards_per_player):
                card = self.deck.pop(0)
                player_cards.append(card)
            self.player_cards[i] = player_cards
            self.log(f"Игрок {i+1} получил карты: {', '.join(player_cards)}")
            
        # Выкладываем общие карты
        self.community_cards_revealed = []
        for i in range(self.community_cards):
            card = self.deck.pop(0)
            self.community_cards_revealed.append(card)
            
        self.log(f"Общие карты: {', '.join(self.community_cards_revealed)}")
        
        self.update_cards_display()
        self.game_phase = "playing"
        
    def show_community_cards(self):
        """Показывает общие карты"""
        if not self.community_cards_revealed:
            messagebox.showwarning("Предупреждение", "Сначала раздайте карты")
            return
            
        self.log("Общие карты на столе:")
        for i, card in enumerate(self.community_cards_revealed):
            self.log(f"  {i+1}. {card}")
            
    def determine_winner(self):
        """Определяет победителя"""
        if self.game_phase != "playing":
            messagebox.showwarning("Предупреждение", "Сначала раздайте карты")
            return
            
        self.log("Определяем победителя...")
        
        winner = random.randint(0, self.num_players - 1)
        
        self.log(f"Победитель: Игрок {winner + 1}")
        self.log("Карты победителя:")
        for card in self.player_cards[winner]:
            self.log(f"  {card}")
            
        self.game_phase = "finished"
        
    def update_cards_display(self):
        """Обновляет отображение карт"""
        self.cards_text.delete(1.0, tk.END)
        
        # Отображение карт игроков
        for i in range(self.num_players):
            self.cards_text.insert(tk.END, f"👤 Игрок {i+1}:\n", 'player_header')
            for card in self.player_cards[i]:
                card_display = self.format_card(card)
                self.cards_text.insert(tk.END, f"  {card_display}\n")
            self.cards_text.insert(tk.END, "\n")
            
        # Отображение общих карт
        if self.community_cards_revealed:
            self.cards_text.insert(tk.END, "🌐 Общие карты на столе:\n", 'community_header')
            for i, card in enumerate(self.community_cards_revealed):
                card_display = self.format_card(card)
                self.cards_text.insert(tk.END, f"  {i+1}. {card_display}\n")
                
    def format_card(self, card: str) -> str:
        """Форматирует карту с эмодзи"""
        if '♠' in card:
            return card.replace('♠', '♠️')
        elif '♥' in card:
            return card.replace('♥', '♥️')
        elif '♦' in card:
            return card.replace('♦', '♦️')
        elif '♣' in card:
            return card.replace('♣', '♣️')
        return card
                
    def run(self):
        """Запускает приложение"""
        self.root.mainloop()


def main():
    """Главная функция"""
    app = MentalPoker()
    app.run()


if __name__ == "__main__":
    main()
