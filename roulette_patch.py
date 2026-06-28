import tkinter as tk
from tkinter import simpledialog, messagebox
import socket
import threading
import json
import math
import random
import time

import games.roulette
from multiplayer.client import RelayClient
from multiplayer.utils import get_local_ip, encode_connection, decode_connection

class RouletteServer:
    def __init__(self, host="0.0.0.0", port=0):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients = []
        self.max_players = 10
        self._accept_thread = None

    def start(self):
        self.server_socket.bind((self.host, self.port))
        self.port = self.server_socket.getsockname()[1]
        self.server_socket.listen(self.max_players)
        print(f"[ROULETTE SERVER] Listening on {self.host}:{self.port}")
        self._accept_thread = threading.Thread(target=self._accept_loop, daemon=True)
        self._accept_thread.start()

    def _accept_loop(self):
        while True:
            try:
                client_socket, addr = self.server_socket.accept()
                if len(self.clients) >= self.max_players:
                    client_socket.close()
                    continue
                
                client_id = f"p{len(self.clients) + 1}"
                self.clients.append((client_socket, client_id))
                
                # Assign role
                self._send(client_socket, {"action": "assign", "player": client_id})
                
                # If host, allow start
                if len(self.clients) == 1:
                    self._send(client_socket, {"action": "start"})
                
                thread = threading.Thread(target=self._handle_client, args=(client_socket, client_id), daemon=True)
                thread.start()
            except OSError:
                break

    def _handle_client(self, client_socket, role):
        try:
            while True:
                data = client_socket.recv(4096).decode("utf-8").strip()
                if not data:
                    break
                for line in data.split("\n"):
                    if not line: continue
                    try:
                        msg = json.loads(line)
                        msg["sender_role"] = role
                        self._broadcast(msg, exclude=client_socket)
                    except Exception as e:
                        print(f"Error relaying: {e}")
        except Exception:
            pass
        finally:
            self._remove_client(client_socket, role)

    def _remove_client(self, client_socket, role):
        self.clients = [c for c in self.clients if c[0] != client_socket]
        self._broadcast({"action": "player_left", "player": role})
        try:
            client_socket.close()
        except:
            pass

    def _broadcast(self, message, exclude=None):
        data = json.dumps(message) + "\n"
        bdata = data.encode("utf-8")
        for sock, _ in self.clients:
            if sock != exclude:
                try:
                    sock.sendall(bdata)
                except:
                    pass

    def _send(self, client_socket, message):
        try:
            data = json.dumps(message) + "\n"
            client_socket.sendall(data.encode("utf-8"))
        except:
            pass

    def shutdown(self):
        try:
            for sock, _ in self.clients:
                sock.close()
            self.server_socket.close()
        except:
            pass

class AdvancedRouletteGame(games.roulette.RouletteGame):
    def __init__(self, parent, hub):
        self.pnl_data = {}
        self.active_players = {}
        self.total_rounds = 0
        self.current_round = 0
        self.my_name = hub.storage.get_setting("player_name", "Player")
        super().__init__(parent, hub)

    def setup_ui(self):
        super().setup_ui()
        
        # Add Round selector to multi_frame
        colors = self.theme.colors
        self.rounds_var = tk.StringVar(value="25")
        self.rounds_menu = tk.OptionMenu(self.multi_frame, self.rounds_var, "25", "50", "Custom")
        self.rounds_menu.config(font=self.theme.get_font("button"), bg=colors["bg_card"], fg=colors["text"], highlightthickness=0)
        self.rounds_menu.pack(side=tk.LEFT, padx=5)
        
        # Add Active Players sidebar
        left_frame = self.wheel_canvas.master
        main_frame = left_frame.master
        self.players_frame = tk.Frame(main_frame, bg=colors["bg_dark"], width=150)
        self.players_frame.pack(side=tk.LEFT, fill=tk.Y, padx=10, before=left_frame)
        tk.Label(self.players_frame, text="Active Players", font=self.theme.get_font("heading_sm"), fg=colors["text"], bg=colors["bg_dark"]).pack(pady=5)
        self.players_list_lbl = tk.Label(self.players_frame, text="", font=self.theme.get_font("body"), fg=colors["text_secondary"], bg=colors["bg_dark"], justify=tk.LEFT)
        self.players_list_lbl.pack(anchor="w", pady=5)
        
        self.rounds_lbl = tk.Label(self.content_frame, text="", font=self.theme.get_font("heading_sm"), fg=colors["gold"], bg=colors["bg_dark"])
        self.rounds_lbl.pack(pady=5, before=main_frame)
        
    def _host_game(self):
        self._disconnect_multiplayer()
        colors = self.theme.colors
        try:
            self.server = RouletteServer()
            self.server.start()
            
            ip = get_local_ip()
            port = self.server.port
            self.current_room_code = encode_connection(ip, port)
            
            self.client = RelayClient("127.0.0.1", port, self._on_net_message_raw)
            if not self.client.connect():
                self.multi_status.configure(text="Failed to start.", fg=colors["error"])
                self.client = None
                return
            self.online_waiting = True
            self.multi_status.configure(text="Hosting...", fg=colors["success"])
            
            # Lock rounds selection
            self.rounds_menu.configure(state="disabled")
            
            if self.rounds_var.get() == "Custom":
                val = simpledialog.askinteger("Custom Rounds", "Enter number of rounds:", parent=self, minvalue=1, maxvalue=1000)
                if not val: val = 25
                self.total_rounds = val
            else:
                self.total_rounds = int(self.rounds_var.get())
                
            self.current_round = 0
            
        except Exception as e:
            self.multi_status.configure(text="Host failed.", fg=colors["error"])
            print(e)
            
    def _join_game(self):
        self._disconnect_multiplayer()
        colors = self.theme.colors
        code = simpledialog.askstring("Join Game", "Enter room code:", parent=self)
        if not code:
            return
        ip, port = decode_connection(code.strip())
        if not ip:
            self.multi_status.configure(text="Invalid code.", fg=colors["error"])
            return
            
        if ip == get_local_ip():
            ip = "127.0.0.1"
            
        self.client = RelayClient(ip, port, self._on_net_message_raw)
        if not self.client.connect():
            self.multi_status.configure(text="Failed to connect.", fg=colors["error"])
            self.client = None
        else:
            self.online_waiting = True
            self.current_room_code = code.strip()
            self.multi_status.configure(text="Connecting...", fg=colors["gold"])

    def _on_net_message_raw(self, message):
        self.after(0, lambda: self._process_net_message(message))

    def _process_net_message(self, msg):
        if not self.client:
            return
            
        action = msg.get("action")
        colors = self.theme.colors
        
        if action == "assign":
            self.online_role = msg["player"]
            my_code = self.hub.storage.get_player_id()
            self.active_players[self.online_role] = f"{self.my_name} #{my_code}"
            self.pnl_data[self.online_role] = {"name": self.my_name, "invested": 0, "won": 0}
            self.client.send_message({"action": "player_info", "name": self.my_name, "code": my_code})
            if self.online_role == "p1":
                self.multi_status.configure(text=f"Host (Code: {self.current_room_code})", fg=colors["success"])
                # Ensure copy button is visible for host
                self.copy_btn.pack(side=tk.LEFT, padx=10, before=self.multi_status)
            else:
                self.multi_status.configure(text="Connected to Host", fg=colors["success"])
            self._update_players_ui()
                
        elif action == "player_info":
            sender = msg["sender_role"]
            code = msg.get("code", "")
            display_name = f"{msg['name']} #{code}" if code else msg['name']
            self.active_players[sender] = display_name
            if sender not in self.pnl_data:
                self.pnl_data[sender] = {"name": display_name, "invested": 0, "won": 0}
            else:
                self.pnl_data[sender]["name"] = display_name
            self._update_players_ui()
            # If host, send back total rounds config, current state, and full player list
            if self.online_role == "p1":
                self.client.send_message({
                    "action": "sync_state", 
                    "rounds": self.total_rounds, 
                    "curr": self.current_round,
                    "players": self.active_players
                })
                
        elif action == "sync_state":
            self.total_rounds = msg["rounds"]
            self.current_round = msg["curr"]
            if "players" in msg:
                for role, name in msg["players"].items():
                    if role not in self.active_players:
                        self.active_players[role] = name
                        self.pnl_data[role] = {"name": name, "invested": 0, "won": 0}
            self._update_players_ui()
            
        elif action == "player_left":
            p = msg["player"]
            if p in self.active_players:
                if not hasattr(self, "inactive_players"):
                    self.inactive_players = set()
                self.inactive_players.add(p)
                self._update_players_ui()
                
        elif action == "spin":
            self.spinning = True
            
            # Client locks their local bet
            if self.online_role != "p1":
                try:
                    num_val = self.num_var.get().strip()
                    if num_val and num_val.isdigit():
                        self.bet_number = int(num_val)
                        if 0 <= self.bet_number <= 36:
                            self.bet_type = "number"
                    else:
                        self.bet_type = self.bet_type_var.get()
                        
                    amt = int(self.bet_var.get())
                    if amt > 0 and self.bankroll.can_afford(amt):
                        self.bet_amount = amt
                        self.bankroll.spend(self.bet_amount, f"Roulette bet ({self.bet_type})", self.GAME_ID)
                        self._update_balance()
                        if self.client:
                            self.client.send_message({"action": "bet_placed", "amount": self.bet_amount})
                            self.pnl_data[self.online_role]["invested"] += self.bet_amount
                except ValueError:
                    self.bet_amount = 0
            
            self.result = msg["result"]
            target = 360 * 5 + msg["angle"]
            self._spin_step(0, target)
            self.current_round += 1
            self._update_players_ui()
            
        elif action == "bet_placed":
            sender = msg["sender_role"]
            if sender not in self.pnl_data:
                self.pnl_data[sender] = {"name": self.active_players.get(sender, sender), "invested": 0, "won": 0}
            self.pnl_data[sender]["invested"] += msg["amount"]
            
        elif action == "bet_won":
            sender = msg["sender_role"]
            if sender not in self.pnl_data:
                self.pnl_data[sender] = {"name": self.active_players.get(sender, sender), "invested": 0, "won": 0}
            self.pnl_data[sender]["won"] += msg["amount"]
            
    def _update_players_ui(self):
        if self.mode_var.get() != "online":
            self.players_list_lbl.configure(text="")
            self.rounds_lbl.configure(text="")
            return
            
        if not hasattr(self, "inactive_players"):
            self.inactive_players = set()
            
        txt = ""
        for role, name in self.active_players.items():
            if role in self.inactive_players:
                prefix = "🔴 "
            else:
                prefix = "⭐ " if role == "p1" else "👤 "
            me = " (You)" if role == self.online_role else ""
            txt += f"{prefix}{name}{me}\n"
        self.players_list_lbl.configure(text=txt)
        
        if self.total_rounds > 0:
            self.rounds_lbl.configure(text=f"Round {self.current_round}/{self.total_rounds}")
            
    def _spin(self):
        if self.spinning: return
        
        if self.mode_var.get() == "online":
            if self.online_role != "p1":
                self.result_label.configure(text="Only the Host can spin!", fg=self.theme.colors["error"])
                return
            if self.current_round >= self.total_rounds:
                self._show_pnl_dashboard()
                return

        # Place local bet
        try:
            num_val = self.num_var.get().strip()
            if num_val and num_val.isdigit():
                self.bet_number = int(num_val)
                if 0 <= self.bet_number <= 36:
                    self.bet_type = "number"
            else:
                self.bet_type = self.bet_type_var.get()
                
            self.bet_amount = int(self.bet_var.get())
            if self.bet_amount <= 0: return
            if not self.bankroll.can_afford(self.bet_amount):
                self.result_label.configure(text="Not enough NeoCoins!", fg=self.theme.colors["error"])
                return
                
            self.bankroll.spend(self.bet_amount, f"Roulette bet ({self.bet_type})", self.GAME_ID)
            self._update_balance()
            
            if self.mode_var.get() == "online" and self.client:
                self.client.send_message({"action": "bet_placed", "amount": self.bet_amount})
                self.pnl_data[self.online_role]["invested"] += self.bet_amount
                
        except ValueError:
            return
            
        self.spinning = True
        self.result = random.randint(0, 36)
        
        # Calculate angle for result
        order = [0, 32, 15, 19, 4, 21, 2, 25, 17, 34, 6, 27, 13, 36, 11, 30, 8, 23, 10, 5, 24, 16, 33, 1, 20, 14, 31, 9, 22, 18, 29, 7, 28, 12, 35, 3, 26]
        idx = order.index(self.result)
        slot_angle = 360 / len(order)
        # Random offset within the slot
        offset = random.uniform(2, slot_angle - 2)
        angle = (90 - (idx * slot_angle + offset)) % 360
        
        if self.mode_var.get() == "online" and self.client:
            self.client.send_message({"action": "spin", "result": self.result, "angle": angle})
            
        target = 360 * 5 + angle
        self._spin_step(0, target)
        
        if self.mode_var.get() == "online":
            self.current_round += 1
            self._update_players_ui()

    def _on_spin_complete(self):
        super()._on_spin_complete()
        
        won = self._check_win(self.result)
        if won:
            payout = self.PAYOUTS.get(self.bet_type, 2)
            winnings = self.bet_amount * payout
            if self.mode_var.get() == "online" and self.client:
                self.client.send_message({"action": "bet_won", "amount": winnings})
                
        if self.mode_var.get() == "online" and self.current_round >= self.total_rounds:
            self.after(2000, self._show_pnl_dashboard)
            
    def _show_pnl_dashboard(self):
        colors = self.theme.colors
        popup = tk.Toplevel(self)
        popup.title("Game Over - PnL Dashboard")
        popup.geometry("600x400")
        popup.configure(bg=colors["bg_card"])
        popup.transient(self.winfo_toplevel())
        popup.grab_set()
        
        tk.Label(popup, text="🏆 Roulette Match Results 🏆", font=self.theme.get_font("heading"), fg=colors["gold"], bg=colors["bg_card"]).pack(pady=20)
        
        frame = tk.Frame(popup, bg=colors["bg_dark"])
        frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
        
        # Headers
        tk.Label(frame, text="Player", font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], width=15).grid(row=0, column=0, pady=5)
        tk.Label(frame, text="Invested", font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], width=10).grid(row=0, column=1)
        tk.Label(frame, text="Won", font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], width=10).grid(row=0, column=2)
        tk.Label(frame, text="Profit/Loss", font=self.theme.get_font("body_bold"), fg=colors["text"], bg=colors["bg_dark"], width=15).grid(row=0, column=3)
        
        row = 1
        for p_role, data in self.pnl_data.items():
            inv = data["invested"]
            won = data["won"]
            pnl = won - inv
            pnl_color = colors["success"] if pnl > 0 else (colors["error"] if pnl < 0 else colors["text_muted"])
            pnl_str = f"+{pnl}" if pnl > 0 else str(pnl)
            
            tk.Label(frame, text=data["name"], font=self.theme.get_font("body"), fg=colors["primary"], bg=colors["bg_dark"], width=15).grid(row=row, column=0, pady=2)
            tk.Label(frame, text=str(inv), font=self.theme.get_font("mono"), fg=colors["text_secondary"], bg=colors["bg_dark"], width=10).grid(row=row, column=1)
            tk.Label(frame, text=str(won), font=self.theme.get_font("mono"), fg=colors["text_secondary"], bg=colors["bg_dark"], width=10).grid(row=row, column=2)
            tk.Label(frame, text=pnl_str, font=self.theme.get_font("mono"), fg=pnl_color, bg=colors["bg_dark"], width=15).grid(row=row, column=3)
            row += 1
            
        btn = tk.Label(popup, text="Close", font=self.theme.get_font("button"), fg=colors["bg_dark"], bg=colors["primary"], padx=20, pady=10, cursor="hand2")
        btn.pack(pady=10)
        btn.bind("<Button-1>", lambda e: popup.destroy())
