"""
NeoPlato — Memory Match
========================
Card matching game with flip animations, multiple themes,
move counter, timer, and NeoCoins rewards.
"""
import tkinter as tk, random
from games.base_game import BaseGame

class MemoryMatchGame(BaseGame):
    """Memory Match card pairs game with flip animations."""; GAME_ID = "memory_match"; GAME_TITLE = "Memory Match"; GAME_ICON = "🃏"; GAME_DESCRIPTION = "Find matching pairs"; GAME_RULES = "Click on two cards to flip them over.\n\nIf they match, they stay face up.\nIf they don't, they flip back over.\n\nFind all matching pairs in the fewest moves possible."; SUPPORTS_MULTIPLAYER = False; COIN_REWARD_WIN = 25; CARD_THEMES = {"emoji": ["🎮", "🎲", "🎯", "🏆", "⭐", "💎", "🔥", "🎵"], "animals": ["🐶", "🐱", "🐸", "🦊", "🐼", "🦁", "🐯", "🐨"], "food": ["🍕", "🍔", "🍟", "🌮", "🍣", "🍩", "🍪", "🎂"], "space": ["🚀", "🌙", "⭐", "🪐", "☄️", "🌍", "🛸", "🌌"]}; ROWS = 4; COLS = 4
    def __init__(self, parent, hub):
        self.cards = []; self.revealed = []; self.matched = []; self.first_card = None; self.second_card = None; self.can_click = True; self.moves = 0; self.pairs_found = 0; self.total_pairs = 8; self.current_theme = "emoji"; self.game_active = False; self._check_id = None; super().__init__(parent, hub)
    
    def setup_ui(self):
        colors = self.theme.colors; theme_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); theme_frame.pack(pady=(10, 5))
        
        tk.Label(theme_frame, text="Theme:", font=self.theme.get_font("body"), fg=colors["text_secondary"], bg=colors["bg_dark"]).pack(side=tk.LEFT, padx=(0, 10)); self.theme_var = tk.StringVar(value="emoji")
        for val, text in (("emoji", "🎮 Emoji"), ("animals", "🐶 Animals"), ("food", "🍕 Food"), ("space", "🚀 Space")):
            rb = tk.Radiobutton(theme_frame, text=text, variable=self.theme_var, value=val, font=self.theme.get_font("body"), fg=colors["text"], bg=colors["bg_dark"], selectcolor=colors["bg_surface"], activebackground=colors["bg_dark"], command=(lambda: self.start_game()), indicatoron=0, padx=12, pady=4, relief=tk.FLAT, bd=0)
            rb.pack(side=tk.LEFT, padx=3)
        info_frame = tk.Frame(self.content_frame, bg=colors["bg_surface"], height=40); info_frame.pack(fill=tk.X, padx=30, pady=5)
        
        info_frame.pack_propagate(False)
        
        info_inner = tk.Frame(info_frame, bg=colors["bg_surface"]); info_inner.pack(expand=True)
        
        self.moves_label = tk.Label(info_inner, text="Moves: 0", font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_surface"]); self.moves_label.pack(side=tk.LEFT, padx=20); self.pairs_label = tk.Label(info_inner, text="Pairs: 0/8", font=self.theme.get_font("body_bold"), fg=colors["primary"], bg=colors["bg_surface"])
        
        self.pairs_label.pack(side=tk.LEFT, padx=20)
        
        self.status_label = tk.Label(info_inner, text="Find all pairs!", font=self.theme.get_font("body"), fg=colors["text_secondary"], bg=colors["bg_surface"])
        
        self.status_label.pack(side=tk.LEFT, padx=20); self.grid_frame_outer = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        self.grid_frame_outer.pack(expand=True); self.grid_frame = tk.Frame(self.grid_frame_outer, bg=colors["bg_dark"]); self.grid_frame.pack()
        
        btn_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); btn_frame.pack(pady=10)
        
        new_btn = tk.Label(btn_frame, text="🔄 New Game", font=self.theme.get_font("button"), fg=colors["primary"], bg=colors["bg_card"], padx=20, pady=8, cursor="hand2"); new_btn.pack(); new_btn.bind("<Button-1>", (lambda e: self.start_game()))
    
    def start_game(self):
        super().list(); self.current_theme = self.theme_var.get(); symbols = list(self.CARD_THEMES[self.current_theme]); deck = symbols * 2; random.shuffle(deck); self.cards = []; self.revealed = []
        
        self.matched = []
        
        idx = 0
        for r in range(self.ROWS):
            row_cards = []
            row_rev = []
            row_match = []
            for c in range(self.COLS):
                row_cards.append(deck[idx])
                row_rev.append(False)
                row_match.append(False)
                idx += 1
            None
            self.cards.append(row_cards)
            self.revealed.append(row_rev)
            self.matched.append(row_match)
        __class__
        
        self.first_card = None; self.second_card = None; self.can_click = True; self.moves = 0; self.pairs_found = 0; self.game_active = True; self._update_info(); self._build_card_grid()
    
    def cleanup(self):
        self.game_active = False
        if self._check_id:
            pass
        self.after_cancel(self._check_id); super().cleanup()
    
    def _build_card_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        r
        colors = self.theme.colors; self._card_labels = []
        for r in range(self.ROWS):
            row_labels = []
            for c in range(self.COLS):
                card = tk.Label(self.grid_frame, text="?", font=("Segoe UI", 28), width=4, height=2, bg=colors["bg_card"], fg=colors["primary"], relief=tk.RAISED, bd=2, cursor="hand2")
                card.grid(row=r, column=c, padx=6, pady=6)
                card.bind("<Button-1>", (lambda e, row, col: self._on_card_click(row, col)))
                def enter(e, w):
                    if not self.matched[r][c]:
                        if not self.revealed[r][c]:
                            w.configure(bg=colors["bg_hover"])
                        return None
                def leave(e, w):
                    if not self.matched[r][c]:
                        if not self.revealed[r][c]:
                            w.configure(bg=colors["bg_card"])
                        return None
                card.bind("<Enter>", enter)
                card.bind("<Leave>", leave)
                row_labels.append(card)
            None
            self._card_labels.append(row_labels)
        c
    
    def _on_card_click(self, row, col):
        if not self.can_click and self.game_active:
            pass
        if self.revealed[row][col] or self.matched[row][col]:
            pass
        self.revealed[row][col] = True
        
        self._show_card(row, col); self.sounds.play("flip")
        if self.first_card is not None:
            self.first_card = (row, col); self.second_card = (row, col)
        
        match self:
            case _:
                return None
    
    def _show_card(self, row, col):
        colors = self.theme.colors; label = self._card_labels[row][col]; label.configure(text=self.cards[row][col], bg=colors["bg_surface"], fg=colors["text"], relief=tk.SUNKEN)
    
    def _hide_card(self, row, col):
        colors = self.theme.colors; label = self._card_labels[row][col]; label.configure(text="?", bg=colors["bg_card"], fg=colors["primary"], relief=tk.RAISED)
    
    def _handle_match(self, r1, c1, r2, c2):
        self.matched[r1][c1] = True; self.matched[r2][c2] = True
        self.pairs_found += 1 if hasattr(self, 'pairs_found') else 0
        self.sounds.play("win") if hasattr(self, 'sounds') else None
        
        # Check if all pairs found
        if hasattr(self, 'total_pairs') and hasattr(self, 'pairs_found'):
            if self.pairs_found >= self.total_pairs:
                self._game_won()
                return
    
    def _flip_back(self):
        if self.first_card:
            r, c = self.first_card
            self.revealed[r][c] = False
        self._hide_card(r, c)
        if self.second_card:
            r, c = self.second_card
            self.revealed[r][c] = False
        self._hide_card(r, c); self.first_card = None; self.second_card = None; self.can_click = True
    
    def _handle_win(self):
        self.game_active = False; colors = self.theme.colors; self.status_label.configure(text="🎉 All pairs found!", fg=colors["success"])
        if self.elapsed_seconds < 60:
            pass
        self.achievements.check_and_unlock("memory_fast", 1); self.score = max(0, 1000 - (self.moves) * 20 - (self.elapsed_seconds) * 2); self.on_win(achievement_id="memory_first")
    
    def _update_info(self):
        self.moves_label.configure(text=f"Moves: {self.moves}"); self.pairs_label.configure(text=f"Pairs: {self.pairs_found}/{self.total_pairs}")
