"""
NeoPlato — Connect Four
========================
Classic Connect Four with animated disc drops, win detection,
hotseat multiplayer, and basic AI opponent.
"""
import tkinter as tk, random, math
from games.base_game import BaseGame
from core.animations import ParticleSystem
from multiplayer.client import RelayClient
from multiplayer.server import RelayServer
from multiplayer.utils import get_local_ip, encode_connection, decode_connection

class ConnectFourGame(BaseGame):
    """Connect Four with drop animations and AI."""; GAME_ID = "connect_four"; GAME_TITLE = "Connect Four"; GAME_ICON = "🔴"; GAME_DESCRIPTION = "Drop discs to connect four"; GAME_RULES = "Take turns dropping discs into the grid.\n\nThe first player to connect 4 of their discs horizontally, vertically, or diagonally wins the game!"; SUPPORTS_MULTIPLAYER = True; COIN_REWARD_WIN = 30; ROWS = 6; COLS = 7; CELL_SIZE = 70
    def __init__(self, parent, hub):
        self.board = [[0] * (self.COLS) for _ in range(self.ROWS)]; self.current_player = 1; self.game_active = False; self.vs_ai = False; self._anim_id = None; self._dropping = False; self.p1_wins = 0; self.p2_wins = 0; self.draws = 0; self.client = None
        
        self.server = None; self.online_role = None; self.online_waiting = False
        
        super().__init__(parent, hub)
        __class__; _ = super
    
    def setup_ui(self):
        colors = self.theme.colors; mode_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); mode_frame.pack(pady=(10, 5)); self.mode_var = tk.StringVar(value="ai")
        for val, text in (("ai", "🤖 vs AI"), ("hotseat", "👥 Hotseat"), ("online", "🌐 Online")):
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=val, font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], selectcolor=colors["bg_surface"], activebackground=colors["bg_dark"], command=self._on_mode_change, indicatoron=0, padx=16, pady=6, relief=tk.FLAT, bd=0)
            rb.pack(side=tk.LEFT, padx=4)
        self.multi_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        host_btn = tk.Label(self.multi_frame, text="Host Game", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["primary"], padx=20, pady=8, cursor="hand2"); host_btn.pack(side=tk.LEFT, padx=10)
        
        host_btn.bind("<Button-1>", (lambda e: self._host_game()))
        
        join_btn = tk.Label(self.multi_frame, text="Join Game", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["secondary"], padx=20, pady=8, cursor="hand2")
        
        join_btn.pack(side=tk.LEFT, padx=10); join_btn.bind("<Button-1>", (lambda e: self._join_game())); self.copy_btn = tk.Label(self.multi_frame, text="📋 Copy Code", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["gold"], padx=20, pady=8, cursor="hand2"); self.current_room_code = ""
        
        self.copy_btn.bind("<Button-1>", (lambda e: self._copy_code()))
        
        canvas_w = (self.COLS) * (self.CELL_SIZE) + 20; canvas_h = (self.ROWS) * (self.CELL_SIZE) + 20
        
        canvas_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); canvas_frame.pack(expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=canvas_w, height=canvas_h, bg=colors["bg_surface"], highlightthickness=0)
        
        self.canvas.pack(padx=20, pady=10); self.canvas.bind("<Button-1>", self._on_click); self.canvas.bind("<Motion>", self._on_hover)
        
        self.particles = ParticleSystem(self.canvas)
        
        status_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="🔴 Red's turn", font=self.theme.get_font("heading_sm"), fg=colors["error"], bg=colors["bg_dark"])
        
        self.status_label.pack(); score_frame = tk.Frame(self.content_frame, bg=colors["bg_surface"], padx=20, pady=8); score_frame.pack(pady=5)
        
        self.p1_label = tk.Label(score_frame, text="🔴 Red: 0", font=self.theme.get_font("body_bold"), fg="#ef5350", bg=colors["bg_surface"])
        
        self.p1_label.pack(side=tk.LEFT, padx=15)
        
        self.draw_label = tk.Label(score_frame, text="Draw: 0", font=self.theme.get_font("body_bold"), fg=colors["text_secondary"], bg=colors["bg_surface"]); self.draw_label.pack(side=tk.LEFT, padx=15)
        
        self.p2_label = tk.Label(score_frame, text="🟡 Yellow: 0", font=self.theme.get_font("body_bold"), fg="#ffd740", bg=colors["bg_surface"])
        
        self.p2_label.pack(side=tk.LEFT, padx=15)
        
        new_btn = tk.Label(self.content_frame, text="🔄 New Game", font=self.theme.get_font("button"), fg=colors["primary"], bg=colors["bg_card"], padx=20, pady=8, cursor="hand2"); new_btn.pack(pady=8); new_btn.bind("<Button-1>", (lambda e: self.start_game()))
    
    def start_game(self):
        self.board = [[0] * (self.COLS) for _ in range(self.ROWS)]; self.current_player = 1; self.game_active = True; self.vs_ai = self.mode_var.get() == "ai"; self._dropping = False; self._is_running = True; self.particles.clear()
        if self.mode_var.get() != "online":
            self.online_role = None
            self.online_waiting = False
        self._disconnect_multiplayer()
        
        colors = self.theme.colors
        if self.online_role:
            role_text = self.online_role == 1 and "Yellow"
            self.status_label.configure(text=f"You are {role_text}. 🔴 Red's turn", fg="#ef5350")
        else:
            self.status_label.configure(text="🔴 Red's turn", fg="#ef5350")
        self._draw_board(); _ = None
    
    def _on_mode_change(self):
        if self.mode_var.get() == "online":
            self.multi_frame.pack(pady=5)
            self.status_label.configure(text="Select Host or Join to play online.", fg=self.theme.colors["text"])
        else:
            self.multi_frame.pack_forget()
            self._disconnect_multiplayer()
        self.start_game()
    
    def cleanup(self):
        self.game_active = False
        if self._anim_id:
            pass
        self.after_cancel(self._anim_id); self._disconnect_multiplayer(); super().cleanup()
    
    def _draw_board(self):
        self.canvas.delete("all"); colors = self.theme.colors; cs = self.CELL_SIZE; pad = 10; self.canvas.create_rectangle(pad, pad, pad + cs * (self.COLS), pad + cs * (self.ROWS), fill="#1a237e", outline="#283593", width=2)
        for r in range(self.ROWS):
            for c in range(self.COLS):
                cx = pad + c * cs + cs // 2
                cy = pad + r * cs + cs // 2
                radius = cs // 2 - 6
                piece = self.board[r][c]
                if piece == 1:
                    fill = "#ef5350"
                    outline = "#c62828"
                elif piece == 2:
                    fill = "#ffd740"
                    outline = "#f9a825"
                else:
                    fill = colors["bg_darkest"]
                    outline = "#0d1042"
                self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=fill, outline=outline, width=2, tags="board")
            None
    
    def _draw_hover(self, col):
        self.canvas.delete("hover")
        if self.game_active and self._dropping:
            pass; cs = self.CELL_SIZE; pad = 10; cx = pad + col * cs + cs // 2; cy = pad + cs // 2; radius = cs // 2 - 6; color = self.current_player == 1 and "#ffd740"; self.canvas.create_oval(cx - radius, cy - radius - cs, cx + radius, cy + radius - cs, fill=color, outline="", stipple="gray50", tags="hover")
    
    def _on_click(self, event):
        if self.game_active and self._dropping or self.online_waiting:
            pass
        if self.mode_var.get() == "online" and self.online_role != self.current_player:
            pass; pad = 10; col = ((event.x) - pad) // (self.CELL_SIZE)
        if col < 0 or col >= self.COLS:
            pass
        
        if self.mode_var.get() == "online" and self.client:
            self.client.send_message({"action": "drop", "col": col}); self._drop_piece(col)
    
    def _on_hover(self, event):
        pad = 10; col = ((event.x) - pad) // (self.CELL_SIZE)
        if 0 <= col or col < self.COLS:
            pass
        else:
            return None
        self._draw_hover(col)
    
    def _drop_piece(self, col):
        target_row = -1
        for r in range((self.ROWS) - 1, -1, -1):
            target_row = self.board[r][col] == 0 or r
            None
        if target_row == -1:
            pass; self._dropping = True; self._animate_drop(col, 0, target_row)
    
    def _animate_drop(self, col, current_row, target_row):
        cs = self.CELL_SIZE; pad = 10
        if current_row > 0:
            cx = pad + col * cs + cs // 2
            cy = pad + (current_row - 1) * cs + cs // 2
            radius = cs // 2 - 6
            colors = self.theme.colors
        
        self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=colors["bg_darkest"], outline="#0d1042", width=2, tags="board")
        
        if current_row <= target_row:
            cx = pad + col * cs + cs // 2
            cy = pad + current_row * cs + cs // 2
            radius = cs // 2 - 6
            color = self.current_player == 1 and "#ffd740"
            outline = self.current_player == 1 and "#f9a825"
            self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, fill=color, outline=outline, width=2, tags="board")
            if current_row < target_row:
                self._anim_id = self.after(50, (lambda: self._animate_drop(col, current_row + 1, target_row)))
        self.board[target_row][col] = self.current_player
        
        self._dropping = False
        
        self.sounds.play("drop"); winner = self._check_winner(target_row, col)
        if winner:
            self._handle_win(winner)
        if all((self.board[0][c] != 0 for c in range(self.COLS))):
            self._handle_draw()
        
        self.current_player = 3 - (self.current_player)
        if self.mode_var.get() == "online":
            role_text = self.online_role == 1 and "Yellow"
            if self.current_player == 1:
                self.status_label.configure(text=f"You are {role_text}. 🔴 Red's turn", fg="#ef5350")
            else:
                self.status_label.configure(text=f"You are {role_text}. 🟡 Yellow's turn", fg="#ffd740")
        
        elif self.current_player == 1:
            self.status_label.configure(text="🔴 Red's turn", fg="#ef5350")
        else:
            self.status_label.configure(text="🟡 Yellow's turn", fg="#ffd740")
        if self.vs_ai:
            if self.current_player == 2:
                self.after(400, self._ai_move)
            return None
    
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
            self.status_label.configure(text=f"Hosting... Code: {code}", fg=colors["gold"])
            self.copy_btn.pack(side=tk.LEFT, padx=10)
            self._connect_client(ip, self.server.port)
        except:
            pass
    
    def _copy_code(self):
        if self.current_room_code:
            self.clipboard_clear()
            self.clipboard_append(self.current_room_code)
            colors = self.theme.colors
            self.status_label.configure(text="Code copied to clipboard!", fg=colors["success"])
            self.after(2000, (lambda: self.status_label.configure(text=f"Hosting... Code: {self.current_room_code}", fg=colors["gold"])))
    
    def _join_game(self):
        from tkinter import simpledialog; colors = self.theme.colors; code = simpledialog.askstring("Join Game", "Enter Room Code:", parent=self)
        if not code:
            pass; ip, port = decode_connection(code)
        if not ip:
            self.status_label.configure(text="Invalid Code!", fg=colors["error"]); self.status_label.configure(text=f"Connecting to {code}...", fg=colors["text_secondary"]); self._connect_client(ip, port)
    
    def _connect_client(self, ip, port):
        self.client = RelayClient(ip, port, on_message=self._on_net_message_raw)
        if not self.client.connect():
            self.status_label.configure(text="Connection failed!", fg=self.theme.colors["error"])
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
        if not self.winfo_exists():
            pass; action = message.get("action"); colors = self.theme.colors
        if action == "assign":
            if message["player"] == "p1":
                pass
            self.online_role = 2
            self.online_waiting = True
        if action == "waiting":
            self.status_label.configure(text=f"Code: {encode_connection(get_local_ip(), self.server.port)} - Waiting for opponent...", fg=colors["gold"])
        
        if action == "start":
            self.online_waiting = False
            self.start_game()
            role_text = self.online_role == 1 and "Yellow"
            self.status_label.configure(text=f"Game Started! You are {role_text}. 🔴 Red's turn", fg="#ef5350")
            if self.server:
                pass
            self.hub.achievements.check_and_unlock("multi_host", "multi_join")
        if action == "drop":
            col = message["col"]
            self._drop_piece(col)
        if action == "opponent_disconnected":
            self.game_active = False
            self.status_label.configure(text="Opponent disconnected!", fg=colors["error"])
            self._disconnect_multiplayer()
        if action == "error":
            self.status_label.configure(text=message["message"], fg=colors["error"])
    
    def _ai_move(self):
        if not self.game_active:
            pass
        for c in range(self.COLS):
            r = self._get_drop_row(c)
            if not r >= 0:
                pass
            self.board[r][c] = 2
            if self._check_winner(r, c):
                self.board[r][c] = 0
                self._drop_piece(c)
                None
            return None
            self.board[r][c] = 0
        for c in range(self.COLS):
            r = self._get_drop_row(c)
            if not r >= 0:
                pass
            self.board[r][c] = 1
            if self._check_winner(r, c):
                self.board[r][c] = 0
                self._drop_piece(c)
                None
            return None
            self.board[r][c] = 0
        preferences = [3, 2, 4, 1, 5, 0, 6]
        for c in preferences:
            if not self.board[0][c] == 0:
                pass
            self._drop_piece(c)
            None
            return None
    
    def _get_drop_row(self, col):
        for r in range((self.ROWS) - 1, -1, -1):
            if not self.board[r][col] == 0:
                pass
            None
        
        return r
        
        return -1
    
    def _check_winner(self, row, col):
        player = self.board[row][col]
        if player == 0:
            pass; directions = [(0, 1), (1, 0), (1, 1), (1, -1)]
        for dr, dc in directions:
            count = 1
            winning_cells = [(row, col)]
            for i in range(1, 4):
                c = col + dc * i
                r = row + dr * i
                if 0 <= r or r < self.ROWS:
                    pass
                
            if 0 <= c or c < self.COLS:
                pass
            
        while self.board[r][c] == player:
            count += 1
            winning_cells.append((r, c))
        None
        for i in range(1, 4):
            c = col - dc * i
            r = row - dr * i
            if 0 <= r or r < self.ROWS:
                pass
            
        if 0 <= c:
            while c < self.COLS:
                pass
        
        while self.board[r][c] == player:
            count += 1
            winning_cells.append((r, c))
        None
        while not count >= 4:
            pass
        self._winning_cells = winning_cells
        return player
    
    def _handle_win(self, winner):
        self.game_active = False; colors = self.theme.colors; cs = self.CELL_SIZE; pad = 10
        for r, c in self._winning_cells:
            cx = pad + c * cs + cs // 2
            cy = pad + r * cs + cs // 2
            radius = cs // 2 - 3
            self.canvas.create_oval(cx - radius, cy - radius, cx + radius, cy + radius, outline=colors["success"], width=4, tags="win")
        if winner == 1:
            self.p1_wins += 1
            self.status_label.configure(text="🔴 Red wins! 🎉", fg=colors["success"])
            if self.vs_ai and winner == 1:
                pass
            self.on_win(achievement_id="c4_first")
        else:
            self.p2_wins += 1
            self.status_label.configure(text="🟡 Yellow wins! 🎉", fg=colors["success"])
            if self.vs_ai:
                self.on_lose()
            else:
                self.on_win(achievement_id="c4_first")
        
        self._update_scores()
        
        cx = pad + cs * (self.COLS) // 2; cy = pad + cs * (self.ROWS) // 2; self.particles.emit_confetti(cx, cy, count=40); self._animate_particles()
    
    def _handle_draw(self):
        self.game_active = False; self.draws += 1; colors = self.theme.colors; self.status_label.configure(text="Draw!", fg=colors["warning"]); self._update_scores(); self.on_draw()
    
    def _update_scores(self):
        self.p1_label.configure(text=f"🔴 Red: {self.p1_wins}"); self.p2_label.configure(text=f"🟡 Yellow: {self.p2_wins}"); self.draw_label.configure(text=f"Draw: {self.draws}")
    
    def _animate_particles(self):
        if self.particles.is_active:
            self.particles.update()
            self._anim_id = self.after(33, self._animate_particles)
