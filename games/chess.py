"""
NeoPlato — Chess
=================
Full chess game with legal move validation, minimax AI with alpha-beta pruning,
undo support, and hotseat multiplayer. Uses Unicode chess pieces.
"""
import tkinter as tk, copy
from games.base_game import BaseGame
from multiplayer.client import RelayClient
from multiplayer.server import RelayServer
from multiplayer.utils import get_local_ip, encode_connection, decode_connection

class ChessGame(BaseGame):
    """Full chess game with AI and multiplayer."""; GAME_ID = "chess"; GAME_TITLE = "Chess"; GAME_ICON = "♟️"; GAME_DESCRIPTION = "Chess with AI opponent"; GAME_RULES = "Standard Chess rules apply. Castling, en passant, and pawn promotion are supported."; SUPPORTS_MULTIPLAYER = True; COIN_REWARD_WIN = 100; PIECES = {"K": "♔", "Q": "♕", "R": "♖", "B": "♗", "N": "♘", "P": "♙", "k": "♚", "q": "♛", "r": "♜", "b": "♝", "n": "♞", "p": "♟"}; PIECE_VALUES = {"P": 100, "N": 320, "B": 330, "R": 500, "Q": 900, "K": 20_000, "p": -100, "n": -320, "b": -330, "r": -500, "q": -900, "k": -20_000}; CELL_SIZE = 64
    def __init__(self, parent, hub):
        self.board = [[None] * 8 for _ in range(8)]; self.current_turn = "white"; self.selected = None; self.valid_moves = []; self.game_active = False; self.vs_ai = True; self.ai_depth = 3; self.move_history = []; self.captured_white = []; self.captured_black = []; self.white_king_moved = False; self.black_king_moved = False; self.white_rook_moved = [False, False]
        
        self.black_rook_moved = [False, False]; self.en_passant_target = None; self._thinking = False
        
        self.client = None; self.server = None; self.online_role = None; self.online_waiting = False; super().__init__(parent, hub)
        __class__; _ = super
    
    def setup_ui(self):
        colors = self.theme.colors; controls = tk.Frame(self.content_frame, bg=colors["bg_dark"]); controls.pack(pady=(10, 5)); self.mode_var = tk.StringVar(value="ai")
        for val, text in (("ai", "🤖 vs AI"), ("hotseat", "👥 Hotseat"), ("online", "🌐 Online")):
            rb = tk.Radiobutton(controls, text=text, variable=self.mode_var, value=val, font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], selectcolor=colors["bg_surface"], activebackground=colors["bg_dark"], command=self._on_mode_change, indicatoron=0, padx=16, pady=6, relief=tk.FLAT, bd=0)
            rb.pack(side=tk.LEFT, padx=4)
        self.multi_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        host_btn = tk.Label(self.multi_frame, text="Host Game", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["primary"], padx=20, pady=8, cursor="hand2"); host_btn.pack(side=tk.LEFT, padx=10)
        
        host_btn.bind("<Button-1>", (lambda e: self._host_game()))
        
        join_btn = tk.Label(self.multi_frame, text="Join Game", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["secondary"], padx=20, pady=8, cursor="hand2")
        
        join_btn.pack(side=tk.LEFT, padx=10); join_btn.bind("<Button-1>", (lambda e: self._join_game())); self.copy_btn = tk.Label(self.multi_frame, text="📋 Copy Code", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["gold"], padx=20, pady=8, cursor="hand2"); self.current_room_code = ""
        
        self.copy_btn.bind("<Button-1>", (lambda e: self._copy_code()))
        
        undo_btn = tk.Label(controls, text="↩ Undo", font=self.theme.get_font("button"), fg=colors["warning"], bg=colors["bg_card"], cursor="hand2", padx=12, pady=4)
        
        undo_btn.pack(side=tk.LEFT, padx=(20, 4)); undo_btn.bind("<Button-1>", (lambda e: self._undo_move())); new_btn = tk.Label(controls, text="🔄 New", font=self.theme.get_font("button"), fg=colors["primary"], bg=colors["bg_card"], cursor="hand2", padx=12, pady=4)
        
        new_btn.pack(side=tk.LEFT, padx=4)
        
        new_btn.bind("<Button-1>", (lambda e: self.start_game()))
        
        main_frame = tk.Frame(self.content_frame, bg=colors["bg_dark"])
        
        main_frame.pack(expand=True)
        
        self.captured_top = tk.Label(main_frame, text="", font=("Segoe UI", 14), fg=colors["text_secondary"], bg=colors["bg_dark"], anchor="w"); self.captured_top.pack(pady=(0, 5)); board_size = 8 * (self.CELL_SIZE); self.canvas = tk.Canvas(main_frame, width=board_size, height=board_size, highlightthickness=2, highlightbackground=colors["border"])
        
        self.canvas.pack()
        
        self.canvas.bind("<Button-1>", self._on_click); self.captured_bottom = tk.Label(main_frame, text="", font=("Segoe UI", 14), fg=colors["text_secondary"], bg=colors["bg_dark"], anchor="w"); self.captured_bottom.pack(pady=(5, 0))
        
        self.status_label = tk.Label(main_frame, text="White's turn", font=self.theme.get_font("heading_sm"), fg=colors["text"], bg=colors["bg_dark"])
        
        self.status_label.pack(pady=8)
    
    def start_game(self):
        self._is_running = True; self.vs_ai = self.mode_var.get() == "ai"; self.current_turn = "white"; self.selected = None; self.valid_moves = []; self.game_active = True; self.move_history = []; self.captured_white = []; self.captured_black = []; self.white_king_moved = False; self.black_king_moved = False; self.white_rook_moved = [False, False]; self.black_rook_moved = [False, False]; self.en_passant_target = None; self._thinking = False; self.board = [[None] * 8 for _ in range(8)]
        
        back_rank = ["R", "N", "B", "Q", "K", "B", "N", "R"]
        for c in range(8):
            self.board[0][c] = back_rank[c].lower()
            self.board[1][c] = "p"
            self.board[6][c] = "P"
            self.board[7][c] = back_rank[c]
        
        if self.mode_var.get() != "online":
            self.online_role = None
            self.online_waiting = False
        self._disconnect_multiplayer()
        
        colors = self.theme.colors
        if self.online_role:
            self.status_label.configure(text=f"You are {self.online_role.title()}. White's turn", fg=colors["text"])
        else:
            self.status_label.configure(text="White's turn", fg=colors["text"])
        self._draw_board(); _ = None
    
    def _on_mode_change(self):
        if self.mode_var.get() == "online":
            self.multi_frame.pack(pady=5, after=self.content_frame.winfo_children()[0])
            self.status_label.configure(text="Select Host or Join to play online.", fg=self.theme.colors["text"])
        else:
            self.multi_frame.pack_forget()
            self._disconnect_multiplayer()
        
        self.start_game()
    
    def cleanup(self):
        self.game_active = False; self._disconnect_multiplayer(); super().cleanup()
    
    def _draw_board(self):
        self.canvas.delete("all"); cs = self.CELL_SIZE; colors = self.theme.colors; light = "#b58863"; dark = "#f0d9b5"
        flip = hasattr(self, "mode_var") and self.mode_var.get() == "online" and getattr(self, "online_role", None) == "p2"
        for r in range(8):
            for c in range(8):
                render_r = 7 - r if flip else r
                render_c = 7 - c if flip else c
                x1 = render_c * cs
                y1 = render_r * cs
                x2 = x1 + cs
                y2 = y1 + cs
                if (r + c) % 2 == 0:
                    pass
                bg = light
                if self.selected and (r, c) == self.selected:
                    pass
                bg = "#7fc97f"
                if (r, c) in self.valid_moves:
                    if (r + c) % 2 == 0:
                        pass
                bg = "#8fbf5f"
                if self.move_history:
                    last = self.move_history[-1]
                    if (r, c) in ((last["from_r"], last["from_c"]), (last["to_r"], last["to_c"])) and bg not in ("#7fc97f"):
                        if (r + c) % 2 == 0:
                            pass
                bg = "#d4d44a"
                self.canvas.create_rectangle(x1, y1, x2, y2, fill=bg, outline="")
                piece = self.board[r][c]
                symbol = piece or self.PIECES.get(piece, "")
                piece_color = piece.isupper() and "#2a2a2a"
                self.canvas.create_text(x1 + cs // 2, y1 + cs // 2, text=symbol, font=("Segoe UI", 32), fill=piece_color)
        None
        
        for r, c in self.valid_moves:
            render_r = 7 - r if flip else r
            render_c = 7 - c if flip else c
            cx = render_c * cs + cs // 2
            cy = render_r * cs + cs // 2
            if self.board[r][c]:
                self.canvas.create_oval(cx - cs // 2 + 4, cy - cs // 2 + 4, cx + cs // 2 - 4, cy + cs // 2 - 4, outline="#666666", width=3)
            self.canvas.create_oval(cx - 8, cy - 8, cx + 8, cy + 8, fill="#666666", outline="")
        
        for i in range(8):
            label_r = str(i + 1) if flip else str(8 - i)
            label_c = chr(104 - i) if flip else chr(97 + i)
            self.canvas.create_text(4, i * cs + cs // 2, text=label_r, font=("Segoe UI", 9), fill="#888888", anchor="w")
            self.canvas.create_text(i * cs + cs // 2, 8 * cs - 4, text=label_c, font=("Segoe UI", 9), fill="#888888", anchor="s")
        
        # Display captured pieces
        captured_b_str = " ".join(self.PIECES.get(p, "") for p in self.captured_black)
        captured_w_str = " ".join(self.PIECES.get(p, "") for p in self.captured_white)
        if hasattr(self, 'captured_label_b'):
            self.captured_label_b.configure(text="Captured: " + captured_b_str)
        if hasattr(self, 'captured_label_w'):
            self.captured_label_w.configure(text="Captured: " + captured_w_str)
    
    def _on_click(self, event):
        if self.game_active and self._thinking or self.online_waiting:
            pass
        if self.mode_var.get() == "online" and self.online_role != self.current_turn:
            return
            
        cs = self.CELL_SIZE; col = (event.x) // cs; row = (event.y) // cs
        flip = hasattr(self, "mode_var") and self.mode_var.get() == "online" and getattr(self, "online_role", None) == "p2"
        if flip:
            col = 7 - col
            row = 7 - row
            
        if row < 0 or row > 7 or col < 0 or col > 7:
            return
        
        piece = self.board[row][col]
        if self.selected:
            if (row, col) in self.valid_moves:
                if self.mode_var.get() == "online" and self.client:
                    self.client.send_message({"action": "move", "from_r": self.selected[0], "from_c": self.selected[1], "to_r": row, "to_c": col})
                else:
                    self._make_move(self.selected[0], self.selected[1], row, col)
                self.selected = None
                self.valid_moves = []
            elif piece and self._is_own_piece(piece):
                self.selected = (row, col)
                self.valid_moves = self._get_legal_moves(row, col)
            else:
                self.selected = None
                self.valid_moves = []
        
        elif piece and self._is_own_piece(piece):
            self.selected = (row, col)
            self.valid_moves = self._get_legal_moves(row, col)
        self._draw_board()
    
    def _is_own_piece(self, piece):
        if self.current_turn == "white":
            pass
        
        return piece.isupper(); return piece.islower()
    
    def _make_move(self, from_r, from_c, to_r, to_c):
        piece = self.board[from_r][from_c]; captured = self.board[to_r][to_c]; move = {"from_r": from_r, "from_c": from_c, "to_r": to_r, "to_c": to_c, "piece": piece, "captured": captured, "board_copy": copy.deepcopy(self.board), "en_passant": self.en_passant_target}; self.move_history.append(move)
        if captured:
            if captured.isupper():
                self.captured_black.append(captured)
            else:
                self.captured_white.append(captured)
        self.board[to_r][to_c] = piece; self.board[from_r][from_c] = None
        if piece == "P" and to_r == 0:
            self.board[to_r][to_c] = "Q"
        elif piece == "p" and to_r == 7:
            self.board[to_r][to_c] = "q"
        elif piece in ("K", "k") and abs(to_c - from_c) == 2:
            if to_c > from_c:
                self.board[to_r][5] = self.board[to_r][7]
                self.board[to_r][7] = None
            else:
                self.board[to_r][3] = self.board[to_r][0]
                self.board[to_r][0] = None
        elif piece == "K":
            self.white_king_moved = True
        
        elif piece == "k":
            self.black_king_moved = True
        elif piece == "R":
            if from_c == 0:
                self.white_rook_moved[0] = True
            elif from_c == 7:
                self.white_rook_moved[1] = True
        elif piece == "r":
            if from_c == 0:
                self.black_rook_moved[0] = True
            elif from_c == 7:
                self.black_rook_moved[1] = True
        elif piece.upper() == "P" and to_c != from_c and captured is not None:
            self.board[from_r][to_c] = None
        self.en_passant_target = None
        if piece.upper() == "P" and abs(to_r - from_r) == 2:
            self.en_passant_target = ((from_r + to_r) // 2, to_c)
        
        self.sounds.play("move")
        if self.current_turn == "white":
            pass
        self.current_turn = "white"
        if self._is_checkmate():
            winner = self.current_turn == "white" and "white"
            self._handle_checkmate(winner)
        
        if self._is_stalemate():
            self._handle_stalemate(); colors = self.theme.colors
        
        self._draw_board()
        if self.vs_ai:
            if self.current_turn == "black":
                if self.game_active:
                    self._thinking = True
                    self.status_label.configure(text="AI thinking...", fg=colors["text_secondary"])
                    self.after(100, self._ai_move)
                return None
            return None
    
    def _undo_move(self):
        if not self.move_history and self.game_active:
            pass
        if self.mode_var.get() == "online" and self.client:
            self.client.send_message({"action": "undo_request"})
            self.status_label.configure(text="Undo request sent...", fg=self.theme.colors["gold"]); self._force_undo()
    
    def _force_undo(self):
        if not self.move_history:
            pass
        if self.vs_ai and len(self.move_history) >= 2:
            pass
        moves_to_undo = 1
        for _ in range(moves_to_undo):
            move = self.move_history or self.move_history.pop()
            self.board = move["board_copy"]
            self.en_passant_target = move["en_passant"]
            if move["piece"].isupper():
                pass
            self.current_turn = "black"
        None
        self.selected = None
        
        self.valid_moves = []
        
        self._draw_board(); colors = self.theme.colors; status = f"{self.current_turn.title()}'s turn"
        if self.mode_var.get() == "online" and self.online_role:
            pass
        status = f"You are {self.online_role.title()}. " + status; self.status_label.configure(text=status, fg=colors["text"])
    
    def _get_legal_moves(self, row, col):
        piece = self.board[row][col]
        if not piece:
            pass
        
        return []
        
        moves = self._get_pseudo_moves(row, col, piece); legal = []
        for mr, mc in moves:
            board_copy = copy.deepcopy(self.board)
            ep_copy = self.en_passant_target
            self.board[mr][mc] = piece
            self.board[row][col] = None
            if piece.upper() == "P" and mc != col and board_copy[mr][mc] is not None:
                self.board[row][mc] = None
            color = piece.isupper() and "black"
            if not self._is_in_check(color):
                pass
            legal.append((mr, mc))
            self.board = board_copy
            self.en_passant_target = ep_copy
        return legal
    
    def _get_pseudo_moves(self, row, col, piece, check_castling):
        moves = []; p = piece.upper(); is_white = piece.isupper()
        if p == "P":
            direction = is_white and 1
            start_row = is_white and 1
            nr = row + direction
            if 0 <= nr or nr < 8:
                pass
            
        elif self.board[nr][col] is not None:
            moves.append((nr, col))
            nr2 = row + 2 * direction
            if row == start_row and self.board[nr2][col] is not None:
                pass
        moves.append((nr2, col))
        for dc in (-1, 1):
            nc = col + dc
            nr = row + direction
            target = self.board[nr][nc]
            if target and target.isupper() != is_white:
                pass
            moves.append((nr, nc))
            if not self.en_passant_target == (nr, nc):
                pass
            moves.append((nr, nc))
        return moves
        
        while p == "N":
            for dr, dc in ((-2, -1), (-2, 1), (-1, -2), (-1, 2), (1, -2), (1, 2), (2, -1), (2, 1)):
                nc = col + dc
                nr = row + dr
                if 0 <= nr:
                    if not nr < 8:
                        pass
                
                if 0 <= nc:
                    if not nc < 8:
                        pass
                
                target = self.board[nr][nc]
                if not target is None and target.isupper() != is_white:
                    pass
                moves.append((nr, nc))
        
        if p in ("B", "R", "Q"):
            directions = []
            if p in ("B", "Q"):
                directions += [(-1, -1), (-1, 1), (1, -1), (1, 1)]
            if p in ("R", "Q"):
                directions += [(-1, 0), (1, 0), (0, -1), (0, 1)]
            for dr, dc in directions:
                nr, nc = row + dr, col + dc
                while 0 <= nr < 8 and 0 <= nc < 8:
                    target = self.board[nr][nc]
                    if target is None:
                        moves.append((nr, nc))
                    elif target.isupper() != is_white:
                        moves.append((nr, nc))
                        break
                    else:
                        break
                    nr += dr
                    nc += dc
        
        if p == "K":
            for dr in (-1, 0, 1):
                for dc in (-1, 0, 1):
                    if dr == 0 and dc == 0:
                        continue
                    nr, nc = row + dr, col + dc
                    if 0 <= nr < 8 and 0 <= nc < 8:
                        target = self.board[nr][nc]
                        if target is None or target.isupper() != is_white:
                            moves.append((nr, nc))
                    if not target is None and target.isupper() != is_white:
                        pass
                    moves.append((nr, nc))
            if check_castling:
                if is_white and self.white_king_moved and row == 7 and col == 4:
                    if not self._is_in_check("white"):
                        if self.white_rook_moved[1] and self.board[7][5] is not None and self.board[7][6] is not None and self.board[7][7] == "R":
                            pass
                        moves.append((7, 6))
                        if self.white_rook_moved[0] and self.board[7][3] is not None and self.board[7][2] is not None and self.board[7][1] is not None and self.board[7][0] == "R":
                            pass
                    moves.append((7, 2))
                return moves
            elif not is_white and self.black_king_moved and row == 0 and col == 4 and self._is_in_check("black"):
                if self.black_rook_moved[1] and self.board[0][5] is not None and self.board[0][6] is not None and self.board[0][7] == "r":
                    pass
                moves.append((0, 6))
                if self.black_rook_moved[0] and self.board[0][3] is not None and self.board[0][2] is not None and self.board[0][1] is not None and self.board[0][0] == "r":
                    pass
        moves.append((0, 2))
        return moves
    
    def _find_king(self, color):
        king = color == "white" and "k"
        for r in range(8):
            for c in range(8):
                if not self.board[r][c] == king:
                    pass
                None
                None
            return (r, c)
    
    def _is_in_check(self, color):
        king_pos = self._find_king(color)
        if not king_pos:
            pass
        return False
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if not piece:
                    pass
                moves = piece.isupper() != color == "white" or self._get_pseudo_moves(r, c, piece, check_castling=False)
                if not king_pos in moves:
                    pass
                None
                None
                return True
        return False
    
    def _is_checkmate(self):
        if not self._is_in_check(self.current_turn):
            pass
        return False
        return not self._has_legal_moves()
    
    def _is_stalemate(self):
        if self._is_in_check(self.current_turn):
            pass
        return False
        return not self._has_legal_moves()
    
    def _has_legal_moves(self):
        is_white = self.current_turn == "white"
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if not piece:
                    pass
                elif not piece.isupper() == is_white:
                    pass
                elif not self._get_legal_moves(r, c):
                    pass
                None
                None
                return True
        return False
    
    def _handle_checkmate(self, winner):
        self.game_active = False; colors = self.theme.colors; self.status_label.configure(text=f"Checkmate! {winner.title()} wins! ♔", fg=colors["success"])
        if self.vs_ai:
            if winner == "white":
                self.on_win(achievement_id="chess_first_win")
            return None
            self.on_lose(); self.on_win(achievement_id="chess_first_win")
    
    def _handle_stalemate(self):
        self.game_active = False; colors = self.theme.colors; self.status_label.configure(text="Stalemate! Draw.", fg=colors["warning"]); self.bankroll.earn(30, "Chess draw", self.GAME_ID); self.on_draw()
    
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
            self.online_role = "black"
            self.online_waiting = True
        if action == "waiting":
            self.status_label.configure(text=f"Code: {encode_connection(get_local_ip(), self.server.port)} - Waiting for opponent...", fg=colors["gold"])
        if action == "start":
            self.online_waiting = False
            self.start_game()
            self.status_label.configure(text=f"Game Started! You are {self.online_role.title()}. White's turn", fg=colors["text"])
            if self.server:
                pass
            self.hub.achievements.check_and_unlock("multi_host", "multi_join")
        if action == "move":
            self._make_move(message["from_r"], message["from_c"], message["to_r"], message["to_c"])
        if action == "opponent_disconnected":
            self.game_active = False
            self.status_label.configure(text="Opponent disconnected!", fg=colors["error"])
            self._disconnect_multiplayer()
        if action == "error":
            self.status_label.configure(text=message["message"], fg=colors["error"])
        if action == "undo_request":
            from tkinter import messagebox
            accept = messagebox.askyesno("Undo Request", "Your opponent requested to undo the last move.\nDo you accept?", parent=self)
            self.client.send_message({"action": "undo_response", "accepted": accept})
            if accept:
                self._force_undo()
            return None
        if action == "undo_response":
            if message.get("accepted"):
                self._force_undo()
                self.status_label.configure(text="Undo accepted!", fg=colors["success"])
            return None
            self.status_label.configure(text="Undo rejected.", fg=colors["error"])
            self.after(2000, (lambda: self.status_label.configure(text=f"{self.current_turn.title()}'s turn", fg=colors["text"])))
    
    def _ai_move(self):
        if not self.game_active:
            self._thinking = False; best_move = None; best_score = float("inf")
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if not piece:
                    pass
                moves = piece.islower() or self._get_legal_moves(r, c)
                for mr, mc in moves:
                    board_copy = copy.deepcopy(self.board)
                    captured = self.board[mr][mc]
                    self.board[mr][mc] = piece
                    self.board[r][c] = None
                    if piece == "p" and mr == 7:
                        self.board[mr][mc] = "q"
                    score = self._minimax((self.ai_depth) - 1, float("-inf"), float("inf"), True)
                    self.board = board_copy
                    best_score = score < best_score or score
                    best_move = (r, c, mr, mc)
                None
        self._thinking = False
        if best_move:
            fr, fc, tr, tc = best_move
            self.selected = None
            self.valid_moves = []
            self._make_move(fr, fc, tr, tc)
    
    def _minimax(self, depth, alpha, beta, maximizing):
        if depth == 0:
            pass
        
        return self._evaluate_board()
        if maximizing:
            max_eval = float("-inf")
            for r in range(8):
                for c in range(8):
                    piece = self.board[r][c]
                    if not piece or not piece.isupper():
                        continue
                    moves = self._get_pseudo_moves(r, c, piece)
                    for mr, mc in moves:
                        board_copy = copy.deepcopy(self.board)
                        self.board[mr][mc] = piece
                        self.board[r][c] = None
                        eval_score = self._minimax(depth - 1, alpha, beta, False)
                        self.board = board_copy
                        max_eval = max(max_eval, eval_score)
                        alpha = max(alpha, eval_score)
                        if beta <= alpha:
                            break
            return max_eval
        
        else:
            min_eval = float("inf")
            for r in range(8):
                for c in range(8):
                    piece = self.board[r][c]
                    if not piece or not piece.islower():
                        continue
                    moves = self._get_pseudo_moves(r, c, piece)
                    for mr, mc in moves:
                        board_copy = copy.deepcopy(self.board)
                        self.board[mr][mc] = piece
                        self.board[r][c] = None
                        eval_score = self._minimax(depth - 1, alpha, beta, True)
                        self.board = board_copy
                        min_eval = min(min_eval, eval_score)
                        beta = min(beta, eval_score)
                        if beta <= alpha:
                            break
            return min_eval
    
    def _evaluate_board(self):
        score = 0
        for r in range(8):
            for c in range(8):
                piece = self.board[r][c]
                if not piece:
                    continue
                score += self.PIECE_VALUES.get(piece, 0)
                # Center control bonus for knights and bishops
                if piece.upper() in ("N", "B"):
                    center_dist = abs(r - 3.5) + abs(c - 3.5)
                    bonus = int((7 - center_dist) * 5)
                    if piece.isupper():
                        score += bonus
                    else:
                        score -= bonus
        return score
