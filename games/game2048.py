"""
NeoPlato — 2048
================
Tile sliding puzzle game with smooth animations, mouse drag support,
and score tracking. Reach the 2048 tile to win!
"""
import tkinter as tk, random
from games.base_game import BaseGame
from core.animations import ParticleSystem

class Game2048(BaseGame):
    """2048 tile game with smooth animations."""
    GAME_ID = "2048"
    GAME_TITLE = "2048"
    GAME_ICON = "🔢"
    GAME_DESCRIPTION = "Slide tiles to reach 2048"
    GAME_RULES = "Use the arrow keys (or drag with mouse) to slide tiles.\n\nWhen two tiles with the same number touch, they merge into one with double the value.\n\nReach the 2048 tile to win!"
    SUPPORTS_MULTIPLAYER = False
    COIN_REWARD_WIN = 75
    GRID_SIZE = 4
    CELL_PAD = 8
    CELL_SIZE = 100
    TILE_COLORS = {
        0: ("#1a1a2e", "#555577"),
        2: ("#2d3a5c", "#e8e8f0"),
        4: ("#2d4a5c", "#e8e8f0"),
        8: ("#c47832", "#ffffff"),
        16: ("#d4602a", "#ffffff"),
        32: ("#d44a2a", "#ffffff"),
        64: ("#d42a2a", "#ffffff"),
        128: ("#e6c840", "#ffffff"),
        256: ("#e6c020", "#ffffff"),
        512: ("#e6b800", "#ffffff"),
        1024: ("#e6a800", "#ffffff"),
        2048: ("#e69800", "#ffffff"),
        4096: ("#60d060", "#ffffff"),
        8192: ("#40c0c0", "#ffffff"),
    }

    def __init__(self, parent, hub):
        self.grid_data = [[0] * 4 for _ in range(4)]
        self.game_active = False
        self._max_tile = 0
        self._drag_start = None
        self._anim_id = None
        super().__init__(parent, hub)

    def setup_ui(self):
        colors = self.theme.colors
        info_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        info_frame.pack(pady=(10, 5))
        hs = self.storage.get_high_score(self.GAME_ID)

        self.hs_label = tk.Label(info_frame, text=f"Best: {hs}",
                                 font=self.theme.get_font("body_bold"),
                                 fg=colors["gold"], bg=colors["bg_dark"])
        self.hs_label.pack(side=tk.LEFT, padx=20)

        self.max_tile_label = tk.Label(info_frame, text="Max Tile: 0",
                                       font=self.theme.get_font("body"),
                                       fg=colors["text_secondary"],
                                       bg=colors["bg_dark"])
        self.max_tile_label.pack(side=tk.LEFT, padx=20)

        total = self.GRID_SIZE * self.CELL_SIZE + (self.GRID_SIZE + 1) * self.CELL_PAD

        canvas_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        canvas_frame.pack(expand=True)

        self.canvas = tk.Canvas(canvas_frame, width=total, height=total,
                                bg=colors["bg_surface"], highlightthickness=0)
        self.canvas.pack(padx=20, pady=10)

        self.particles = ParticleSystem(self.canvas)
        self.bind_all("<Key>", self._on_key)
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)

        hint = tk.Label(self.content_frame,
                        text="Arrow keys or drag to slide tiles",
                        font=self.theme.get_font("caption"),
                        fg=colors["text_muted"], bg=colors["bg_dark"])
        hint.pack(pady=5)

        new_btn = tk.Label(self.content_frame, text="🔄 New Game",
                           font=self.theme.get_font("button"),
                           fg=colors["primary"], bg=colors["bg_card"],
                           padx=20, pady=8, cursor="hand2")
        new_btn.pack(pady=5)
        new_btn.bind("<Button-1>", lambda e: self.start_game())

    def start_game(self):
        self.grid_data = [[0] * 4 for _ in range(4)]
        self.game_active = True
        self._max_tile = 0
        self.score = 0
        self._is_running = True
        self._spawn_tile()
        self._spawn_tile()
        self._draw()

    def cleanup(self):
        self.game_active = False
        if self._anim_id:
            self.after_cancel(self._anim_id)
        try:
            self.unbind_all("<Key>")
            super().cleanup()
        except Exception:
            pass

    def _draw(self):
        self.canvas.delete("tiles")
        colors = self.theme.colors
        pad = self.CELL_PAD
        cs = self.CELL_SIZE
        for r in range(4):
            for c in range(4):
                x = pad + c * (cs + pad)
                y = pad + r * (cs + pad)
                val = self.grid_data[r][c]
                bg, fg = self.TILE_COLORS.get(val, ("#333355", "#ffffff"))
                self.canvas.create_rectangle(x, y, x + cs, y + cs,
                                             fill=bg, outline="", tags="tiles")
                if val > 0:
                    digits = len(str(val))
                    font_size = max(14, 32 - digits * 4)
                    self.canvas.create_text(x + cs // 2, y + cs // 2,
                                            text=str(val),
                                            font=("Segoe UI", font_size, "bold"),
                                            fill=fg, tags="tiles")
        self.max_tile_label.configure(text=f"Max Tile: {self._max_tile}")

    def _spawn_tile(self):
        empty = []
        for r in range(4):
            for c in range(4):
                if self.grid_data[r][c] == 0:
                    empty.append((r, c))
        if empty:
            r, c = random.choice(empty)
            self.grid_data[r][c] = 4 if random.random() < 0.1 else 2

    def _slide_row_left(self, row):
        tiles = [x for x in row if x != 0]
        merged = []
        score_add = 0
        skip = False
        for i in range(len(tiles)):
            if skip:
                skip = False
                continue
            if i + 1 < len(tiles) and tiles[i] == tiles[i + 1]:
                merged_val = tiles[i] * 2
                merged.append(merged_val)
                score_add += merged_val
                skip = True
            else:
                merged.append(tiles[i])
        while len(merged) < 4:
            merged.append(0)
        return (merged, score_add)

    def _move(self, direction):
        if not self.game_active:
            return False
        old_grid = [row[:] for row in self.grid_data]
        total_score = 0
        if direction == "left":
            for r in range(4):
                self.grid_data[r], added = self._slide_row_left(self.grid_data[r])
                total_score += added
        elif direction == "right":
            for r in range(4):
                rev = self.grid_data[r][::-1]
                slid, added = self._slide_row_left(rev)
                self.grid_data[r] = slid[::-1]
                total_score += added
        elif direction == "up":
            for c in range(4):
                col = [self.grid_data[r][c] for r in range(4)]
                slid, added = self._slide_row_left(col)
                for r in range(4):
                    self.grid_data[r][c] = slid[r]
                total_score += added
        elif direction == "down":
            for c in range(4):
                col = [self.grid_data[r][c] for r in range(4)][::-1]
                slid, added = self._slide_row_left(col)
                slid = slid[::-1]
                for r in range(4):
                    self.grid_data[r][c] = slid[r]
                total_score += added
        changed = self.grid_data != old_grid
        if changed:
            self.score += total_score
            self._update_score_display()
            for r in range(4):
                for c in range(4):
                    self._max_tile = max(self._max_tile, self.grid_data[r][c])
            self._spawn_tile()
            self._draw()
            self.sounds.play("move")
            if self._max_tile >= 2048:
                self._handle_win()
            elif not self._can_move():
                self._handle_game_over()
        return changed

    def _can_move(self):
        for r in range(4):
            for c in range(4):
                if self.grid_data[r][c] == 0:
                    return True
                if c + 1 < 4 and self.grid_data[r][c] == self.grid_data[r][c + 1]:
                    return True
                if r + 1 < 4 and self.grid_data[r][c] == self.grid_data[r + 1][c]:
                    return True
        return False

    def _handle_win(self):
        colors = self.theme.colors
        total = self.GRID_SIZE * self.CELL_SIZE + (self.GRID_SIZE + 1) * self.CELL_PAD
        self.canvas.create_rectangle(0, 0, total, total,
                                     fill=colors["bg_darkest"], stipple="gray50",
                                     tags="win_overlay")
        self.canvas.create_text(total // 2, total // 2 - 20,
                                text="🎉 2048!", font=("Segoe UI", 36, "bold"),
                                fill=colors["gold"], tags="win_overlay")
        self.canvas.create_text(total // 2, total // 2 + 25,
                                text="Click to continue playing",
                                font=("Segoe UI", 12),
                                fill=colors["text"], tags="win_overlay")
        self.particles.emit_confetti(total // 2, total // 2, count=50)
        self._animate_particles()
        self.on_win(0, "2048_reach")
        self.canvas.bind("<Button-1>", lambda e: self._dismiss_win())

    def _dismiss_win(self):
        self.canvas.delete("win_overlay")
        self.game_active = True
        self._is_running = True
        self.canvas.bind("<ButtonPress-1>", self._on_drag_start)
        self.canvas.bind("<ButtonRelease-1>", self._on_drag_end)

    def _handle_game_over(self):
        self.game_active = False
        colors = self.theme.colors
        total = self.GRID_SIZE * self.CELL_SIZE + (self.GRID_SIZE + 1) * self.CELL_PAD
        self.canvas.create_rectangle(0, 0, total, total,
                                     fill=colors["bg_darkest"], stipple="gray50",
                                     tags="overlay")
        self.canvas.create_text(total // 2, total // 2 - 10,
                                text="Game Over!", font=("Segoe UI", 28, "bold"),
                                fill=colors["error"], tags="overlay")
        self.canvas.create_text(total // 2, total // 2 + 25,
                                text=f"Score: {self.score}",
                                font=("Segoe UI", 16),
                                fill=colors["text"], tags="overlay")
        self.on_lose("")
        hs = self.storage.get_high_score(self.GAME_ID)
        self.hs_label.configure(text=f"Best: {hs}")

    def _animate_particles(self):
        if self.particles.is_active:
            self.particles.update()
            self._anim_id = self.after(33, self._animate_particles)

    def _on_key(self, event):
        key_map = {
            "Up": "up", "Down": "down", "Left": "left", "Right": "right",
            "w": "up", "s": "down", "a": "left", "d": "right",
            "W": "up", "S": "down", "A": "left", "D": "right",
        }
        direction = key_map.get(event.keysym)
        if direction:
            self._move(direction)

    def _on_drag_start(self, event):
        self._drag_start = (event.x, event.y)

    def _on_drag_end(self, event):
        if not self._drag_start:
            return
        dx = event.x - self._drag_start[0]
        dy = event.y - self._drag_start[1]
        self._drag_start = None
        min_dist = 30
        if abs(dx) < min_dist and abs(dy) < min_dist:
            return
        if abs(dx) > abs(dy):
            self._move("right" if dx > 0 else "left")
        else:
            self._move("down" if dy > 0 else "up")
