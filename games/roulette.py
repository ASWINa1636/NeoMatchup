"""
NeoPlato — Roulette Casino
============================
European Roulette with animated wheel spinning, multiple bet types,
NeoCoins wagering, and payout calculations.
"""
import tkinter as tk, math, random
from games.base_game import BaseGame
from core.animations import ParticleSystem
from multiplayer.client import RelayClient
from multiplayer.server import RelayServer
from multiplayer.utils import get_local_ip, encode_connection, decode_connection

class RouletteGame(BaseGame):
    """European Roulette with animated wheel and NeoCoins betting."""; GAME_ID = "roulette"; GAME_TITLE = "Roulette"; GAME_ICON = "🎰"; GAME_DESCRIPTION = "Bet NeoCoins on the wheel"; GAME_RULES = "Place your NeoCoins on the betting board.\n\nYou can bet on specific numbers, colors (Red/Black), or Odd/Even.\n\nSpin the wheel to see if you win!"; SUPPORTS_MULTIPLAYER = False; COIN_REWARD_WIN = 0; NUMBERS = list(range(37)); RED_NUMBERS = {1, 3, 5, 7, 9, 12, 14, 16, 18, 19, 21, 23, 25, 27, 30, 32, 34, 36}; BLACK_NUMBERS = {2, 4, 6, 8, 10, 11, 13, 15, 17, 20, 22, 24, 26, 28, 29, 31, 33, 35}; PAYOUTS = {"number": 36, "red": 2, "black": 2, "odd": 2, "even": 2, "low": 2, "high": 2, "dozen_1": 3, "dozen_2": 3, "dozen_3": 3}
    def __init__(self, parent, hub):
        self.bet_type = "red"; self.bet_number = 0; self.bet_amount = 10; self.spinning = False; self.result = None; self.spin_angle = 0; self.target_angle = 0; self.win_streak = 0; self._anim_id = None; self.client = None; self.server = None; self.online_role = None; self.online_waiting = False; super().__init__(parent, hub)
    
    def setup_ui(self):
        colors = self.theme.colors; mode_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); mode_frame.pack(pady=(10, 5)); self.mode_var = tk.StringVar(value="solo")
        for val, text in (("solo", "👤 Solo"), ("online", "🌐 Online (with friends)")):
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=val, font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], selectcolor=colors["bg_surface"], activebackground=colors["bg_dark"], command=self._on_mode_change, indicatoron=0, padx=16, pady=6, relief=tk.FLAT, bd=0)
            rb.pack(side=tk.LEFT, padx=4)
        self.multi_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        host_btn = tk.Label(self.multi_frame, text="Host Game", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["primary"], padx=20, pady=8, cursor="hand2"); host_btn.pack(side=tk.LEFT, padx=10)
        
        host_btn.bind("<Button-1>", (lambda e: self._host_game()))
        
        join_btn = tk.Label(self.multi_frame, text="Join Game", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["secondary"], padx=20, pady=8, cursor="hand2")
        
        join_btn.pack(side=tk.LEFT, padx=10); join_btn.bind("<Button-1>", (lambda e: self._join_game())); self.copy_btn = tk.Label(self.multi_frame, text="📋 Copy Code", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["gold"], padx=20, pady=8, cursor="hand2"); self.current_room_code = ""
        
        self.copy_btn.bind("<Button-1>", (lambda e: self._copy_code()))
        
        self.multi_status = tk.Label(self.multi_frame, text="", font=self.theme.get_font("caption"), fg=colors["text_secondary"], bg=colors["bg_dark"])
        
        self.multi_status.pack(side=tk.LEFT, padx=10)
        
        main = tk.Frame(self.content_frame, bg=colors["bg_dark"]); main.pack(fill=tk.BOTH, expand=True, padx=20, pady=10); left = tk.Frame(main, bg=colors["bg_dark"])
        
        left.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        self.wheel_canvas = tk.Canvas(left, width=360, height=360, bg=colors["bg_dark"], highlightthickness=0); self.wheel_canvas.pack(pady=10)
        
        self.particles = ParticleSystem(self.wheel_canvas)
        
        self.result_label = tk.Label(left, text="Place your bet!", font=self.theme.get_font("heading"), fg=colors["text"], bg=colors["bg_dark"]); self.result_label.pack(pady=5); self.result_number = tk.Label(left, text="", font=("Segoe UI", 48, "bold"), fg=colors["gold"], bg=colors["bg_dark"]); self.result_number.pack()
        
        right = tk.Frame(main, bg=colors["bg_surface"], width=350, padx=20, pady=15)
        
        right.pack(side=tk.RIGHT, fill=tk.Y); right.pack_propagate(False)
        
        tk.Label(right, text="🎰 Place Your Bet", font=self.theme.get_font("heading_sm"), fg=colors["text"], bg=colors["bg_surface"]).pack(pady=(0, 10))
        
        self.balance_label = tk.Label(right, text=f"🪙 {self.bankroll.balance:,}", font=self.theme.get_font("heading_sm"), fg=colors["gold"], bg=colors["bg_surface"])
        
        self.balance_label.pack(pady=5); amt_frame = tk.Frame(right, bg=colors["bg_surface"]); amt_frame.pack(pady=10)
        
        tk.Label(amt_frame, text="Bet Amount:", font=self.theme.get_font("body"), fg=colors["text_secondary"], bg=colors["bg_surface"]).pack(side=tk.LEFT); self.bet_var = tk.StringVar(value="10")
        
        bet_entry = tk.Entry(amt_frame, textvariable=self.bet_var, width=8, font=self.theme.get_font("body_bold"), bg=colors["bg_card"], fg=colors["text"], insertbackground=colors["text"], bd=1, relief=tk.FLAT); bet_entry.pack(side=tk.LEFT, padx=10)
        
        quick_frame = tk.Frame(right, bg=colors["bg_surface"]); quick_frame.pack(pady=5)
        for amt in (10, 25, 50, 100, 500):
            btn = tk.Label(quick_frame, text=str(amt), font=self.theme.get_font("caption"), fg=colors["text"], bg=colors["bg_card"], padx=8, pady=3, cursor="hand2")
            btn.pack(side=tk.LEFT, padx=2)
            btn.bind("<Button-1>", (lambda e, a: self.bet_var.set(str(a))))
        
        tk.Frame(right, bg=colors["border"], height=1).pack(fill=tk.X, pady=10)
        
        tk.Label(right, text="Bet Type:", font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_surface"]).pack(anchor="w")
        
        self.bet_type_var = tk.StringVar(value="red")
        
        bet_types = [("🔴 Red", "red"), ("⚫ Black", "black"), ("Odd", "odd"), ("Even", "even"), ("1-18", "low"), ("19-36", "high"), ("1-12", "dozen_1"), ("13-24", "dozen_2"), ("25-36", "dozen_3")]
        
        types_frame = tk.Frame(right, bg=colors["bg_surface"]); types_frame.pack(fill=tk.X, pady=5)
        for i, (text, val) in enumerate(bet_types):
            rb = tk.Radiobutton(types_frame, text=text, variable=self.bet_type_var, value=val, font=self.theme.get_font("caption"), fg=colors["text"], bg=colors["bg_surface"], selectcolor=colors["bg_card"], activebackground=colors["bg_surface"], command=(lambda: self.num_var.set("")), indicatoron=0, padx=6, pady=3, relief=tk.FLAT, bd=0)
            rb.grid(row=i // 3, column=i % 3, padx=2, pady=2, sticky="ew")
        num_frame = tk.Frame(right, bg=colors["bg_surface"]); num_frame.pack(fill=tk.X, pady=5)
        
        tk.Label(num_frame, text="Or bet on number (0-36):", font=self.theme.get_font("caption"), fg=colors["text_secondary"], bg=colors["bg_surface"]).pack(side=tk.LEFT); self.num_var = tk.StringVar(value="")
        
        num_entry = tk.Entry(num_frame, textvariable=self.num_var, width=4, font=self.theme.get_font("body"), bg=colors["bg_card"], fg=colors["text"], insertbackground=colors["text"], bd=1, relief=tk.FLAT); num_entry.pack(side=tk.LEFT, padx=5)
        
        tk.Frame(right, bg=colors["border"], height=1).pack(fill=tk.X, pady=10); self.spin_btn = tk.Label(right, text="🎰 SPIN!", font=("Segoe UI", 18, "bold"), fg=colors["bg_darkest"], bg=colors["primary"], padx=30, pady=10, cursor="hand2")
        
        self.spin_btn.pack(pady=10); self.spin_btn.bind("<Button-1>", (lambda e: self._spin()))
        
        self.history_label = tk.Label(right, text="History: —", font=self.theme.get_font("caption"), fg=colors["text_muted"], bg=colors["bg_surface"], wraplength=280, justify=tk.LEFT); self.history_label.pack(pady=5, anchor="w"); self._results_history = []; self._draw_wheel(0)
    
    def start_game(self):
        self._is_running = True; self.game_active = True; self.spinning = False; self._results_history = []; self.win_streak = 0; self._update_balance(); self._draw_wheel(0)
        if self.mode_var.get() != "online":
            self.online_role = None
            self.online_waiting = False
            self._disconnect_multiplayer()
            self.spin_btn.configure(state=tk.NORMAL)
            self.result_label.configure(text="Place your bet!")
    
    def _on_mode_change(self):
        if self.mode_var.get() == "online":
            self.multi_frame.pack(pady=5, after=self.content_frame.winfo_children()[0])
            self.result_label.configure(text="Select Host or Join to play online.")
            self.multi_status.configure(text="")
        else:
            self.multi_frame.pack_forget()
            self._disconnect_multiplayer()
        
        self.start_game()
    
    def cleanup(self):
        self.spinning = False
        if self._anim_id:
            pass
        self.after_cancel(self._anim_id); self._disconnect_multiplayer(); super().cleanup()
    
    def _draw_wheel(self, angle):
        self.wheel_canvas.delete("wheel"); cx, cy = (180, 180); outer_r = 160; inner_r = 100; order = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]; n = len(order); slot_angle = 360 / n
        for i, num in enumerate(order):
            start = angle + i * slot_angle
            if num == 0:
                color = "#2e7d32"
            elif num in self.RED_NUMBERS:
                color = "#c62828"
            else:
                color = "#212121"
            self.wheel_canvas.create_arc(cx - outer_r, cy - outer_r, cx + outer_r, cy + outer_r, start=start, extent=slot_angle, fill=color, outline="#555555", width=1, tags="wheel")
            mid_angle = math.radians(start + slot_angle / 2)
            tx = cx + (outer_r - 25) * math.cos(mid_angle)
            ty = cy - (outer_r - 25) * math.sin(mid_angle)
            self.wheel_canvas.create_text(tx, ty, text=str(num), font=("Segoe UI", 8, "bold"), fill="white", tags="wheel")
        
        self.wheel_canvas.create_oval(cx - inner_r, cy - inner_r, cx + inner_r, cy + inner_r, fill="#1a1a2e", outline="#333355", width=2, tags="wheel"); self.wheel_canvas.create_oval(cx - 20, cy - 20, cx + 20, cy + 20, fill="#ffd700", outline="#b8860b", width=2, tags="wheel"); self.wheel_canvas.create_polygon(cx - 8, 8, cx + 8, 8, cx, 22, fill="#ffffff", outline="#cccccc", tags="wheel")
    
    def _spin(self):
        if self.spinning or self.online_waiting:
            pass
        if self.mode_var.get() == "online" and self.online_role != 1:
            self.result_label.configure(text="Only the Host can spin the wheel!", fg=self.theme.colors["error"])
        try:
            self.bet_amount = int(self.bet_var.get())
            if self.bet_amount <= 0:
                pass
            return None
            if not self.bankroll.can_afford(self.bet_amount):
                colors = self.theme.colors
                self.result_label.configure(text="Not enough NeoCoins!", fg=colors["error"])
            return None
            num_text = self.num_var.get().strip()
            if num_text.isdigit():
                if 0 <= int(num_text) or int(num_text) <= 36:
                    pass
                
            else:
                self.bet_type = "number"
                self.bet_number = int(num_text)
        except ValueError:
            self.bet_amount = 10
            self.bet_var.set("10")
    
    def _spin_step(self, current, target):
        if current >= target:
            self._on_spin_complete(); remaining = target - current; speed = max(2, remaining * 0.05); current += speed; self._draw_wheel(current % 360); interval = max(16, int(33 * (1 + current / target * 2)))
        
        self._anim_id = self.after(interval, (lambda: self._spin_step(current, target)))
    
    def _on_spin_complete(self):
        self.spinning = False; colors = self.theme.colors; num = self.result
        if num == 0:
            color_text = "🟢 Green"
            num_color = "#2e7d32"
        elif num in self.RED_NUMBERS:
            color_text = "🔴 Red"
            num_color = "#c62828"
        else:
            color_text = "⚫ Black"
            num_color = "#555555"
        self.result_number.configure(text=str(num), fg=num_color); won = self._check_win(num)
        if won:
            payout = self.PAYOUTS.get(self.bet_type, 2)
            winnings = (self.bet_amount) * payout
            self.bankroll.earn(winnings, f"Roulette win ({self.bet_type})", self.GAME_ID)
            self.result_label.configure(text=f"🎉 {color_text} {num} — You win {winnings} coins!", fg=colors["success"])
            match self:
                case 1000 if len(self._results_history) > 10:
                    return None
        
        else:
            self.win_streak = 0
        
        self._results_history = self._results_history[-10:]
    
    def _check_win(self, result):
        if self.bet_type == "number":
            pass
        
        return result == self.bet_number
        if self.bet_type == "red":
            pass
        
        return result in self.RED_NUMBERS
        if self.bet_type == "black":
            pass
        
        return result in self.BLACK_NUMBERS
        if self.bet_type == "odd":
            pass
        
        return result > 0 and result % 2 == 1
        if self.bet_type == "even":
            pass
        
        return result > 0 and result % 2 == 0
        if self.bet_type == "low":
            1 <= result if 1 <= result else result <= 18
            return result <= 18
        if self.bet_type == "high":
            19 <= result if 19 <= result else result <= 36
            return result <= 36
        if self.bet_type == "dozen_1":
            1 <= result if 1 <= result else result <= 12
            return result <= 12
        if self.bet_type == "dozen_2":
            13 <= result if 13 <= result else result <= 24
            return result <= 24
        if self.bet_type == "dozen_3":
            25 <= result if 25 <= result else result <= 36
            return result <= 36
        
        return False
    
    def _update_balance(self):
        self.balance_label.configure(text=f"🪙 {self.bankroll.balance:,}")
    
    def _animate_particles(self):
        if self.particles.is_active:
            self.particles.update()
            self._anim_id = self.after(33, self._animate_particles)
    
    def _host_game(self):
        self._disconnect_multiplayer(); colors = self.theme.colors
        try:
            self.server = RelayServer(host="0.0.0.0", port=0)
            self.server.server_socket.bind((self.server.host,
    self.server.port))
            self.server.port = self.server.server_socket.getsockname()[1]
            self.server.server_socket.listen(2)
            import threading
            self.server._accept_thread = threading.Thread(target=self.server._accept_loop, daemon=True)
            self.server._accept_thread.start()
            ip = get_local_ip()
            code = encode_connection(ip, self.server.port)
            self.current_room_code = code
            self.multi_status.configure(text=f"Hosting... Code: {code}", fg=colors["gold"])
            self.copy_btn.pack(side=tk.LEFT, padx=10)
            self._connect_client(ip, self.server.port)
        except:
            pass
    
    def _copy_code(self):
        if self.current_room_code:
            self.clipboard_clear()
            self.clipboard_append(self.current_room_code)
            colors = self.theme.colors
            self.multi_status.configure(text="Code copied to clipboard!", fg=colors["success"])
            self.after(2000, (lambda: self.multi_status.configure(text=f"Hosting... Code: {self.current_room_code}", fg=colors["gold"])))
    
    def _join_game(self):
        from tkinter import simpledialog; colors = self.theme.colors; code = simpledialog.askstring("Join Game", "Enter Room Code:", parent=self)
        if not code:
            pass; ip, port = decode_connection(code)
        if not ip:
            self.multi_status.configure(text="Invalid Code!", fg=colors["error"]); self.multi_status.configure(text=f"Connecting to {code}...", fg=colors["text_secondary"]); self._connect_client(ip, port)
    
    def _connect_client(self, ip, port):
        self.client = RelayClient(ip, port, on_message=self._on_net_message_raw)
        if not self.client.connect():
            self.multi_status.configure(text="Connection failed!", fg=self.theme.colors["error"])
            self.client = None
    
    def _disconnect_multiplayer(self):
        if self.client:
            self.client.disconnect()
            self.client = None
        elif self.server:
            self.server.shutdown()
            self.server = None
        self.online_role = None; self.copy_btn.pack_forget(); self.current_room_code = ""
    
    def _on_net_message_raw(self, message):
        self.after(0, (lambda: self._process_net_message(message)))
    
    def _process_net_message(self, message):
        try:
            if not self.winfo_exists():
                pass
            return None
            action = message.get("action")
            colors = self.theme.colors
            if action == "assign":
                if message["player"] == "p1":
                    pass
                self.online_role = 2
                self.online_waiting = True
            return None
            if action == "waiting":
                self.multi_status.configure(text=f"Code: {encode_connection(get_local_ip(), self.server.port)} - Waiting for opponent...", fg=colors["gold"])
            return None
            if action == "start":
                self.online_waiting = False
                self.multi_status.configure(text="Game Started! Host controls the spin.", fg=colors["success"])
                self.result_label.configure(text="Place your bets!")
                if self.server:
                    pass
                self.hub.achievements.check_and_unlock("multi_host", "multi_join")
            return None
            if action == "spin" and self.online_role == 2:
                self.result = message["result"]
                total_spin = message["target_angle"]
                try:
                    self.bet_amount = int(self.bet_var.get())
                    if self.bet_amount > 0 and self.bankroll.can_afford(self.bet_amount):
                        num_text = self.num_var.get().strip()
                        if num_text.isdigit():
                            if 0 <= int(num_text) or int(num_text) <= 36:
                                pass
                            
                        else:
                            self.bet_type = "number"
                            self.bet_number = int(num_text)
                    else:
                        self.bet_type = self.bet_type_var.get()
                    self.bankroll.spend(self.bet_amount, f"Roulette bet: {self.bet_type}", self.GAME_ID)
                    self._update_balance()
                except:
                    pass
                self.bet_amount = 0
                self.spinning = True
                self.spin_angle = 0
                self.target_angle = total_spin
                self.result_label.configure(text="Spinning...", fg=colors["primary"])
                self.result_number.configure(text="")
                self._spin_step(0, total_spin)
            return None
            if action == "opponent_disconnected":
                self.game_active = False
                self.multi_status.configure(text="Opponent disconnected!", fg=colors["error"])
                self._disconnect_multiplayer()
            return None
            if action == "error":
                self.multi_status.configure(text=message["message"], fg=colors["error"])
        except ValueError:
            self.bet_amount = 10
