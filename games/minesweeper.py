"""
NeoPlato — Minesweeper
=======================
Classic Minesweeper with flag system, timer, cascade reveal animation,
and difficulty levels. First click never hits a mine.
"""
import tkinter as tk, random
from games.base_game import BaseGame

class MinesweeperGame(BaseGame):
    """Minesweeper with multiple difficulty levels."""; GAME_ID = "minesweeper"; GAME_TITLE = "Minesweeper"; GAME_ICON = "💣"; GAME_DESCRIPTION = "Classic Minesweeper"; GAME_RULES = "Click on squares to reveal them.\n\nNumbers indicate how many mines are adjacent to that square.\nRight-click to flag suspected mines.\n\nClear all safe squares to win!"; SUPPORTS_MULTIPLAYER = False; COIN_REWARD_WIN = 25; DIFFICULTIES = {"easy": {"rows": 9, "cols": 9, "mines": 10, "reward": 25}, "medium": {"rows": 16, "cols": 16, "mines": 40, "reward": 50}, "hard": {"rows": 16, "cols": 30, "mines": 99, "reward": 100}}
    def __init__(self, parent, hub):
        self.difficulty = "easy"; self.rows = 9; self.cols = 9; self.num_mines = 10; self.grid = []; self.revealed = []; self.flagged = []; self.first_click = True; self.game_active = False; self.buttons = []; self.cell_size = 30; super().__init__(parent, hub)
    
    def setup_ui(self):
        colors = self.theme.colors; diff_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); diff_frame.pack(pady=(10, 5)); self.diff_var = tk.StringVar(value="easy")
        for val, text in (("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")):
            rb = tk.Radiobutton(diff_frame, **{"text": text, "variable": self.diff_var, "value": val, "font": self.theme.get_font("body_bold"), "fg": colors["text"], "bg": colors["bg_dark"], "selectcolor": colors["bg_surface"], "activebackground": colors["bg_dark"], "activeforeground": colors["primary"], "command": self._on_difficulty_change, "indicatoron": 0, "padx": 16, "pady": 6, "relief": tk.FLAT, "bd": 0})
            rb.pack(side=tk.LEFT, padx=4)
        self
        info_frame = tk.Frame(self.content_frame, bg=colors["bg_surface"], height=40); info_frame.pack(fill=tk.X, padx=20, pady=5); info_frame.pack_propagate(False); info_inner = tk.Frame(info_frame, bg=colors["bg_surface"]); info_inner.pack(expand=True)
        
        self.mines_label = tk.Label(info_inner, text="💣 10", font=self.theme.get_font("body_bold"), fg=colors["error"], bg=colors["bg_surface"]); self.mines_label.pack(side=tk.LEFT, padx=20)
        
        self.status_label = tk.Label(info_inner, text="Click to start", font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_surface"]); self.status_label.pack(side=tk.LEFT, padx=20)
        
        new_btn = tk.Label(info_inner, text="🔄 New", font=self.theme.get_font("button"), fg=colors["primary"], bg=colors["bg_surface"], cursor="hand2", padx=10); new_btn.pack(side=tk.RIGHT, padx=10)
        
        new_btn.bind("<Button-1>", (lambda e: self.start_game()))
        
        self.grid_outer = tk.Frame(self.content_frame, bg=colors["bg_dark"]); self.grid_outer.pack(expand=True)
        
        self.grid_frame = tk.Frame(self.grid_outer, bg=colors["border"], padx=2, pady=2); self.grid_frame.pack()
    
    def start_game(self):
        self._is_running = True; self._is_paused = False; self.difficulty = self.diff_var.get(); d = self.DIFFICULTIES[self.difficulty]; self.rows = d["rows"]; self.cols = d["cols"]; self.num_mines = d["mines"]; self.COIN_REWARD_WIN = d["reward"]; self.grid = [[0] * (self.cols) for _ in range(self.rows)]
        
        self.revealed = [[False] * (self.cols) for _ in range(self.rows)]; self.flagged = [[False] * (self.cols) for _ in range(self.rows)]; self.first_click = True; self.game_active = True
        
        self.mines_label.configure(text=f"💣 {self.num_mines}")
        
        colors = self.theme.colors; self.status_label.configure(text="Click to start", fg=colors["text"]); self._build_grid(); _ = None; _ = None; _ = None
    
    def _on_difficulty_change(self):
        self.start_game()
    
    def cleanup(self):
        self.game_active = False; super().cleanup()
    
    def _build_grid(self):
        for widget in self.grid_frame.winfo_children():
            widget.destroy()
        self
        colors = self.theme.colors; self.buttons = []
        if self.difficulty == "hard":
            self.cell_size = 30
        elif self.difficulty == "medium":
            self.cell_size = 38
        
        else:
            self.cell_size = 46
        
        for r in range(self.rows):
            row_buttons = []
            for c in range(self.cols):
                btn = tk.Label(self.grid_frame, width=2, height=1, font=("Consolas", max(9, (self.cell_size) // 3), "bold"), bg=colors["bg_card"], fg=colors["text"], relief=tk.RAISED, bd=1, cursor="hand2")
                btn.grid(row=r, column=c, padx=0, pady=0)
                btn.bind("<Button-1>", (lambda e, row, col: self._on_left_click(row, col)))
                btn.bind("<Button-3>", (lambda e, row, col: self._on_right_click(row, col)))
                row_buttons.append(btn)
            None
            self.buttons.append(row_buttons)
    
    def _place_mines(self, safe_r, safe_c):
        safe_zone = set()
        for dr in range(-1, 2):
            for dc in range(-1, 2):
                nc = safe_c + dc
                nr = safe_r + dr
                safe_zone.add((nr, nc))
        for r in range(self.rows):
            for c in range(self.cols):
                if not (r, c) not in safe_zone:
                    pass
            None
        
        []
        candidates = r; r = c; c = None
        
        mine_positions = random.sample(candidates, min(self.num_mines, len(candidates)))
        for r, c in mine_positions:
            self.grid[r][c] = -1
        for r in range(self.rows):
            for c in range(self.cols):
                count = 0
                for dr in range(-1, 2):
                    for dc in range(-1, 2):
                        if dr == 0 and dc == 0:
                            continue
                        nr = r + dr
                        nc = c + dc
                        if 0 <= nr < self.rows and 0 <= nc < self.cols:
                            if self.grid[nr][nc] == -1:
                                count += 1
                self.grid[r][c] = count
    
    def _on_left_click(self, row, col):
        if not self.game_active:
            pass
        if self.revealed[row][col] or self.flagged[row][col]:
            pass
        if self.first_click:
            self.first_click = False
            self._place_mines(row, col)
            self._start_time = __import__("time").time()
        self._start_timer()
        if self.grid[row][col] == -1:
            self._game_over(row, col)
        
        self._reveal(row, col); self.sounds.play("click")
        if self._check_win():
            self._handle_win()
    
    def _on_right_click(self, row, col):
        if self.game_active and self.revealed[row][col]:
            pass; colors = self.theme.colors
        self.flagged[row][col] = not self.flagged[row][col]
        
        btn = self.buttons[row][col]
        
        flags = sum((self.flagged[r][c] for c in range(self.rows))); remaining = (self.num_mines) - flags
        
        self.mines_label.configure(text=f"💣 {remaining}")
    
    def _reveal(self, row, col):
        if row < 0 and row >= self.rows and col < 0 or col >= self.cols:
            pass
        if self.revealed[row][col] or self.flagged[row][col]:
            pass
        self.revealed[row][col] = True
        
        self._update_cell_display(row, col)
        while self.grid[row][col] == 0:
            for dr in range(-1, 2):
                for dc in range(-1, 2):
                    if dr == 0 and dc == 0:
                        pass
                    self._reveal(row + dr, col + dc)
                None
            return None
    
    def _update_cell_display(self, row, col):
        colors = self.theme.colors; btn = self.buttons[row][col]; val = self.grid[row][col]; num_colors = {1: "#4fc3f7", 2: "#69f0ae", 3: "#ff8a80", 4: "#7c4dff", 5: "#ff6e40", 6: "#26c6da", 7: "#ec407a", 8: "#78909c"}
        if val == 0:
            btn.configure(text="", bg=colors["bg_surface"], relief=tk.FLAT, bd=0)
        if val > 0:
            btn.configure(text=str(val), fg=num_colors.get(val, colors["text"]), bg=colors["bg_surface"], relief=tk.FLAT, bd=0)
    
    def _check_win(self):
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c] != -1:
                    pass
                elif self.revealed[r][c]:
                    pass
                None
                None
                return False
        return True
    
    def _handle_win(self):
        self.game_active = False; colors = self.theme.colors; self.status_label.configure(text="🎉 You Win!", fg=colors["success"]); self.achievements.check_and_unlock("mines_first", 1)
        if self.difficulty == "hard":
            pass
        self.achievements.check_and_unlock("mines_hard", 1); self.on_win(bonus_coins=self.DIFFICULTIES[self.difficulty]["reward"] - 25, achievement_id="mines_first")
    
    def _game_over(self, mine_r, mine_c):
        self.game_active = False; colors = self.theme.colors; self.status_label.configure(text="💥 Game Over!", fg=colors["error"])
        for r in range(self.rows):
            for c in range(self.cols):
                if not self.grid[r][c] == -1:
                    pass
                btn = self.buttons[r][c]
                if r == mine_r and c == mine_c:
                    btn.configure(text="💥", bg=colors["error"], relief=tk.FLAT)
                btn.configure(text="💣", bg=colors["bg_hover"], relief=tk.FLAT)
            None
        self.on_lose()
