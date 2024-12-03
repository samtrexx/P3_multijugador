import socket
import threading
import pickle
import random
import time

class MinesweeperServer:
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen(5)
        self.clients = []
        self.board = []
        self.mines = set()
        self.current_turn = 0
        self.num_players = 0
        self.turn_event = threading.Event()
        self.game_started = False

    def generate_board(self, difficulty):
        if difficulty == "principiante":
            rows, cols, num_mines = 9, 9, 10
        elif difficulty == "avanzado":
            rows, cols, num_mines = 16, 16, 40
        else:
            rows, cols, num_mines = 9, 9, 10  # Default to beginner

        self.board = [['_' for _ in range(cols)] for _ in range(rows)]
        while len(self.mines) < num_mines:
            mine = (random.randint(0, rows - 1), random.randint(0, cols - 1))
            self.mines.add(mine)

    def broadcast(self, message):
        for client_socket, _ in self.clients:
            client_socket.send(message.encode())

    def broadcast_board(self):
        board_data = pickle.dumps(self.board)  # Serialize the board
        for client_socket, _ in self.clients:
            client_socket.send(board_data)  # Send the serialized board

    def pass_turn(self):
        self.current_turn = (self.current_turn + 1) % self.num_players
        self.turn_event.set()

    def handle_client(self, client_socket, player_id):
        if player_id == 0:
            # Primer jugador: configura el juego
            client_socket.send("Elige la dificultad (principiante/avanzado): ".encode())
            difficulty = client_socket.recv(1024).decode()
            self.generate_board(difficulty)

            client_socket.send("Elige el número de jugadores: ".encode())
            self.num_players = int(client_socket.recv(1024).decode())

            self.broadcast("Esperando que todos los jugadores se conecten...")

        # Espera hasta que todos los jugadores se conecten
        while len(self.clients) < self.num_players:
            time.sleep(1)

        if not self.game_started:
            self.broadcast("¡El juego ha comenzado!")
            self.game_started = True
            self.turn_event.set()
            self.broadcast_board()  # Send the board after game starts

        # Ciclo principal del juego para cada jugador
        while True:
            self.turn_event.wait()

            if self.current_turn != player_id:
                continue

            client_socket.send("Es tu turno. Da las coordenadas (número, letra): ".encode())
            try:
                fila, columna = pickle.loads(client_socket.recv(1024))
                print(f"Jugador {player_id + 1} jugó: ({fila}, {columna})")
            except Exception:
                client_socket.send("Error en las coordenadas.".encode())
                continue

            if (fila, columna) in self.mines:
                for mine_row, mine_col in self.mines:
                    self.board[mine_row][mine_col] = "X"
                self.broadcast("¡Un jugador ha pisado una mina! Juego terminado.")
                self.broadcast_board()
                break
            else:
                self.board[fila][columna] = "0"
                client_socket.send("Tablero actualizado".encode())
                self.broadcast_board()

            self.pass_turn()

    def start(self):
        print("Servidor iniciado. Esperando conexiones...")
        while True:
            client_socket, client_address = self.server_socket.accept()
            print(f"Conexión aceptada desde {client_address}")
            player_id = len(self.clients)
            self.clients.append((client_socket, client_address))
            threading.Thread(target=self.handle_client, args=(client_socket, player_id)).start()

if __name__ == "__main__":
    host = "192.168.56.1"  # Cambia a la IP adecuada
    port = 54321
    server = MinesweeperServer(host, port)
    server.start()
