"""
NeoMatchup - Main Entry Point
==============================
This script loads the game hub from compiled bytecode modules and applies
runtime patches for bug fixes and new features.

The original .py source files were lost due to a file corruption event.
The .pyc (Python Compiled) bytecode files in each directory ARE the original
working game code. This main.py loads them and applies monkey-patches for
all new features and fixes.
"""

import tkinter as tk
import sys
import os
import types
import marshal
import importlib
import importlib.util

# ============================================================================
# STEP 1: Force Python to use .pyc files instead of broken .py stubs
# ============================================================================
# The .py files alongside the .pyc files are imperfect decompilation attempts.
# We need to load the .pyc files directly since they contain the original code.

def load_pyc_module(name, pyc_path):
    """Load a module directly from a .pyc file, bypassing any .py file."""
    with open(pyc_path, 'rb') as f:
        f.read(16)  # Skip pyc header (16 bytes for Python 3.13)
        code = marshal.load(f)
    
    mod = types.ModuleType(name)
    mod.__file__ = pyc_path
    mod.__loader__ = None
    mod.__spec__ = None
    
    # For packages, set __path__ so sub-imports work
    parent_dir = os.path.dirname(pyc_path)
    if os.path.basename(pyc_path).startswith('__init__'):
        mod.__path__ = [parent_dir]
        mod.__package__ = name
    else:
        mod.__package__ = name.rsplit('.', 1)[0] if '.' in name else ''
    
    return mod, code


def preload_all_pyc_modules():
    """Pre-register all .pyc modules in sys.modules BEFORE any imports happen."""
    base = os.path.dirname(os.path.abspath(__file__))
    
    # Define all modules and their .pyc paths
    modules = {
        # Core package
        'core': os.path.join(base, 'core', '__init__.pyc'),
        'core.storage': os.path.join(base, 'core', 'storage.pyc'),
        'core.theme': os.path.join(base, 'core', 'theme.pyc'),
        'core.achievements': os.path.join(base, 'core', 'achievements.pyc'),
        'core.bankroll': os.path.join(base, 'core', 'bankroll.pyc'),
        'core.animations': os.path.join(base, 'core', 'animations.pyc'),
        'core.sounds': os.path.join(base, 'core', 'sounds.pyc'),
        
        # Games package
        'games': os.path.join(base, 'games', '__init__.pyc'),
        'games.base_game': os.path.join(base, 'games', 'base_game.pyc'),
        'games.chess': os.path.join(base, 'games', 'chess.pyc'),
        'games.connect_four': os.path.join(base, 'games', 'connect_four.pyc'),
        'games.game2048': os.path.join(base, 'games', 'game2048.pyc'),
        'games.memory_match': os.path.join(base, 'games', 'memory_match.pyc'),
        'games.minesweeper': os.path.join(base, 'games', 'minesweeper.pyc'),
        'games.roulette': os.path.join(base, 'games', 'roulette.pyc'),
        'games.snake': os.path.join(base, 'games', 'snake.pyc'),
        'games.sudoku': os.path.join(base, 'games', 'sudoku.pyc'),
        'games.tictactoe': os.path.join(base, 'games', 'tictactoe.pyc'),
        'games.wordle': os.path.join(base, 'games', 'wordle.pyc'),
        
        # Pages package
        'pages': os.path.join(base, 'pages', '__init__.pyc'),
        'pages.profile': os.path.join(base, 'pages', 'profile.pyc'),
        'pages.settings': os.path.join(base, 'pages', 'settings.pyc'),
        'pages.achievements_page': os.path.join(base, 'pages', 'achievements_page.pyc'),
        'pages.bank_shop': os.path.join(base, 'pages', 'bank_shop.pyc'),
        
        # Multiplayer package
        'multiplayer': os.path.join(base, 'multiplayer', '__init__.pyc'),
        'multiplayer.client': os.path.join(base, 'multiplayer', 'client.pyc'),
        'multiplayer.server': os.path.join(base, 'multiplayer', 'server.pyc'),
        'multiplayer.utils': os.path.join(base, 'multiplayer', 'utils.pyc'),
    }
    
    # First pass: create all module objects and register them in sys.modules
    # This must happen before execution so cross-imports resolve correctly
    pending = []
    for name, pyc_path in modules.items():
        if not os.path.exists(pyc_path):
            print(f"[WARN] Missing .pyc: {pyc_path}")
            continue
        try:
            mod, code = load_pyc_module(name, pyc_path)
            sys.modules[name] = mod
            pending.append((name, mod, code))
        except Exception as e:
            print(f"[ERR] Failed to load {name}: {e}")
    
    # Second pass: execute code objects in DEPENDENCY ORDER
    # core/* and multiplayer/* must be exec'd before games/* and pages/*
    def exec_priority(name):
        # Packages (__init__) first within each group
        is_init = name.count('.') == 0
        if name.startswith('core'):
            return (0, 0 if is_init else 1, name)
        elif name.startswith('multiplayer'):
            return (1, 0 if is_init else 1, name)
        elif name.startswith('games'):
            # base_game before other games
            if 'base_game' in name:
                return (2, 0 if is_init else 1, name)
            return (2, 2, name)
        elif name.startswith('pages'):
            return (3, 0 if is_init else 1, name)
        return (4, 0, name)
    
    pending.sort(key=lambda x: exec_priority(x[0]))
    
    for name, mod, code in pending:
        try:
            exec(code, mod.__dict__)
        except Exception as e:
            print(f"[ERR] Failed to exec {name}: {e}")
            
    # Explicitly link submodules to parent modules (e.g. set 'snake' on 'games' module)
    for name in modules:
        if '.' in name:
            parent_name, child_name = name.rsplit('.', 1)
            if parent_name in sys.modules:
                setattr(sys.modules[parent_name], child_name, sys.modules[name])
    
    return modules


# Load the hub module separately since it's at the root level
def load_hub():
    """Load the main GameHub from hub.pyc."""
    base = os.path.dirname(os.path.abspath(__file__))
    pyc_path = os.path.join(base, 'hub.pyc')
    
    mod, code = load_pyc_module('hub', pyc_path)
    sys.modules['hub'] = mod
    exec(code, mod.__dict__)
    return mod


# ============================================================================
# STEP 2: Execute the loading
# ============================================================================
print("[NeoMatchup] Loading game modules from .pyc bytecode...")

# Preload all sub-modules first (so hub's imports resolve)
preload_all_pyc_modules()

# Now load hub (which imports from core, games, pages, multiplayer)
hub_module = load_hub()

# Verify
if hasattr(hub_module, 'GameHub'):
    print("[NeoMatchup] GameHub loaded successfully!")
else:
    print("[FATAL] GameHub not found in hub.pyc!")
    sys.exit(1)

# Re-import for convenience
import hub
import games.snake
import games.base_game
import pages.profile


# ============================================================================
# STEP 3: Apply patches
# ============================================================================

# --- Patch 1: NeoMatchup Rename ---
original_title = tk.Tk.title
def patched_title(self, string=None):
    if string:
        string = string.replace("NeoPlato", "NeoMatchup")
    return original_title(self, string)
tk.Tk.title = patched_title

# Patch _draw_logo to say NeoMatchup
try:
    original_draw_logo = hub.GameHub._draw_logo
    def patched_draw_logo(self):
        original_draw_logo(self)
        c = self.logo_canvas
        colors = self.theme.colors
        c.delete("all")
        c.update_idletasks()
        
        cx, cy = 35, 40
        for i in range(3):
            r = 18 - i * 3
            alpha_color = self.theme.interpolate_color(
                colors["primary"], colors["sidebar_bg"], 0.3 + i * 0.2
            )
            c.create_oval(cx - r, cy - r, cx + r, cy + r, fill=alpha_color, outline="")

        c.create_text(cx, cy, text="N", font=("Segoe UI", 16, "bold"), fill=colors["bg_darkest"])
        c.create_text(65, 32, text="NeoMatchup", font=("Segoe UI", 13, "bold"), fill=colors["text"], anchor="w")
        c.create_text(65, 52, text="Game Hub", font=("Segoe UI", 10), fill=colors["text_muted"], anchor="w")
        
    hub.GameHub._draw_logo = patched_draw_logo
except (AttributeError, TypeError) as e:
    print(f"[WARNING] Could not patch _draw_logo: {e}")


# --- Patch 2: Sidebar Scrollable ---
try:
    original_build_sidebar = hub.GameHub._build_sidebar
    def patched_build_sidebar(self):
        colors = self.theme.colors
        
        # Create a canvas and scrollbar inside self.sidebar
        self.sidebar_canvas = tk.Canvas(self.sidebar, bg=colors["sidebar_bg"], highlightthickness=0, width=210)
        self.sidebar_scrollbar = tk.Scrollbar(self.sidebar, orient="vertical", command=self.sidebar_canvas.yview, width=8)
        self.sidebar_canvas.configure(yscrollcommand=self.sidebar_scrollbar.set)
        
        self.sidebar_scrollbar.pack(side="right", fill="y")
        self.sidebar_canvas.pack(side="left", fill="both", expand=True)
        
        # Create an inner frame
        self.sidebar_inner = tk.Frame(self.sidebar_canvas, bg=colors["sidebar_bg"], width=210)
        self.sidebar_window = self.sidebar_canvas.create_window((0, 0), window=self.sidebar_inner, anchor="nw")
        
        def on_configure(event):
            self.sidebar_canvas.configure(scrollregion=self.sidebar_canvas.bbox("all"))
        self.sidebar_inner.bind("<Configure>", on_configure)
        
        def on_mousewheel(event):
            try:
                self.sidebar_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        
        def _bind_mouse(event):
            self.sidebar_canvas.bind_all("<MouseWheel>", on_mousewheel)
        def _unbind_mouse(event):
            self.sidebar_canvas.unbind_all("<MouseWheel>")
        
        self.sidebar_canvas.bind("<Enter>", _bind_mouse)
        self.sidebar_canvas.bind("<Leave>", _unbind_mouse)
        
        # Temporarily swap self.sidebar so original packs into sidebar_inner
        original_sidebar = self.sidebar
        self.sidebar = self.sidebar_inner
        original_build_sidebar(self)
        self.sidebar = original_sidebar

    hub.GameHub._build_sidebar = patched_build_sidebar
except (AttributeError, TypeError) as e:
    print(f"[WARNING] Could not patch _build_sidebar: {e}")


# --- Patch 3: Snake Game - Press Space to Start ---
try:
    original_snake_start = games.snake.SnakeGame.start_game
    def patched_snake_start(self):
        self.game_running = False
        self.direction = 'Right'
        self.next_direction = 'Right'
        mid_r = self.ROWS // 2
        mid_c = self.COLS // 2
        self.snake = [(mid_r, mid_c), (mid_r, mid_c - 1), (mid_r, mid_c - 2)]
        
        self.speed_level = self.speed_var.get()
        if self.speed_level == "slow":
            self.BASE_SPEED = 180
        elif self.speed_level == "fast":
            self.BASE_SPEED = 70
        else:
            self.BASE_SPEED = 120
        self._speed = self.BASE_SPEED
        self._foods_eaten = 0
        self.score = 0
        
        self._place_food()
        self._draw()
        
        colors = self.theme.colors
        canvas_w = self.COLS * self.CELL_SIZE
        canvas_h = self.ROWS * self.CELL_SIZE
        
        self.overlay_text = self.canvas.create_text(
            canvas_w // 2, canvas_h // 2, text="Press Space to Start",
            font=("Segoe UI", 24, "bold"), fill=colors["text"]
        )
    
    def patched_snake_on_key(self, event):
        if event.keysym.lower() == "space":
            if not self.game_running:
                if hasattr(self, 'overlay_text') and self.overlay_text:
                    self.canvas.delete(self.overlay_text)
                    self.overlay_text = None
                self.game_running = True
                self._game_loop()
                return
        if not self.game_running:
            return
        if event.keysym in ['Up', 'w', 'W'] and self.direction != 'Down':
            self.next_direction = 'Up'
        elif event.keysym in ['Down', 's', 'S'] and self.direction != 'Up':
            self.next_direction = 'Down'
        elif event.keysym in ['Left', 'a', 'A'] and self.direction != 'Right':
            self.next_direction = 'Left'
        elif event.keysym in ['Right', 'd', 'D'] and self.direction != 'Left':
            self.next_direction = 'Right'
    
    games.snake.SnakeGame.start_game = patched_snake_start
    games.snake.SnakeGame._on_key = patched_snake_on_key
except (AttributeError, TypeError) as e:
    print(f"[WARNING] Could not patch Snake: {e}")


# --- Patch 4: Profile Page - Scrollable with Charts ---
try:
    original_profile_build = pages.profile.ProfilePage._build_ui
    
    # Avatar map for display
    AVATAR_MAP = {
        "default": "👤", "robot": "🤖", "alien": "👽",
        "ninja": "🥷", "wizard": "🧙", "pirate": "🏴‍☠️",
        "mask": "🎭", "crown": "👑", "dragon": "🐉"
    }
    
    def patched_profile_build(self):
        colors = self.theme.colors
        
        # Clear everything and build scrollable container
        for widget in self.winfo_children():
            widget.destroy()
        
        self.profile_canvas = tk.Canvas(self, bg=colors["bg_dark"], highlightthickness=0)
        self.profile_scrollbar = tk.Scrollbar(self, orient="vertical", command=self.profile_canvas.yview, width=10)
        self.profile_canvas.configure(yscrollcommand=self.profile_scrollbar.set)
        self.profile_scrollbar.pack(side="right", fill="y")
        self.profile_canvas.pack(side="left", fill="both", expand=True)
        
        inner = tk.Frame(self.profile_canvas, bg=colors["bg_dark"])
        self.profile_window = self.profile_canvas.create_window((0, 0), window=inner, anchor="nw")
        
        def on_configure(event):
            self.profile_canvas.configure(scrollregion=self.profile_canvas.bbox("all"))
        inner.bind("<Configure>", on_configure)
        
        def on_canvas_configure(event):
            self.profile_canvas.itemconfig(self.profile_window, width=event.width)
        self.profile_canvas.bind("<Configure>", on_canvas_configure)
        
        def on_profile_mousewheel(event):
            try:
                self.profile_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")
            except tk.TclError:
                pass
        def _p_bind(event):
            self.profile_canvas.bind_all("<MouseWheel>", on_profile_mousewheel)
        def _p_unbind(event):
            self.profile_canvas.unbind_all("<MouseWheel>")
        self.profile_canvas.bind("<Enter>", _p_bind)
        self.profile_canvas.bind("<Leave>", _p_unbind)
        
        # ── Header / Active Avatar ──
        header = tk.Frame(inner, bg=colors["bg_surface"], height=150)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        header_inner = tk.Frame(header, bg=colors["bg_surface"])
        header_inner.pack(expand=True)
        
        active_avatar_id = self.storage.get_setting("active_avatar", "default")
        active_icon = AVATAR_MAP.get(active_avatar_id, "👤")
        
        tk.Label(header_inner, text=active_icon, font=("Segoe UI", 48),
                 fg=colors["text"], bg=colors["bg_surface"]).pack(side=tk.LEFT, padx=20)
        info_frame = tk.Frame(header_inner, bg=colors["bg_surface"])
        info_frame.pack(side=tk.LEFT)
        
        player_name = self.storage.get_setting("player_name", "Player")
        player_id = self.storage.get_player_id()
        
        name_frame = tk.Frame(info_frame, bg=colors["bg_surface"])
        name_frame.pack(anchor="w")
        tk.Label(name_frame, text=f"{player_name} #{player_id}",
                 font=("Segoe UI", 24, "bold"), fg=colors["text"],
                 bg=colors["bg_surface"]).pack(side=tk.LEFT)
        
        edit_btn = tk.Label(name_frame, text="✏️", font=("Segoe UI", 14),
                            fg=colors["text_muted"], bg=colors["bg_surface"], cursor="hand2")
        edit_btn.pack(side=tk.LEFT, padx=10)
        edit_btn.bind("<Button-1>", lambda e: self._edit_name())
        
        tk.Label(info_frame, text=f"Active Avatar: {active_avatar_id.title()}",
                 font=self.theme.get_font("body"), fg=colors["primary"],
                 bg=colors["bg_surface"]).pack(anchor="w")
        
        # ── Lifetime Stats ──
        stats_frame = tk.Frame(inner, bg=colors["bg_dark"])
        stats_frame.pack(fill=tk.BOTH, padx=30, pady=20)
        
        tk.Label(stats_frame, text="📊 Lifetime Stats",
                 font=self.theme.get_font("heading_sm"), fg=colors["text"],
                 bg=colors["bg_dark"]).pack(anchor="w", pady=(0, 10))
        
        sf_inner = tk.Frame(stats_frame, bg=colors["bg_card"], padx=20, pady=20)
        sf_inner.pack(fill=tk.X)
        
        all_stats = self.storage.get_all_game_stats()
        t_played = sum(s.get("games_played", 0) for s in all_stats)
        t_won = sum(s.get("games_won", 0) for s in all_stats)
        wr = (t_won / t_played * 100) if t_played > 0 else 0
        
        def add_stat_row(parent, label, val):
            r = tk.Frame(parent, bg=colors["bg_card"])
            r.pack(fill=tk.X, pady=4)
            tk.Label(r, text=label, font=self.theme.get_font("body"),
                     fg=colors["text_secondary"], bg=colors["bg_card"],
                     width=20, anchor="w").pack(side=tk.LEFT)
            tk.Label(r, text=str(val), font=self.theme.get_font("body_bold"),
                     fg=colors["text"], bg=colors["bg_card"]).pack(side=tk.LEFT)
        
        add_stat_row(sf_inner, "Total Games Played:", t_played)
        add_stat_row(sf_inner, "Total Games Won:", t_won)
        add_stat_row(sf_inner, "Overall Win Rate:", f"{wr:.1f}%")
        add_stat_row(sf_inner, "Current Balance:", f"{self.hub.bankroll.balance} NeoCoins")
        
        # ── Avatar Inventory ──
        inv_frame = tk.Frame(inner, bg=colors["bg_dark"])
        inv_frame.pack(fill=tk.BOTH, padx=30, pady=20)
        tk.Label(inv_frame, text="👤 Avatar Inventory",
                 font=self.theme.get_font("heading_sm"), fg=colors["text"],
                 bg=colors["bg_dark"]).pack(anchor="w", pady=(0, 10))
        
        inv_inner = tk.Frame(inv_frame, bg=colors["bg_dark"])
        inv_inner.pack(fill=tk.X)
        
        raw_purchases = self.storage.get_purchases()
        purchased = [p["item_id"] if isinstance(p, dict) else p for p in raw_purchases]
        
        avatars = [{"id": "default", "name": "Default", "icon": "👤"}]
        for item_id in purchased:
            if item_id in AVATAR_MAP:
                avatars.append({"id": item_id, "name": item_id.title(), "icon": AVATAR_MAP[item_id]})
        
        for av in avatars:
            f = tk.Frame(inv_inner, bg=colors["bg_card"], padx=15, pady=15)
            f.pack(side=tk.LEFT, padx=(0, 15))
            tk.Label(f, text=av["icon"], font=("Segoe UI", 24),
                     fg=colors["text"], bg=colors["bg_card"]).pack()
            tk.Label(f, text=av["name"], font=self.theme.get_font("caption"),
                     fg=colors["text"], bg=colors["bg_card"]).pack(pady=(5, 10))
            
            if av["id"] == active_avatar_id:
                tk.Label(f, text="✅ Equipped", font=self.theme.get_font("caption"),
                         fg=colors["success"], bg=colors["bg_card"]).pack()
            else:
                btn = tk.Button(f, text="Equip", font=self.theme.get_font("caption"),
                                bg=colors["bg_surface"], fg=colors["primary"], relief=tk.FLAT,
                                command=lambda a=av["id"]: self._equip_avatar(a))
                btn.pack()
        
        # ── Charts Section ──
        charts_frame = tk.Frame(inner, bg=colors["bg_dark"])
        charts_frame.pack(fill=tk.BOTH, expand=True, padx=30, pady=10)
        
        tk.Label(charts_frame, text="📈 Player Statistics",
                 font=self.theme.get_font("heading_sm"), fg=colors["text"],
                 bg=colors["bg_dark"]).pack(anchor="w", pady=(0, 10))
        
        canvas = tk.Canvas(charts_frame, height=250, bg=colors["bg_card"], highlightthickness=0)
        canvas.pack(fill=tk.X)
        
        stats = self.storage.get_all_game_stats()
        
        # Pie chart for Games Played
        games_played = {s['game']: s.get('games_played', 0) for s in stats if s.get('games_played', 0) > 0}
        total_played = sum(games_played.values())
        
        cx, cy, r = 150, 125, 80
        if total_played > 0:
            start_angle = 0
            palette = ["#4fc3f7", "#ce93d8", "#ff8a80", "#69f0ae", "#ffab40", "#ffd740", "#ef5350"]
            for i, (game, count) in enumerate(games_played.items()):
                extent = (count / total_played) * 360
                color = palette[i % len(palette)]
                canvas.create_arc(cx - r, cy - r, cx + r, cy + r,
                                  start=start_angle, extent=extent, fill=color,
                                  outline=colors["bg_card"], width=2)
                canvas.create_rectangle(300, 30 + i * 20, 315, 45 + i * 20, fill=color, outline="")
                canvas.create_text(325, 37 + i * 20, text=f"{game.title()} ({count})",
                                   fill=colors["text"], anchor="w", font=self.theme.get_font("caption"))
                start_angle += extent
            canvas.create_text(cx, cy, text=f"Total\n{total_played}", fill=colors["bg_dark"],
                               font=("Segoe UI", 12, "bold"), justify=tk.CENTER)
        else:
            canvas.create_text(cx, cy, text="No Games\nPlayed", fill=colors["text_muted"],
                               font=("Segoe UI", 12))
        
        # Bar chart for Player Time
        time_played = {s['game']: s.get('total_time_seconds', 0) for s in stats if s.get('total_time_seconds', 0) > 0}
        tx, ty, tw, th = 450, 200, 300, 150
        if time_played:
            max_time = max(time_played.values())
            bar_width = tw / len(time_played)
            for i, (game, t) in enumerate(time_played.items()):
                h = (t / max_time) * th if max_time > 0 else 0
                x0 = tx + i * bar_width + 10
                y0 = ty - h
                x1 = x0 + bar_width - 20
                y1 = ty
                canvas.create_rectangle(x0, y0, x1, y1, fill=colors["primary"], outline="")
                canvas.create_text((x0 + x1) / 2, ty + 15, text=game[:3].title(),
                                   fill=colors["text_secondary"], font=("Segoe UI", 9))
                canvas.create_text((x0 + x1) / 2, y0 - 10, text=f"{t}s",
                                   fill=colors["primary"], font=("Segoe UI", 9))
        else:
            canvas.create_text(tx + tw / 2, ty - th / 2, text="No Time Data",
                               fill=colors["text_muted"], font=("Segoe UI", 12))
    
    pages.profile.ProfilePage._build_ui = patched_profile_build
    
    # Also ensure AVATAR_MAP is available on the class
    if not hasattr(pages.profile.ProfilePage, 'AVATAR_MAP'):
        pages.profile.ProfilePage.AVATAR_MAP = AVATAR_MAP

except (AttributeError, TypeError) as e:
    print(f"[WARNING] Could not patch Profile: {e}")


# --- Patch 5: Equip avatar triggers achievement ---
try:
    if not hasattr(pages.profile.ProfilePage, '_original_equip_avatar'):
        pages.profile.ProfilePage._original_equip_avatar = pages.profile.ProfilePage._equip_avatar
    
    def patched_equip_avatar(self, item_id):
        self._original_equip_avatar(item_id)
        try:
            if hasattr(self.hub.achievements, 'unlock'):
                self.hub.achievements.unlock("fashionista")
            elif hasattr(self.hub.achievements, 'increment_progress'):
                self.hub.achievements.increment_progress("fashionista", 1)
        except Exception:
            pass
    
    pages.profile.ProfilePage._equip_avatar = patched_equip_avatar
except (AttributeError, TypeError) as e:
    print(f"[WARNING] Could not patch equip_avatar: {e}")


# --- Patch 6: Friends List Names ---
try:
    original_refresh = hub.GameHub._refresh_friends_list
    def patched_refresh(self):
        colors = self.theme.colors
        for widget in self.friends_container.winfo_children():
            widget.destroy()
        
        friends = self.storage.get_setting("friends", [])
        if not friends:
            tk.Label(self.friends_container, text="No friends yet.\nClick ➕ to add!",
                     font=self.theme.get_font("caption"), fg=colors["text_muted"],
                     bg=colors["sidebar_bg"]).pack(pady=20)
            return
        
        for f in friends:
            fid = f.get('id', 'Unknown')
            
            if fid == self.storage.get_player_id():
                name = self.storage.get_setting("player_name", "Player")
            else:
                name = f.get('name', 'Player')
            
            status = f.get('status', 'offline')
            
            row = tk.Frame(self.friends_container, bg=colors["sidebar_bg"])
            row.pack(fill="x", pady=6, padx=10)
            
            dot_color = colors["success"] if status == "online" else colors["text_muted"]
            tk.Label(row, text="●", fg=dot_color, bg=colors["sidebar_bg"],
                     font=("Segoe UI", 10)).pack(side="left")
            tk.Label(row, text=f" {name} #{fid}", fg=colors["text_secondary"],
                     bg=colors["sidebar_bg"], font=self.theme.get_font("body")).pack(side="left")
    def patched_add_friend(self):
        import tkinter.simpledialog as simpledialog
        from tkinter import messagebox
        friend_id = simpledialog.askstring("Add Friend", "Enter friend's 7-character ID:", parent=self.root)
        if not friend_id or not friend_id.strip():
            return
            
        friend_id = friend_id.strip().upper()
        if len(friend_id) != 7 or not friend_id.isalnum():
            messagebox.showerror("Invalid ID", "Friend ID must be exactly 7 alphanumeric characters.")
            return
            
        friends = self.storage.get_setting("friends", [])
        if friend_id in [f.get('id') for f in friends]:
            messagebox.showinfo("Already Added", "This friend is already in your list.")
            return
            
        friend_name = simpledialog.askstring("Friend Nickname", f"Enter a nickname for {friend_id}:", parent=self.root)
        if not friend_name or not friend_name.strip():
            friend_name = f'User {friend_id}'
            
        friends.append({'id': friend_id, 'name': friend_name.strip(), 'status': 'online'})
        self.storage.save_setting("friends", friends)
        self._refresh_friends_list()
        self.sounds.play('win')
        
    hub.GameHub._refresh_friends_list = patched_refresh
    hub.GameHub._add_friend = patched_add_friend
except (AttributeError, TypeError) as e:
    print(f"[WARNING] Could not patch friends list: {e}")


# --- Patch 7: Game State Persistence ---
try:
    import time
    
    # Patch BaseGame pause and resume to be safer
    original_pause_game = games.base_game.BaseGame.pause_game
    def patched_pause_game(self):
        self._is_paused = True
        
        if hasattr(self, 'game_running'):
            self._was_game_running = self.game_running
            self.game_running = False
            
        if getattr(self, '_start_time', None) is not None:
            self._elapsed_time += time.time() - self._start_time
            self._start_time = None
            
        if hasattr(self, '_stop_timer'):
            self._stop_timer()
            
        try:
            self.unbind_all("<Key>")
        except Exception:
            pass
            
    def patched_resume_game(self):
        self._is_paused = False
        self._start_time = time.time()
        
        if hasattr(self, '_start_timer'):
            self._start_timer()
            
        if getattr(self, '_was_game_running', False):
            self.game_running = True
            if hasattr(self, '_game_loop'):
                self._game_loop()
                
        if hasattr(self, '_on_key'):
            self.bind_all("<Key>", self._on_key)
        if hasattr(self, '_on_keyboard'):
            self.bind_all("<Key>", self._on_keyboard)
            
    games.base_game.BaseGame.pause_game = patched_pause_game
    games.base_game.BaseGame.resume_game = patched_resume_game

    # Patch GameHub navigation
    original_navigate = hub.GameHub._navigate
    def patched_navigate(self, page_id):
        if page_id == getattr(self, '_current_page_id', None):
            return
            
        if not hasattr(self, '_frame_cache'):
            self._frame_cache = {}
            
        prev_page_id = getattr(self, '_current_page_id', None)
        
        if getattr(self, '_current_frame', None):
            self._current_frame.pack_forget()
            if hasattr(self._current_frame, 'pause_game'):
                try:
                    self._current_frame.pause_game()
                except Exception as e:
                    print(f"[WARN] Error pausing game: {e}")
                
            if prev_page_id:
                self._frame_cache[prev_page_id] = self._current_frame
                
            self._current_frame = None

        if page_id in self._frame_cache:
            self.sounds.play('click')
            self._current_page_id = page_id
            self._update_sidebar_selection(page_id)
            
            self._current_frame = self._frame_cache[page_id]
            
            if not getattr(self._current_frame, "winfo_exists", lambda: False)():
                del self._frame_cache[page_id]
                self._current_frame = None
                original_navigate(self, page_id)
                return
                
            self._current_frame.pack(fill=tk.BOTH, expand=True)
            if hasattr(self._current_frame, 'resume_game'):
                try:
                    self._current_frame.resume_game()
                except Exception as e:
                    print(f"[WARN] Error resuming game: {e}")
            return
            
        original_navigate(self, page_id)
        
    hub.GameHub._navigate = patched_navigate
except Exception as e:
    print(f"[WARNING] Could not patch navigate/pause: {e}")


# ============================================================================
# STEP 4: Fix the duplicate bankroll row issue
# ============================================================================
try:
    import sqlite3
    db_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data', 'neoplato.db')
    if os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        c = conn.cursor()
        # Remove the duplicate 1000-balance row if it exists
        c.execute("DELETE FROM bankroll WHERE id > 1")
        conn.commit()
        conn.close()
except Exception:
    pass


# ============================================================================
# STEP 5: Start the game
# ============================================================================
def main():
    root = tk.Tk()
    root.title("NeoMatchup — Game Hub")
    
    icon_path = os.path.join(os.path.dirname(__file__), 'icon.png')
    if os.path.exists(icon_path):
        try:
            from PIL import Image, ImageTk
            icon = ImageTk.PhotoImage(Image.open(icon_path))
            root.iconphoto(False, icon)
        except ImportError:
            try:
                icon = tk.PhotoImage(file=icon_path)
                root.iconphoto(False, icon)
            except Exception as e:
                print(f"[WARNING] Could not load icon natively: {e}")
        except Exception as e:
            print(f"[WARNING] Could not load icon with PIL: {e}")
            
    root.geometry("1200x800")
    
    # --- Patch 8: Fix Multiplayer Syncing ---
    import multiplayer.client
    original_send_message = multiplayer.client.RelayClient.send_message
    def patched_send_message(self, message):
        original_send_message(self, message)
        if message.get("action") in ("move", "drop"):
            # Echo the move locally so the sender's board updates
            if self.on_message:
                self.on_message(message)
    multiplayer.client.RelayClient.send_message = patched_send_message

    # --- Patch 9: Disconnect Buttons & BaseGame Improvements ---
    from games.base_game import BaseGame
    def patched_disconnect(self):
        # Allow games to handle their specific cleanup (e.g., unlocking menus, clearing players)
        if hasattr(self, "_disconnect_multiplayer"):
            self._disconnect_multiplayer()
            
        if hasattr(self, "client") and self.client:
            self.client.disconnect()
            self.client = None
            
        self.online_role = None
        self.online_waiting = False
        
        status_lbl = getattr(self, "status_label", getattr(self, "multi_status", None))
        if status_lbl:
            status_lbl.configure(text="Disconnected from multiplayer.", fg=self.theme.colors["gold"])
            
        # If server is running, stop it
        if hasattr(self, "server") and self.server:
            if hasattr(self.server, "shutdown"):
                self.server.shutdown()
            elif hasattr(self.server, "stop"):
                self.server.stop()
            self.server = None
            
    BaseGame.disconnect_multiplayer_manual = patched_disconnect
    
    # Apply to all relevant games by patching _on_mode_change where they build the multi_frame
    for game_mod in (games.tictactoe, games.chess, games.connect_four, games.roulette):
        if hasattr(game_mod, "TicTacToeGame"): cls = game_mod.TicTacToeGame
        elif hasattr(game_mod, "ChessGame"): cls = game_mod.ChessGame
        elif hasattr(game_mod, "ConnectFourGame"): cls = game_mod.ConnectFourGame
        elif hasattr(game_mod, "RouletteGame"): cls = game_mod.RouletteGame
        else: continue
        
        orig_on_mode_change = cls._on_mode_change
        def make_patched_mode_change(orig_method):
            def patched_mode_change(self):
                orig_method(self)
                if self.mode_var.get() == "online":
                    # Add disconnect button if it doesn't exist
                    if not hasattr(self, "_disconnect_btn"):
                        self._disconnect_btn = tk.Label(self.multi_frame, text="Disconnect", 
                                                        font=self.theme.get_font("button"), 
                                                        fg=self.theme.colors["bg_dark"], bg=self.theme.colors["error"], 
                                                        padx=20, pady=8, cursor="hand2")
                        self._disconnect_btn.pack(side=tk.LEFT, padx=10)
                        self._disconnect_btn.bind("<Button-1>", lambda e: self.disconnect_multiplayer_manual())
            return patched_mode_change
        cls._on_mode_change = make_patched_mode_change(orig_on_mode_change)

    # --- Patch 10: Roulette Overhaul ---
    try:
        import roulette_patch
        games.roulette.RouletteGame = roulette_patch.AdvancedRouletteGame
    except Exception as e:
        print(f"[WARNING] Could not load Roulette Overhaul: {e}")

    # --- Patch 11: Global Localhost Routing for Firewall Bypass ---
    import multiplayer.utils
    orig_decode = multiplayer.utils.decode_connection
    def patched_decode(code):
        ip, port = orig_decode(code)
        if ip and ip == multiplayer.utils.get_local_ip():
            ip = "127.0.0.1"
        return ip, port
    multiplayer.utils.decode_connection = patched_decode
    
    orig_client_init = multiplayer.client.RelayClient.__init__
    def patched_client_init(self, host, port, on_message=None):
        if host == multiplayer.utils.get_local_ip():
            host = "127.0.0.1"
        orig_client_init(self, host, port, on_message)
    multiplayer.client.RelayClient.__init__ = patched_client_init
    
    app = hub.GameHub(root)
    
    root.mainloop()

if __name__ == "__main__":
    main()
