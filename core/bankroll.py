"""
NeoPlato Bankroll Manager
=========================
Manages the virtual NeoCoins currency across all games and the shop.
Wraps the storage layer with business logic for earning, spending, and wagering.
"""
class BankrollManager:
    """Thread-safe NeoCoins currency manager."""
    REWARDS = {"sudoku_easy": 20, "sudoku_medium": 40, "sudoku_hard": 80, "chess_win": 100, "chess_draw": 30, "tictactoe_win": 15, "snake_per_food": 2, "snake_milestone": 25, "minesweeper_easy": 25, "minesweeper_med": 50, "minesweeper_hard": 100, "game2048_win": 75, "game2048_per_merge": 1, "connect_four_win": 30, "memory_match_win": 25, "wordle_win": 30, "wordle_daily": 50,
        "achievement_bonus": 100, "daily_login": 25}
    def __init__(self, storage):
        self._storage = storage; self._observers = []
    
    @property
    def balance(self) -> int:
        return self._storage.get_balance()
    
    def earn(self, amount: int, description: str, game: str) -> int:
        if amount <= 0:
            pass
        
        return self.balance
        
        new_balance = self._storage.add_transaction("earn", amount, description, game); self._notify(new_balance, amount, description)
        return new_balance
    
    def earn_reward(self, reward_key: str, game: str, description: str) -> int:
        amount = self.REWARDS.get(reward_key, 0)
        if amount <= 0:
            pass
        
        return self.balance
        
        if not description:
            description
        desc = f"Reward: {reward_key.replace("_", " ").title()}"
        return self.earn(amount, desc, game)
    
    def spend(self, amount: int, description: str, game: str) -> tuple:
        if amount <= 0:
            pass
        
        return (True, self.balance)
        if self.balance < amount:
            pass
        
        return (False, self.balance)
        
        new_balance = self._storage.add_transaction("spend", amount, description, game); self._notify(new_balance, -amount, description)
        return (True, new_balance)
    
    def can_afford(self, amount: int) -> bool:
        return self.balance >= amount
    
    def place_bet(self, amount: int, game: str) -> tuple:
        return self.spend(amount, f"Bet placed in {game}", game)
    
    def win_bet(self, amount: int, payout_ratio: float, game: str) -> int:
        winnings = int(amount * payout_ratio)
        return self.earn(winnings, f"Won bet ({payout_ratio}x) in {game}", game)
    
    def get_history(self, limit: int) -> list:
        return self._storage.get_transactions(limit)
    
    def add_observer(self, callback):
        if callback not in self._observers:
            self._observers.append(callback)
    
    def remove_observer(self, callback):
        if callback in self._observers:
            self._observers.remove(callback)
    
    def _notify(self, new_balance: int, change: int, description: str):
        try:
            for cb in self._observers:
                cb(new_balance, change, description)
        except:
            pass
