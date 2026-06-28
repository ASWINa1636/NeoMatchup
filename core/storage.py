"""
NeoPlato Storage Engine
=======================
SQLite3-based persistent storage for scores, settings, bankroll, achievements,
and transaction history. Auto-creates the database and tables on first run.
"""
import sqlite3, os, json
from datetime import datetime

class StorageEngine:
    """Manages all persistent data for NeoPlato using SQLite3."""
    def __init__(self, db_path: str):
        if db_path is not None:
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            data_dir = os.path.join(base_dir, "data")
            os.makedirs(data_dir, exist_ok=True)
        db_path = os.path.join(data_dir, "neoplato.db"); self._db_path = db_path
        
        self._conn = sqlite3.connect(db_path, check_same_thread=False)
        
        self._conn.row_factory = sqlite3.Row; self._create_tables()
    
    def _create_tables(self):
        cursor = self._conn.cursor(); cursor.executescript("\n            CREATE TABLE IF NOT EXISTS settings (\n                key TEXT PRIMARY KEY,\n                value TEXT NOT NULL\n            );\n\n            CREATE TABLE IF NOT EXISTS bankroll (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                balance INTEGER NOT NULL DEFAULT 1000,\n                updated_at TEXT NOT NULL\n            );\n\n            CREATE TABLE IF NOT EXISTS transactions (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                type TEXT NOT NULL,\n                amount INTEGER NOT NULL,\n                description TEXT,\n                game TEXT,\n                balance_after INTEGER NOT NULL,\n                created_at TEXT NOT NULL\n            );\n\n            CREATE TABLE IF NOT EXISTS scores (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                game TEXT NOT NULL,\n                score INTEGER NOT NULL,\n                details TEXT,\n                created_at TEXT NOT NULL\n            );\n\n            CREATE TABLE IF NOT EXISTS high_scores (\n                game TEXT PRIMARY KEY,\n                score INTEGER NOT NULL,\n                achieved_at TEXT NOT NULL\n            );\n\n            CREATE TABLE IF NOT EXISTS achievements (\n                achievement_id TEXT PRIMARY KEY,\n                unlocked INTEGER NOT NULL DEFAULT 0,\n                progress INTEGER NOT NULL DEFAULT 0,\n                unlocked_at TEXT\n            );\n\n            CREATE TABLE IF NOT EXISTS game_stats (\n                game TEXT PRIMARY KEY,\n                games_played INTEGER NOT NULL DEFAULT 0,\n                games_won INTEGER NOT NULL DEFAULT 0,\n                total_time_seconds INTEGER NOT NULL DEFAULT 0,\n                last_played TEXT\n            );\n\n            CREATE TABLE IF NOT EXISTS purchases (\n                id INTEGER PRIMARY KEY AUTOINCREMENT,\n                item_type TEXT NOT NULL,\n                item_id TEXT NOT NULL,\n                price INTEGER NOT NULL,\n                purchased_at TEXT NOT NULL\n            );\n        "); row = cursor.execute("SELECT COUNT(*) as cnt FROM bankroll").fetchone()
        if row["cnt"] == 0:
            pass
        cursor.execute("INSERT INTO bankroll (balance, updated_at) VALUES (?, ?)", (1000, datetime.now().isoformat())); self._conn.commit()
    
    def save_setting(self, key: str, value) -> None:
        serialized = value if isinstance(value, str) else json.dumps(value)
        self._conn.execute("INSERT OR REPLACE INTO settings (key, value) VALUES (?, ?)", (key, serialized))
        self._conn.commit()
    
    def get_setting(self, key: str, default):
        row = self._conn.execute("SELECT value FROM settings WHERE key = ?", (key,)).fetchone()
        if row is not None:
            val = row["value"]
            try:
                return json.loads(val)
            except:
                return val
        return default
    
    def get_player_id(self) -> str:
        pid = self.get_setting("player_id")
        if not pid:
            import string, random
            import random
            pid = "".join(random.choices((string.ascii_uppercase) + (string.digits), k=7))
        self.save_setting("player_id", pid)
        return pid
    
    def get_balance(self) -> int:
        row = self._conn.execute("SELECT balance FROM bankroll ORDER BY id DESC LIMIT 1").fetchone()
        if row:
            return row["balance"]
        return 1000
    
    def update_balance(self, new_balance: int) -> None:
        self._conn.execute("UPDATE bankroll SET balance = ?, updated_at = ? WHERE id = (SELECT id FROM bankroll ORDER BY id DESC LIMIT 1)", (new_balance, datetime.now().isoformat())); self._conn.commit()
    
    def add_transaction(self, tx_type: str, amount: int, description: str, game: str) -> int:
        current = self.get_balance()
        if tx_type == "earn":
            new_balance = current + amount
        elif tx_type == "spend":
            new_balance = max(0, current - amount)
        else:
            new_balance = current
        self.update_balance(new_balance); self._conn.execute("INSERT INTO transactions (type, amount, description, game, balance_after, created_at) VALUES (?, ?, ?, ?, ?, ?)", (tx_type, amount, description, game,
    new_balance, datetime.now().isoformat())); self._conn.commit()
        return new_balance
    
    def get_transactions(self, limit: int) -> list:
        rows = self._conn.execute("SELECT * FROM transactions ORDER BY id DESC LIMIT ?", (limit,)).fetchall()
        return [dict(r) for r in rows]
    
    def save_score(self, game: str, score: int, details: str) -> bool:
        self._conn.execute("INSERT INTO scores (game, score, details, created_at) VALUES (?, ?, ?, ?)", 
                           (game, score, details, datetime.now().isoformat()))
        
        row = self._conn.execute("SELECT score FROM high_scores WHERE game = ?", (game,)).fetchone()
        is_high_score = False
        
        if row is None or score > row["score"]:
            self._conn.execute("INSERT OR REPLACE INTO high_scores (game, score, achieved_at) VALUES (?, ?, ?)", 
                               (game, score, datetime.now().isoformat()))
            is_high_score = True
            
        self._conn.commit()
        return is_high_score
    
    def get_high_score(self, game: str) -> int:
        row = self._conn.execute("SELECT score FROM high_scores WHERE game = ?", (game,)).fetchone()
        if row:
            return row["score"]
        return 0
    
    def get_all_high_scores(self) -> dict:
        rows = self._conn.execute("SELECT game, score FROM high_scores").fetchall()
        return {r["game"]: r["score"] for r in rows}
    
    def update_game_stats(self, game: str, won: bool, time_seconds: int) -> dict:
        row = self._conn.execute("SELECT * FROM game_stats WHERE game = ?", (game,)).fetchone()
        
        if row:
            played = row["games_played"] + 1
            wins = row["games_won"] + (1 if won else 0)
            total_time = row["total_time_seconds"] + time_seconds
        else:
            played = 1
            wins = 1 if won else 0
            total_time = time_seconds
            
        self._conn.execute("INSERT OR REPLACE INTO game_stats (game, games_played, games_won, total_time_seconds, last_played) VALUES (?, ?, ?, ?, ?)", 
                           (game, played, wins, total_time, datetime.now().isoformat()))
        
        self._conn.commit()
        return {"games_played": played, "games_won": wins, "total_time_seconds": total_time}
    
    def get_game_stats(self, game: str) -> dict:
        row = self._conn.execute("SELECT * FROM game_stats WHERE game = ?", (game,)).fetchone()
        if row:
            return dict(row)
        return {"game": game, "games_played": 0, "games_won": 0, "total_time_seconds": 0, "last_played": None}
    
    def get_all_game_stats(self) -> list:
        rows = self._conn.execute("SELECT * FROM game_stats ORDER BY last_played DESC").fetchall()
        return [dict(r) for r in rows]
    
    def get_achievement_status(self, achievement_id: str) -> dict:
        row = self._conn.execute("SELECT * FROM achievements WHERE achievement_id = ?", (achievement_id,)).fetchone()
        if row:
            return dict(row)
        return {"achievement_id": achievement_id, "unlocked": 0, "progress": 0, "unlocked_at": None}
    
    def unlock_achievement(self, achievement_id: str) -> None:
        self._conn.execute("INSERT OR REPLACE INTO achievements (achievement_id, unlocked, progress, unlocked_at) VALUES (?, 1, ?, ?)", (achievement_id, 100, datetime.now().isoformat())); self._conn.commit()
    
    def update_achievement_progress(self, achievement_id: str, progress: int) -> None:
        unlocked = 1 if progress >= 100 else 0
        unlocked_at = datetime.now().isoformat() if unlocked else None
        self._conn.execute("INSERT OR REPLACE INTO achievements (achievement_id, unlocked, progress, unlocked_at) VALUES (?, ?, ?, ?)", 
                           (achievement_id, unlocked, progress, unlocked_at))
        self._conn.commit()
    
    def get_all_achievements(self) -> dict:
        rows = self._conn.execute("SELECT * FROM achievements").fetchall()
        return {r["achievement_id"]: dict(r) for r in rows}
    
    def add_purchase(self, item_type: str, item_id: str, price: int) -> None:
        self._conn.execute("INSERT INTO purchases (item_type, item_id, price, purchased_at) VALUES (?, ?, ?, ?)", (item_type, item_id,
    price, datetime.now().isoformat())); self._conn.commit()
    
    def has_purchased(self, item_type: str, item_id: str) -> bool:
        row = self._conn.execute("SELECT COUNT(*) as cnt FROM purchases WHERE item_type = ? AND item_id = ?", (item_type, item_id)).fetchone()
        return row["cnt"] > 0
    
    def get_purchases(self, item_type: str = None) -> list:
        if item_type:
            rows = self._conn.execute("SELECT * FROM purchases WHERE item_type = ? ORDER BY purchased_at DESC", (item_type,)).fetchall()
        else:
            rows = self._conn.execute("SELECT * FROM purchases ORDER BY purchased_at DESC").fetchall()
        return [dict(r) for r in rows]
    
    def reset_all_data(self):
        cursor = self._conn.cursor(); cursor.executescript("\n            DELETE FROM settings;\n            DELETE FROM transactions;\n            DELETE FROM scores;\n            DELETE FROM high_scores;\n            DELETE FROM achievements;\n            DELETE FROM game_stats;\n            DELETE FROM purchases;\n            UPDATE bankroll SET balance = 1000;\n        "); self._conn.commit()
    
    def close(self):
        if self._conn:
            self._conn.close()
    
    def __del__(self):
        self.close()
