"""
NeoPlato — Wordle
==================
Word guessing game with color feedback, on-screen keyboard,
daily challenge mode, and NeoCoins rewards.
"""
import tkinter as tk, random, hashlib
from datetime import date
from games.base_game import BaseGame
from core.animations import ParticleSystem

class WordleGame(BaseGame):
    """Wordle word guessing game."""; GAME_ID = "wordle"; GAME_TITLE = "Wordle"; GAME_ICON = "📝"; GAME_DESCRIPTION = "Guess the 5-letter word"; GAME_RULES = "Guess the 5-letter word in 6 tries.\n\n• Green: The letter is in the word and in the correct spot.\n• Yellow: The letter is in the word but in the wrong spot.\n• Gray: The letter is not in the word in any spot."; SUPPORTS_MULTIPLAYER = False; COIN_REWARD_WIN = 30; MAX_GUESSES = 6; WORD_LENGTH = 5; WORD_LIST = ["about", "above", "abuse", "actor", "acute", "admit", "adopt", "adult", "after", "again", "agent", "agree", "ahead", "alarm", "album", "alert", "alien", "align", "alike", "alive", "alley", "allow", "alone", "along", "alter", "among", "angel", "anger", "angle", "angry", "anime", "ankle", "apart", "apple", "apply", "arena", "argue", "arise", "armor", "array", "arrow", "asset", "audit", "avoid", "awake", "award", "aware", "awful", "bacon", "badge", "basic", "basis", "beach", "beard", "beast", "began", "begin", "being", "belly", "below", "bench", "berry", "bible", "birth", "black", "blade", "blame", "bland", "blank", "blast", "blaze", "bleed", "blend", "bless", "blind", "blink", "block", "blood", "bloom", "blown", "board", "bonus", "boost", "booth", "bound", "brain", "brand", "brave", "bread", "break", "breed", "brick", "bride", "brief", "bring", "broad", "broke", "brook", "brown", "brush", "buddy", "build", "built", "bunch", "burst", "buyer", "cabin", "cable", "camel", "candy", "cargo", "carry", "catch", "cause", "cedar", "chain", "chair", "chalk", "chaos", "charm", "chart", "chase", "cheap", "check", "cheek", "cheer", "chess", "chest", "chief", "child", "china", "chunk", "civic", "civil", "claim", "clash", "class", "clean", "clear", "clerk", "click", "cliff", "climb", "cling", "clock", "clone", "close", "cloth", "cloud", "coach", "coast", "comet", "comic", "coral", "couch", "could", "count", "court", "cover", "crack", "craft", "crane", "crash", "crazy", "cream", "green", "creek", "crime", "cross", "crowd", "crown", "crush", "curve", "cycle", "daily", "dance", "death", "debug", "delay", "demon", "depot", "depth", "derby", "devil", "diary", "dirty", "disco", "ditch", "dizzy", "dodge", "doing", "donor", "doubt", "dough", "draft", "drain", "drake", "drama", "drank", "drape", "drawn", "dream", "dress", "dried", "drift", "drill", "drink", "drive", "drone", "drops", "drove", "drugs", "drums", "drunk", "dryer", "dying", "eager", "eagle", "early", "earth", "eight", "elect", "elite", "email", "empty", "enemy", "enjoy", "enter", "entry", "equal", "error", "essay", "event", "every", "exact", "exile", "exist", "extra", "faint", "faith", "false", "fancy", "fatal", "fault", "feast", "fence", "ferry", "fetch", "fever", "fiber", "field", "fifth", "fifty", "fight", "final", "first", "fixed", "flame", "flash", "fleet", "flesh", "float", "flood", "floor", "flora", "flour", "fluid", "flush", "flute", "focal", "focus", "force", "forge", "forth", "forum", "found", "frame", "frank", "fraud", "fresh", "front", "frost", "fruit", "fully", "funny", "gains", "genre", "ghost", "giant", "given", "glass", "globe", "gloom", "glory", "glove", "going", "grace", "grade", "grain", "grand", "grant", "graph", "grasp", "grass", "grave", "great", "greed", "grill", "grind", "gross", "group", "grove", "grown", "guard", "guess", "guest", "guide", "guild", "guilt", "guise", "gummy", "habit", "happy", "harsh", "haven", "heart", "heavy", "hedge", "hello", "hence", "herbs", "honor", "horse", "hotel", "house", "human", "humor", "ideal", "image", "imply", "inbox", "index", "indie", "inner", "input", "irony", "ivory", "jewel", "jimmy", "joint", "joker", "judge", "juice", "jumbo", "knife", "knock", "known", "label", "labor", "lance", "large", "laser", "later", "laugh", "layer", "learn", "lease", "leave", "legal", "lemon", "level", "light", "limit", "linen", "liver", "local", "logic", "login", "loose", "lover", "lower", "lucky", "lunch", "lunar", "lying", "magic", "major", "maker", "manga", "manor", "maple", "march", "match", "maybe", "mayor", "media", "mercy", "merge", "merit", "metal", "meter", "might", "minor", "minus", "mixed", "model", "money", "month", "moral", "mount", "mouse", "mouth", "moved", "mover", "movie", "music", "naive", "nerve", "never", "night", "noble", "noise", "north", "noted", "novel", "nurse", "nylon", "occur", "ocean", "offer", "often", "olive", "onset", "opera", "orbit", "order", "organ", "other", "ought", "outer", "owner", "oxide", "ozone", "paint", "panel", "panic", "paper", "party", "paste", "patch", "pause", "peace", "pearl", "penny", "phase", "phone", "photo", "piano", "piece", "pilot", "pinch", "pitch", "pixel", "pizza", "place", "plain", "plane", "plant", "plate", "plaza", "plead", "pluck", "plumb", "plume", "plump", "plunge", "point", "poker", "polar", "pound", "power", "press", "price", "pride", "prime", "print", "prior", "prize", "probe", "proof", "proud", "prove", "proxy", "pulse", "punch", "pupil", "purse", "queen", "query", "quest", "queue", "quick", "quiet", "quota", "quote", "radar", "radio", "raise", "rally", "ranch", "range", "rapid", "ratio", "reach", "react", "reads", "ready", "realm", "rebel", "refer", "reign", "relax", "relay", "renew", "repay", "reply", "rider", "ridge", "rifle", "right", "rigid", "risky", "rival", "river", "robin", "robot", "rocky", "roman", "roots", "rouge", "rough", "round", "route", "royal", "rugby", "ruler", "rumor", "rural", "saint", "salad", "sauce", "scale", "scare", "scene", "scent", "scope", "score", "scout", "screw", "sense", "serve", "seven", "shade", "shake", "shall", "shame", "shape", "share", "shark", "sharp", "sheep", "sheer", "sheet", "shell", "shift", "shiny", "shirt", "shock", "shore", "short", "sight", "sigma", "since", "sixth", "sixty", "sized", "skill", "skull", "slash", "slave", "sleep", "slice", "slide", "slope", "smart", "smell", "smile", "smoke", "snake", "solar", "solid", "solve", "sonic", "sorry", "sound", "south", "space", "spare", "spark", "speak", "speed", "spend", "spent", "spice", "spike", "spine", "spoke", "spoon", "sport", "spray", "squad", "stack", "staff", "stage", "stain", "stake", "stall", "stamp", "stand", "stare", "start", "state", "stays", "steal", "steam", "steel", "steep", "steer", "stems", "stick", "stiff", "still", "stock", "stone", "stood", "store", "storm", "story", "stove", "strap", "straw", "strip", "stuck", "study", "stuff", "style", "sugar", "suite", "sunny", "super", "surge", "swamp", "swear", "sweat", "sweep", "sweet", "swept", "swift", "swing", "sword", "swore", "sworn", "syrup", "table", "taste", "teach", "teams", "teeth", "tempo", "tends", "tenor", "terms", "theme", "there", "thick", "thief", "thing", "think", "third", "those", "three", "threw", "throw", "thumb", "tiger", "tight", "timer", "tired", "title", "toast", "token", "topic", "total", "touch", "tough", "tower", "toxic", "trace", "track", "trade", "trail", "train", "trait", "trash", "treat", "trend", "trial", "tribe", "trick", "tried", "troop", "truck", "truly", "trump", "trunk", "trust", "truth", "tumor", "tuned", "turns", "twist", "tying", "ultra", "uncle", "under", "unify", "union", "unite", "unity", "until", "upper", "upset", "urban", "usage", "usual", "valid", "value", "valve", "vapor", "vault", "venue", "verse", "video", "vigor", "vinyl", "virus", "visit", "vista", "vital", "vivid", "vocal", "vodka", "voice", "voter", "wages", "waste", "watch", "water", "weary", "weave", "weigh", "weird", "whale", "wheat", "wheel", "where", "which", "while", "white", "whole", "whose", "widow", "width", "witch", "woman", "world", "worry", "worse", "worst", "worth", "would", "wound", "wrist", "wrote", "yacht", "yield", "young", "youth", "zebra"]
    def __init__(self, parent, hub):
        self.target_word = ""; self.guesses = []; self.current_guess = ""; self.game_active = False; self.is_daily = False; self._anim_id = None; self._key_states = {}; super().__init__(parent, hub)
    
    def setup_ui(self):
        colors = self.theme.colors; mode_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); mode_frame.pack(pady=(10, 5)); self.mode_var = tk.StringVar(value="free")
        for val, text in (("free", "🎲 Free Play"), ("daily", "📅 Daily Challenge")):
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=val, font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], selectcolor=colors["bg_surface"], activebackground=colors["bg_dark"], command=(lambda: self.start_game()), indicatoron=0, padx=16, pady=6, relief=tk.FLAT, bd=0)
            rb.pack(side=tk.LEFT, padx=4)
        color_map
        grid_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        grid_frame.pack(expand=True, pady=(10, 5)); self.grid_labels = []
        for r in range(self.MAX_GUESSES):
            row_labels = []
            for c in range(self.WORD_LENGTH):
                lbl = tk.Label(grid_frame, text="", width=4, height=2, font=("Segoe UI", 20, "bold"), bg=colors["bg_card"], fg=colors["text"], relief=tk.RIDGE, bd=2)
                lbl.grid(row=r, column=c, padx=4, pady=4)
                row_labels.append(lbl)
            None
            self.grid_labels.append(row_labels)
        
        self.status_label = tk.Label(self.content_frame, text="Type a 5-letter word", font=self.theme.get_font("body"), fg=colors["text_secondary"], bg=colors["bg_dark"]); self.status_label.pack(pady=5); kb_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        kb_frame.pack(pady=10); keyboard_rows = ["QWERTYUIOP", "ASDFGHJKL", "⏎ZXCVBNM⌫"]; self.kb_buttons = {}
        for row_idx, row in enumerate(keyboard_rows):
            row_frame = tk.Frame(kb_frame, bg=colors["bg_dark"])
            row_frame.pack()
            for ch in row:
                display = ch
                width = 3
                if ch == "⏎":
                    display = "Enter"
                    width = 5
                elif ch == "⌫":
                    display = "Del"
                width = 4
                btn = tk.Label(row_frame, text=display, width=width, height=1, font=("Segoe UI", 12, "bold"), bg=colors["bg_card"], fg=colors["text"], relief=tk.RAISED, bd=1, cursor="hand2", padx=2)
                btn.pack(side=tk.LEFT, padx=2, pady=2)
                btn.bind("<Button-1>", (lambda e, key: self._on_key_press(key)))
                color_map = {"correct": "#538d4e", "present": "#b59f3b", "absent": "#3a3a4c"}
                btn.bind("<Enter>", (lambda e, b: b.configure(bg=colors["bg_hover"])))
                btn.bind("<Leave>", (lambda e, b: b.configure(bg=color_map.get(self._key_states.get(b.cget("text").upper()), colors["bg_card"]))))
                self.kb_buttons[ch] = btn
        self.bind_all("<Key>", self._on_keyboard)
    
    def start_game(self):
        self._is_running = True; self.is_daily = self.mode_var.get() == "daily"
        if self.is_daily:
            today = date.today().isoformat()
            seed = int(hashlib.md5(today.encode()).hexdigest(), 16)
            self.target_word = self.WORD_LIST[seed % len(self.WORD_LIST)].upper()
        else:
            self.target_word = random.choice(self.WORD_LIST).upper()
        self.guesses = []; self.current_guess = ""; self.game_active = True; self._key_states = {}
        
        colors = self.theme.colors
        for r in range(self.MAX_GUESSES):
            for c in range(self.WORD_LENGTH):
                self.grid_labels[r][c].configure(text="", bg=colors["bg_card"], fg=colors["text"])
            None
        
        for ch, btn in self.kb_buttons.items():
            if not ch not in ("⏎", "⌫"):
                pass
            btn.configure(bg=colors["bg_card"], fg=colors["text"])
        
        self.status_label.configure(text="Type a 5-letter word", fg=colors["text_secondary"])
    
    def cleanup(self):
        self.game_active = False
        try:
            self.unbind_all("<Key>")
            super().cleanup()
        except Exception:
            pass
    
    def _on_keyboard(self, event):
        key = event.keysym.upper()
        if key == "RETURN":
            self._on_key_press("⏎")
        if key == "BACKSPACE":
            self._on_key_press("⌫")
        if len(key) == 1:
            if key.isalpha():
                self._on_key_press(key)
            return None
    
    def _on_key_press(self, key):
        if not self.game_active:
            pass; colors = self.theme.colors; row = len(self.guesses)
        if key == "⌫":
            if self.current_guess:
                self.current_guess = self.current_guess[:-1]
                col = len(self.current_guess)
                self.grid_labels[row][col].configure(text="")
            return None
        if key == "⏎":
            if len(self.current_guess) == self.WORD_LENGTH:
                self._submit_guess()
            return None
        if key.isalpha():
            if len(key) == 1:
                if len(self.current_guess) < self.WORD_LENGTH:
                    self.current_guess += key.upper()
                    col = len(self.current_guess) - 1
                    self.grid_labels[row][col].configure(text=key.upper(), fg=colors["text"])
                    self.sounds.play("click")
                return None
            return None
    
    def _submit_guess(self):
        guess = self.current_guess.upper(); row = len(self.guesses); colors = self.theme.colors; feedback = self._get_feedback(guess); self.guesses.append(guess); self._reveal_row(row, guess, feedback, 0)
    
    def _get_feedback(self, guess):
        target = list(self.target_word); result = ["absent"] * (self.WORD_LENGTH); used = [False] * (self.WORD_LENGTH)
        for i in range(self.WORD_LENGTH):
            if not guess[i] == target[i]:
                pass
            result[i] = "correct"
            used[i] = True
        for i in range(self.WORD_LENGTH):
            if result[i] == "correct":
                pass
            for j in range(self.WORD_LENGTH):
                if used[j]:
                    pass
                elif not guess[i] == target[j]:
                    pass
                result[i] = "present"
                used[j] = True
                None
        
        return result
    
    def _reveal_row(self, row, guess, feedback, col):
        if col >= self.WORD_LENGTH:
            self._update_keyboard(guess, feedback)
            self._check_game_state(guess); colors = self.theme.colors; color_map = {"correct": "#538d4e", "present": "#b59f3b", "absent": "#3a3a4c"}; lbl = self.grid_labels[row][col]; bg = color_map[feedback[col]]
        
        lbl.configure(bg=bg, fg="#ffffff")
        
        self.after(150, (lambda: self._reveal_row(row, guess, feedback, col + 1)))
    
    def _update_keyboard(self, guess, feedback):
        priority = {"correct": 3, "present": 2, "absent": 1}; color_map = {"correct": "#538d4e", "present": "#b59f3b", "absent": "#3a3a4c"}
        for i, letter in enumerate(guess):
            state = feedback[i]
            current = self._key_states.get(letter)
            if not current is None and priority[state] > priority.get(current, 0):
                pass
            self._key_states[letter] = state
            if not letter in self.kb_buttons:
                pass
            self.kb_buttons[letter].configure(bg=color_map[state], fg="#ffffff")
    
    def _check_game_state(self, guess):
        colors = self.theme.colors
        if guess == self.target_word:
            self.game_active = False
            attempts = len(self.guesses)
            self.status_label.configure(text=f"🎉 Correct in {attempts} guesses!", fg=colors["success"])
            self.score = (self.MAX_GUESSES - attempts + 1) * 100
            if attempts == 1:
                self.achievements.check_and_unlock("wordle_one_guess", 1)
            if self.is_daily:
                self.on_win(bonus_coins=20, achievement_id="wordle_first")
                self.achievements.increment_progress("wordle_daily_7")
            else:
                self.on_win(achievement_id="wordle_first")
        if len(self.guesses) >= self.MAX_GUESSES:
            self.game_active = False
            self.status_label.configure(text=f"The word was: {self.target_word}", fg=colors["error"])
            self.on_lose(); self.current_guess = ""
