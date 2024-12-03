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
        self.turn_notified = []  # Lista de banderas para cada jugador
        self.game_started = False
        self.game_over = False  # Nueva bandera para indicar si el juego terminó

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
            try:
                client_socket.send(message.encode())
            except (ConnectionAbortedError, BrokenPipeError):
                print("Error al enviar mensaje a un cliente.")

    def broadcast_board(self):
        board_data = pickle.dumps(self.board)  # Serialize the board
        for client_socket, _ in self.clients:
            try:
                client_socket.send(board_data)
            except (ConnectionAbortedError, BrokenPipeError):
                print("Error al enviar el tablero a un cliente.")

    def pass_turn(self):
        if not self.game_over:  # Solo cambia el turno si el juego no ha terminado
            self.current_turn = (self.current_turn + 1) % len(self.clients)
            self.turn_notified = [False] * len(self.clients)  # Reinicia notificaciones para el siguiente turno

    def remove_client(self, client_socket):
        for i, (sock, _) in enumerate(self.clients):
            if sock == client_socket:
                self.clients.pop(i)
                if self.current_turn >= len(self.clients):
                    self.current_turn = 0  # Ajustar el turno si el jugador eliminado era el último
                break
        client_socket.close()

    def handle_client(self, client_socket, player_id):
        try:
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
                self.broadcast_board()  # Enviar el tablero inicial
                self.turn_notified = [False] * self.num_players  # Inicializa notificaciones

            # Ciclo principal del juego
            while True:
                if self.game_over:
                    break  # Si el juego ha terminado, termina el ciclo

                if player_id == self.current_turn:
                    # Es el turno del cliente actual
                    client_socket.send("Es tu turno. Da las coordenadas (número, letra): ".encode())
                    try:
                        mensaje = client_socket.recv(1024).decode().strip()
                        fila, columna = self.parse_coordinates(mensaje)

                        # Verificar que las coordenadas estén dentro de los límites
                        if fila < 0 or fila >= len(self.board) or columna < 0 or columna >= len(self.board[0]):
                            client_socket.send("Coordenadas fuera de los límites. Intenta nuevamente.".encode())
                            continue  # Vuelve a pedir las coordenadas

                        if (fila, columna) in self.mines:
                            # Caso: El cliente pisa una mina
                            # Primero, enviamos el mensaje que el juego terminó
                            for mine_row, mine_col in self.mines:
                                self.board[mine_row][mine_col] = "X"  # Revelar todas las minas
                            
                            # Enviar el mensaje de que se pisó una mina a todos los clientes
                            self.broadcast("¡Un jugador ha pisado una mina! Juego terminado.")
                            self.broadcast_board()  # Enviar el tablero actualizado con las minas reveladas

                            # Imprimir en el servidor la mina que fue pisada
                            print(f"Jugador {player_id + 1} pisó la mina en ({fila + 1}, {chr(columna + 65)})")
                            
                            self.game_over = True  # Marcar el juego como terminado
                             # Enviar mensaje de despedida antes de cerrar conexiones
                            time.sleep(1)  # Dar tiempo a los clientes para recibir los mensajes
                            self.broadcast("¡Gracias por jugar!")  # Mensaje final opcional
                            return  # Termina el juego
                        else:
                            # Actualiza el tablero
                            self.board[fila][columna] = "0"  # Marca la celda como jugada
                            self.broadcast_board()  # Envía el tablero actualizado

                            # Imprimir el movimiento del jugador en el servidor
                            print(f"Jugador {player_id + 1} movió a la celda ({fila + 1}, {chr(columna + 65)})")

                            self.pass_turn()  # Cambia el turno al siguiente jugador
                    except ValueError:
                        client_socket.send("Coordenadas inválidas. Intenta nuevamente.".encode())
                else:
                    # No es el turno de este cliente
                    if not self.turn_notified[player_id]:
                        try:
                            client_socket.send("No es tu turno".encode())
                            self.turn_notified[player_id] = True  # Marca como notificado
                        except Exception as e:
                            print(f"Error al enviar mensaje 'No es tu turno': {e}")

        except (ConnectionResetError, ConnectionAbortedError):
            print(f"Jugador {player_id + 1} desconectado.")
        finally:
            self.remove_client(client_socket)


    def parse_coordinates(self, mensaje):
        fila, columna = mensaje.split(",")
        return int(fila.strip()) - 1, ord(columna.strip().upper()) - 65  # Ajuste de índices para que empiece desde 0

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
