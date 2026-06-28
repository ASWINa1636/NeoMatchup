"""
NeoPlato — Tic-Tac-Toe
========================
Beautiful animated Tic-Tac-Toe with hotseat multiplayer and AI opponent.
Features animated X/O drawing, win line animation, and particle celebrations.
"""
import tkinter as tk, random, math
from games.base_game import BaseGame
from core.animations import ParticleSystem
from multiplayer.client import RelayClient
from multiplayer.server import RelayServer
from multiplayer.utils import get_local_ip, encode_connection, decode_connection

class TicTacToeGame(BaseGame):
    """Tic-Tac-Toe with animations and AI."""; GAME_ID = "tictactoe"; GAME_TITLE = "Tic-Tac-Toe"; GAME_ICON = "❌"; GAME_DESCRIPTION = "Classic Tic-Tac-Toe with animations"; GAME_RULES = "Take turns placing your X or O on the 3x3 grid.\n\nThe first player to get 3 of their marks in a row (up, down, across, or diagonally) wins!"; SUPPORTS_MULTIPLAYER = True; COIN_REWARD_WIN = 15
    def __init__(self, parent, hub):
        for _ in range(3):
            []
        _ = None; self.board; self.current_player = "X"; self.game_over = False; self.vs_ai = False; self.x_wins = 0; self.o_wins = 0; self.draws = 0; self._anim_id = None; self._ai_thinking = False; self.client = None
        
        self.server = None; self.online_role = None; self.online_waiting = False
        
        super().__init__(parent, hub)
        __class__
        
        _ = super; _ = None
    
    def setup_ui(self):
        colors = self.theme.colors; mode_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); mode_frame.pack(pady=(15, 5)); self.mode_var = tk.StringVar(value="ai")
        for val, text in (("ai", "🤖 vs AI"), ("hotseat", "👥 Hotseat"), ("online", "🌐 Online")):
            rb = tk.Radiobutton(mode_frame, text=text, variable=self.mode_var, value=val, font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], selectcolor=colors["bg_surface"], activebackground=colors["bg_dark"], activeforeground=colors["primary"], command=self._on_mode_change, indicatoron=0, padx=20, pady=8, relief=tk.FLAT, bd=0, highlightbackground=colors["border"])
            rb.pack(side=tk.LEFT, padx=5)
        self
        self.multi_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        host_btn = tk.Label(self.multi_frame, text="Host Game", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["primary"], padx=20, pady=8, cursor="hand2")
        
        host_btn.pack(side=tk.LEFT, padx=10); host_btn.bind("<Button-1>", (lambda e: self._host_game()))
        
        join_btn = tk.Label(self.multi_frame, text="Join Game", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["secondary"], padx=20, pady=8, cursor="hand2"); join_btn.pack(side=tk.LEFT, padx=10); join_btn.bind("<Button-1>", (lambda e: self._join_game()))
        
        self.copy_btn = tk.Label(self.multi_frame, text="📋 Copy Code", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["gold"], padx=20, pady=8, cursor="hand2"); self.current_room_code = ""
        
        self.copy_btn.bind("<Button-1>", (lambda e: self._copy_code())); canvas_size = 420; self.cell_size = canvas_size // 3
        
        canvas_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"]); canvas_frame.pack(expand=True)
        
        self.canvas = tk.Canvas(canvas_frame, width=canvas_size, height=canvas_size, bg=colors["bg_surface"], highlightthickness=0)
        
        self.canvas.pack(padx=20, pady=10); self.canvas.bind("<Button-1>", self._on_click); self.particles = ParticleSystem(self.canvas)
        
        status_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        status_frame.pack(pady=5)
        
        self.status_label = tk.Label(status_frame, text="X's turn", font=self.theme.get_font("heading_sm"), fg=colors["primary"], bg=colors["bg_dark"])
        
        self.status_label.pack()
        
        score_frame = tk.Frame(self.content_frame, bg=colors["bg_surface"], padx=20, pady=10); score_frame.pack(pady=10); self.score_x_label = tk.Label(score_frame, text="X: 0", font=self.theme.get_font("body_bold"), fg=colors["accent"], bg=colors["bg_surface"])
        
        self.score_x_label.pack(side=tk.LEFT, padx=15)
        
        self.score_draw_label = tk.Label(score_frame, text="Draw: 0", font=self.theme.get_font("body_bold"), fg=colors["text_secondary"], bg=colors["bg_surface"])
        
        self.score_draw_label.pack(side=tk.LEFT, padx=15)
        
        self.score_o_label = tk.Label(score_frame, text="O: 0", font=self.theme.get_font("body_bold"), fg=colors["secondary"], bg=colors["bg_surface"]); self.score_o_label.pack(side=tk.LEFT, padx=15)
        
        new_btn = tk.Label(self.content_frame, text="🔄 New Game", font=self.theme.get_font("button"), fg=colors["primary"], bg=colors["bg_card"], padx=20, pady=8, cursor="hand2"); new_btn.pack(pady=10)
        
        new_btn.bind("<Button-1>", (lambda e: self.start_game()))
    
    def start_game(self):
        for _ in range(3):
            []
        _ = None; self.board; self.current_player = "X"; self.game_over = False; self.vs_ai = self.mode_var.get() == "ai"; self._ai_thinking = False; self._is_running = True
        if self.mode_var.get() != "online":
            self.online_role = None
            self.online_waiting = False
        self._disconnect_multiplayer()
        
        colors = self.theme.colors
        
        if self.online_role:
            self.status_label.configure(text=f"You are {self.online_role}. X's turn", fg=colors["primary"])
        
        else:
            self.status_label.configure(text="X's turn", fg=colors["primary"])
        
        self.particles.clear(); self._draw_board(); _ = None; _ = None
    
    def cleanup(self):
        if self._anim_id:
            self.after_cancel(self._anim_id)
            self._anim_id = None
        self._disconnect_multiplayer(); super().cleanup()
    
    def _draw_board(self):
        self.canvas.delete("all"); colors = self.theme.colors; cs = self.cell_size
        for i in range(1, 3):
            x = i * cs
            self.canvas.create_line(x, 10, x, cs * 3 - 10, fill=colors["border_light"], width=3)
            y = i * cs
            self.canvas.create_line(10, y, cs * 3 - 10, y, fill=colors["border_light"], width=3)
        for r in range(3):
            for c in range(3):
                if not self.board[r][c]:
                    pass
                self._draw_piece(r, c, self.board[r][c], animated=False)
            None
    
    def _draw_piece(self, row, col, piece, animated):
        colors = self.theme.colors; cs = self.cell_size; cx = col * cs + cs // 2; cy = row * cs + cs // 2; pad = 25
        if piece == "X":
            color = colors["accent"]
            if animated:
                self._animate_x(cx, cy, pad, color)
            return None
            self.canvas.create_line(cx - pad, cy - pad, cx + pad, cy + pad, fill=color, width=4, capstyle=tk.ROUND)
            self.canvas.create_line(cx + pad, cy - pad, cx - pad, cy + pad, fill=color, width=4, capstyle=tk.ROUND); color = colors["secondary"]
        if animated:
            self._animate_o(cx, cy, pad, color); self.canvas.create_oval(cx - pad, cy - pad, cx + pad, cy + pad, outline=color, width=4)
    
    def _animate_x(self, cx, cy, pad, color, step):
        tag1 = f"anim_x1_{cx}_{cy}"; tag2 = f"anim_x2_{cx}_{cy}"
        if step <= 10:
            t = step / 10
            y1 = cy - pad
            x1 = cx - pad
            x2 = x1 + 2 * pad * t
            y2 = y1 + 2 * pad * t
            self.canvas.delete(tag1)
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=4, capstyle=tk.ROUND, tags=tag1)
            self.after(20, (lambda: self._animate_x(cx, cy, pad, color, step + 1)))
        if step <= 20:
            t = (step - 10) / 10
            y1 = cy - pad
            x1 = cx + pad
            x2 = x1 - 2 * pad * t
            y2 = y1 + 2 * pad * t
            self.canvas.delete(tag2)
            self.canvas.create_line(x1, y1, x2, y2, fill=color, width=4, capstyle=tk.ROUND, tags=tag2)
            self.after(20, (lambda: self._animate_x(cx, cy, pad, color, step + 1)))
    
    def _animate_o(self, cx, cy, pad, color, step):
        tag = f"anim_o_{cx}_{cy}"
        if step <= 15:
            r = pad * step / 15
            self.canvas.delete(tag)
            if r > 0:
                pass
            self.canvas.create_oval(cx - r, cy - r, cx + r, cy + r, outline=color, width=4, tags=tag)
            self.after(20, (lambda: self._animate_o(cx, cy, pad, color, step + 1)))
    
    def _on_click(self, event):
        if self.game_over and self._is_running and self._ai_thinking or self.online_waiting:
            pass
        if self.mode_var.get() == "online" and self.online_role != self.current_player:
            pass; col = (event.x) // (self.cell_size)
        
        row = (event.y) // (self.cell_size)
        if row < 0 and row > 2 and col < 0 or col > 2:
            pass
        if self.board[row][col]:
            pass
        
        if self.mode_var.get() == "online" and self.client:
            self.client.send_message({"action": "move", "row": row, "col": col}); self._make_move(row, col)
    
    def _make_move(self, row, col):
        self.board[row][col] = self.current_player
        
        self._draw_piece(row, col, self.current_player); self.sounds.play("click"); winner = self._check_winner()
        if winner:
            self._handle_win(winner)
        if self._is_full():
            self._handle_draw()
        if self.current_player == "X":
            pass
        self.current_player = "X"
        
        colors = self.theme.colors; color = colors["secondary"] if self.current_player == "O" else colors["accent"]
        
        if self.vs_ai:
            if self.current_player == "O":
                if not self.game_over:
                    self._ai_thinking = True
                    self.status_label.configure(text="AI thinking...", fg=colors["text_secondary"])
                    self.after(400, self._ai_move)
                return None
            return None
    
    def _on_mode_change(self):
        if self.mode_var.get() == "online":
            self.multi_frame.pack(pady=5)
            self.status_label.configure(text="Select Host or Join to play online.", fg=self.theme.colors["text"])
        else:
            self.multi_frame.pack_forget()
            self._disconnect_multiplayer()
        self.start_game()
    
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
            self.online_role = "O"
            self.online_waiting = True
        if action == "waiting":
            self.status_label.configure(text=f"Code: {encode_connection(get_local_ip(), self.server.port)} - Waiting for opponent...", fg=colors["gold"])
        
        if action == "start":
            self.online_waiting = False
            self.start_game()
            self.status_label.configure(text=f"Game Started! You are {self.online_role}. X's turn", fg=colors["primary"])
            if self.server:
                pass
            self.hub.achievements.check_and_unlock("multi_host", "multi_join")
        if action == "move":
            row = message["row"]
            col = message["col"]
            if self.board[row][col] == "":
                self._make_move(row, col)
            return None
        if action == "game_over":
            pass
        if action == "opponent_disconnected":
            self.game_over = True
            self.status_label.configure(text="Opponent disconnected!", fg=colors["error"])
            self._disconnect_multiplayer()
        
        if action == "error":
            self.status_label.configure(text=message["message"], fg=colors["error"])
    
    def _ai_move(self):
        if self.game_over:
            self._ai_thinking = False; best_score = -math.inf; best_move = None
        for r in range(3):
            for c in range(3):
                if not self.board[r][c] == "":
                    pass
                self.board[r][c] = "O"
                score = self._minimax(self.board, 0, False)
                self.board[r][c] = ""
                best_score = score > best_score or score
                best_move = (r, c)
            None
        self._ai_thinking = False
        if best_move:
            self._make_move(*best_move)
    
    def _minimax(self, board, depth, is_maximizing):
        winner = self._check_winner()
        if winner == "O":
            pass
        
        return 10 - depth
        if winner == "X":
            pass
        
        return depth - 10
        if self._is_full():
            pass
        return 0
        while is_maximizing:
            best = -math.inf
            for r in range(3):
                for c in range(3):
                    if not board[r][c] == "":
                        pass
                    board[r][c] = "O"
                    best = max(best, self._minimax(board, depth + 1, False))
                    board[r][c] = ""
                None
        
        return best
        
        best = math.inf
        for r in range(3):
            for c in range(3):
                if not board[r][c] == "":
                    pass
                board[r][c] = "X"
                best = min(best, self._minimax(board, depth + 1, True))
                board[r][c] = ""
            None
        
        return best
    
    def _check_winner(self):
        b = self.board; lines = []
        for r in range(3):
            lines.append([(r, 0), (r, 1), (r, 2)])
        for c in range(3):
            lines.append([(0, c), (1, c), (2, c)])
        lines.append([(0, 0), (1, 1), (2, 2)]); lines.append([(0, 2), (1, 1), (2, 0)])
        for line in lines:
            for r, c in line:
                pass
            r
            vals = c
            r = None
            c = None
            if not vals[0]:
                pass
            elif vals[0] == vals[1]:
                if not vals[1] == vals[2]:
                    pass
            
            self._winning_line = line
        return vals[0]; c = None; r = None
    
    def _is_full(self):
        return all((self.board[r][c] for c in range(3)))
    
    def _handle_win(self, winner):
        self.game_over = True; colors = self.theme.colors; cs = self.cell_size; line = self._winning_line; r1, c1 = line[0]; r2, c2 = line[2]; x1 = c1 * cs + cs // 2; y1 = r1 * cs + cs // 2; x2 = c2 * cs + cs // 2; y2 = r2 * cs + cs // 2; win_color = colors["success"]; self.canvas.create_line(x1, y1, x2, y2, fill=win_color, width=6, capstyle=tk.ROUND)
        if winner == "X":
            self.x_wins += 1
            self.status_label.configure(text="X wins! 🎉", fg=colors["success"])
            if not self.vs_ai:
                self.on_win(achievement_id="ttt_first_win")
            elif winner == "X":
                pass
            self.on_win(achievement_id="ttt_first_win")
        else:
            self.o_wins += 1
            self.status_label.configure(text="O wins! 🎉", fg=colors["success"])
            if not self.vs_ai:
                self.on_win(achievement_id="ttt_first_win")
            else:
                self.on_lose()
        self._update_scores(); self.particles.emit_confetti(cs * 1.5, cs * 1.5, count=40); self._animate_particles()
    
    def _handle_draw(self):
        self.game_over = True; colors = self.theme.colors; self.draws += 1; self.status_label.configure(text="It's a draw!", fg=colors["warning"]); self._update_scores(); self.on_draw()
    
    def _update_scores(self):
        self.score_x_label.configure(text=f"X: {self.x_wins}"); self.score_o_label.configure(text=f"O: {self.o_wins}"); self.score_draw_label.configure(text=f"Draw: {self.draws}")
    
    def _animate_particles(self):
        if self.particles.is_active:
            self.particles.update()
            self._anim_id = self.after(33, self._animate_particles)
