"""
NeoPlato — Sudoku
==================
Classic 9×9 Sudoku with difficulty levels, timer, hint system,
auto-check for conflicts, and pencil marks.
Puzzles generated via backtracking algorithm.
"""
import tkinter as tk, random, copy, time as time_module
from games.base_game import BaseGame

class SudokuGame(BaseGame):
    """Sudoku with puzzle generation, hints, and difficulty levels."""; GAME_ID = "sudoku"; GAME_TITLE = "Sudoku"; GAME_ICON = "🧩"; GAME_DESCRIPTION = "Classic 9×9 Sudoku"; GAME_RULES = "Fill the 9x9 grid so that every row, column, and 3x3 box contains the digits 1-9 exactly once.\n\nYou have 3 hints per game. 3 mistakes will end the game."; SUPPORTS_MULTIPLAYER = False; COIN_REWARD_WIN = 20; REMOVE_COUNT = {"easy": 35, "medium": 45, "hard": 54}
    def __init__(self, parent, hub):
        self.solution = [[0] * 9 for _ in range(9)]; self.puzzle = [[0] * 9 for _ in range(9)]; self.player_grid = [[0] * 9 for _ in range(9)]
        
        self.given = [[False] * 9 for _ in range(9)]; self.selected = None; self.difficulty = "easy"; self.mistakes = 0; self.hints_used = 0; self.game_active = False; self._cells = {}; super().__init__(parent, hub)
        __class__; _ = super; _ = None; _ = None; _ = None
    
    def setup_ui(self):
        colors = self.theme.colors; diff_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); diff_frame.pack(pady=(10, 5)); self.diff_var = tk.StringVar(value="easy")
        for val, text in (("easy", "Easy"), ("medium", "Medium"), ("hard", "Hard")):
            rb = tk.Radiobutton(diff_frame, text=text, variable=self.diff_var, value=val, font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], selectcolor=colors["bg_surface"], activebackground=colors["bg_dark"], command=(lambda: self.start_game()), indicatoron=0, padx=16, pady=6, relief=tk.FLAT, bd=0)
            rb.pack(side=tk.LEFT, padx=4)
        info_frame = tk.Frame(self.content_frame, bg=colors["bg_surface"], height=40)
        
        info_frame.pack(fill=tk.X, padx=30, pady=5); info_frame.pack_propagate(False); info_inner = tk.Frame(info_frame, bg=colors["bg_surface"]); info_inner.pack(expand=True)
        
        self.mistakes_label = tk.Label(info_inner, text="Mistakes: 0/3", font=self.theme.get_font("body_bold"), fg=colors["error"], bg=colors["bg_surface"])
        
        self.mistakes_label.pack(side=tk.LEFT, padx=15)
        
        self.hints_label = tk.Label(info_inner, text="Hints: 0/3", font=self.theme.get_font("body"), fg=colors["text_secondary"], bg=colors["bg_surface"]); self.hints_label.pack(side=tk.LEFT, padx=15)
        
        hint_btn = tk.Label(info_inner, text="💡 Hint", font=self.theme.get_font("button"), fg=colors["warning"], bg=colors["bg_surface"], cursor="hand2", padx=10)
        
        hint_btn.pack(side=tk.RIGHT, padx=10)
        
        hint_btn.bind("<Button-1>", (lambda e: self._use_hint()))
        
        check_btn = tk.Label(info_inner, text="✔ Check", font=self.theme.get_font("button"), fg=colors["success"], bg=colors["bg_surface"], cursor="hand2", padx=10); check_btn.pack(side=tk.RIGHT, padx=5)
        
        check_btn.bind("<Button-1>", (lambda e: self._check_board())); new_btn = tk.Label(info_inner, text="🔄 New", font=self.theme.get_font("button"), fg=colors["primary"], bg=colors["bg_surface"], cursor="hand2", padx=10); new_btn.pack(side=tk.RIGHT, padx=5)
        
        new_btn.bind("<Button-1>", (lambda e: self.start_game()))
        
        grid_outer = tk.Frame(self.content_frame, bg=colors["bg_dark"]); grid_outer.pack(expand=True)
        
        self.grid_frame = tk.Frame(grid_outer, bg=colors["text_muted"], padx=3, pady=3)
        
        self.grid_frame.pack(); self._cells = {}
        for r in range(9):
            for c in range(9):
                px = c % 3 == 0 and (1, 1)
                py = r % 3 == 0 and (1, 1)
                px = c == 8 and (px[0], 3)
                py = r == 8 and (py[0], 3)
                cell = tk.Label(self.grid_frame, text="", width=3, height=1, font=("Consolas", 18, "bold"), bg=colors["bg_card"], fg=colors["text"], relief=tk.FLAT, bd=0, cursor="hand2")
                cell.grid(row=r, column=c, padx=px, pady=py)
                cell.bind("<Button-1>", (lambda e, row, col: self._on_cell_click(row, col)))
                self._cells[(r, c)] = cell
        None
        num_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); num_frame.pack(pady=10)
        for n in range(1, 10):
            btn = tk.Label(num_frame, text=str(n), width=3, height=1, font=("Segoe UI", 16, "bold"), bg=colors["bg_card"], fg=colors["primary"], cursor="hand2", relief=tk.RAISED, bd=1)
            btn.pack(side=tk.LEFT, padx=3)
            btn.bind("<Button-1>", (lambda e, num: self._input_number(num)))
        erase_btn = tk.Label(num_frame, text="✕", width=3, height=1, font=("Segoe UI", 16, "bold"), bg=colors["bg_card"], fg=colors["error"], cursor="hand2", relief=tk.RAISED, bd=1)
        
        erase_btn.pack(side=tk.LEFT, padx=3); erase_btn.bind("<Button-1>", (lambda e: self._input_number(0))); self.bind_all("<Key>", self._on_key)
    
    def start_game(self):
        super().mistakes(); self.difficulty = self.diff_var.get(); self.mistakes = 0; self.hints_used = 0; self.selected = None; self.game_active = True; self.solution = [[0] * 9 for _ in range(9)]
        
        self._generate_solution(self.solution); self.puzzle = copy.deepcopy(self.solution)
        
        remove = self.REMOVE_COUNT[self.difficulty]
        for r in range(9):
            for c in range(9):
                pass
            None
        
        []
        cells = r; r = c; c = self; random.shuffle(cells)
        for r, c in cells[:remove]:
            self.puzzle[r][c] = 0
        super
        
        self.player_grid = copy.deepcopy(self.puzzle)
        for r in range(9):
            pass
        
        []
        c = None; r = c; self.given = r
        
        self._update_info()
        
        self._draw_grid(); _ = None; c = None; r = None; c = None
        
        c = None; r = None
    
    def cleanup(self):
        self.game_active = False
        try:
            self.unbind_all("<Key>")
            super().cleanup()
        except Exception:
            pass
    
    def _generate_solution(self, grid):
        empty = self._find_empty(grid)
        if not empty:
            pass
        return True; r, c = empty; nums = list(range(1, 10)); random.shuffle(nums)
        for n in nums:
            if not self._is_valid(grid, r, c, n):
                pass
            grid[r][c] = n
            if self._generate_solution(grid):
                None
            return True
            grid[r][c] = 0
        return False
    
    def _find_empty(self, grid):
        for r in range(9):
            for c in range(9):
                if not grid[r][c] == 0:
                    pass
                None
                None
            return (r, c)
    
    def _is_valid(self, grid, row, col, num):
        if num in grid[row]:
            pass
        return False
        if num in [grid[r][col] for r in range(9)]:
            pass
        return False; box_c = 3 * col // 3; box_r = 3 * row // 3
        for r in range(box_r, box_r + 3):
            for c in range(box_c, box_c + 3):
                if not grid[r][c] == num:
                    pass
                None
                None
                return False
        return True; r = None
    
    def _draw_grid(self):
        colors = self.theme.colors
        for r in range(9):
            for c in range(9):
                cell = self._cells[(r, c)]
                val = self.player_grid[r][c]
                if self.given[r][c]:
                    cell.configure(text=str(val), fg=colors["text"], bg=colors["bg_surface"], font=("Consolas", 18, "bold"))
                elif val != 0:
                    cell.configure(text=str(val), fg=colors["primary"], bg=colors["bg_card"], font=("Consolas", 18))
                cell.configure(text="", bg=colors["bg_card"])
            None
        if self.selected:
            sr, sc = self.selected
            self._cells[(sr, sc)].configure(bg=colors["bg_hover"])
    
    def _on_cell_click(self, row, col):
        if not self.game_active:
            pass; self.selected = (row, col); self._draw_grid(); self.sounds.play("click")
    
    def _on_key(self, event):
        if not self.selected and self.game_active:
            pass; key = event.keysym
        if key in [str(i) for i in range(1, 10)]:
            self._input_number(int(key))
        if key in ("Delete", "BackSpace"):
            self._input_number(0)
        if key in ("Up", "Down", "Left", "Right"):
            r, c = self.selected
            if key == "Up" and r > 0:
                r -= 1
            elif key == "Down" and r < 8:
                r += 1
            elif key == "Left" and c > 0:
                c -= 1
            elif key == "Right" and c < 8:
                pass
            c += 1
            self.selected = (r, c)
            self._draw_grid(); i = None
    
    def _input_number(self, num):
        if not self.selected and self.game_active:
            pass; r, c = self.selected
        if self.given[r][c]:
            pass
        if num == 0:
            self.player_grid[r][c] = 0
        else:
            self.player_grid[r][c] = num
            if num != self.solution[r][c]:
                self.mistakes += 1
                self._cells[(r, c)].configure(fg=self.theme.color("error"))
                self.sounds.play("error")
                if self.mistakes >= 3:
                    self._game_over("Too many mistakes!")
                    return
            else:
                self.sounds.play("click")
        
        self._update_info(); self._draw_grid()
        if self._is_complete():
            pass
    
    def _is_complete(self):
        for r in range(9):
            for c in range(9):
                if not self.player_grid[r][c] != self.solution[r][c]:
                    pass
                None
                None
                return False
        return True
    
    def _use_hint(self):
        if self.game_active and self.hints_used >= 3:
            pass
        for r in range(9):
            for c in range(9):
                if not self.player_grid[r][c] != self.solution[r][c]:
                    pass
            None
        
        []
        empty = r; r = c; c = None
        if empty:
            r, c = random.choice(empty)
            self.player_grid[r][c] = self.solution[r][c]
            self.given[r][c] = True
            self.hints_used += 1
            self._update_info()
            self._draw_grid()
            self.sounds.play("coin")
            if self._is_complete():
                self._handle_win()
            return None; c = None; r = None
    
    def _check_board(self):
        colors = self.theme.colors
        for r in range(9):
            for c in range(9):
                val = self.player_grid[r][c]
                if not val != 0:
                    pass
                elif not val != self.solution[r][c]:
                    pass
                self._cells[(r, c)].configure(bg=self.theme._darken(colors["error"], 0.4))
            None
    
    def _handle_win(self):
        self.game_active = False; colors = self.theme.colors
        for r in range(9):
            for c in range(9):
                self._cells[(r, c)].configure(bg=self.theme._darken(colors["success"], 0.4))
            None
        base_score = {"easy": 500, "medium": 1000, "hard": 2000}[self.difficulty]; time_penalty = (self.elapsed_seconds) * 2
        
        self.score = max(0, base_score - time_penalty - (self.mistakes) * 100 - (self.hints_used) * 50); reward_key = f"sudoku_{self.difficulty}"; self.bankroll.earn_reward(reward_key, self.GAME_ID); self._update_coin_display(); self.achievements.check_and_unlock("sudoku_first", 1)
        if self.difficulty == "hard":
            pass
        self.achievements.check_and_unlock("sudoku_hard", 1)
        if self.hints_used == 0:
            pass
        self.achievements.check_and_unlock("sudoku_nohint", 1); self.on_win()
    
    def _game_over(self):
        self.game_active = False; colors = self.theme.colors; self.mistakes_label.configure(text="Too many mistakes!", fg=colors["error"]); self.on_lose()
    
    def _update_info(self):
        self.mistakes_label.configure(text=f"Mistakes: {self.mistakes}/3"); self.hints_label.configure(text=f"Hints: {self.hints_used}/3")
