import socket
import random
import pickle
import threading
import time

# Variables globales
turno_event = threading.Event()  # Event to manage turn synchronization
turno_event.set()  # Set the first player as the one who can start
jugadores = []  # List to keep track of the players
tablero_global = []
minas_pos = []
dificultad = ""
pool_size = 0

def generar_tablero(dificultad):
    filas, columnas, minas = (9, 9, 10) if dificultad == 'principiante' else (16, 16, 40)
    tablero = [['_' for _ in range(columnas)] for _ in range(filas)]
    minas_pos = set()

    while len(minas_pos) < minas:
        mina_fila = random.randint(0, filas - 1)
        mina_columna = random.randint(0, columnas - 1)
        minas_pos.add((mina_fila, mina_columna))

    return tablero, minas_pos

def manejar_cliente(conexion, direccion, jugador_id):
    global tablero_global, dificultad, pool_size
    print(f"Jugador {jugador_id} conectado desde {direccion}")
    
    # Indicar si es el primer jugador
    if jugador_id == 0:
        conexion.send("0".encode())  # Primer jugador
    else:
        conexion.send("1".encode())  # No es el primer jugador
    
    # El primer jugador configura el juego
    if jugador_id == 0:
        dificultad = conexion.recv(1024).decode().lower()
        conexion.send(f"Seleccionaste dificultad: {dificultad}".encode())
        
        pool_size = int(conexion.recv(1024).decode())
        conexion.send(f"El POOL es de {pool_size} jugadores.".encode())
        
        # Generar el tablero
        tablero_global, minas_pos = generar_tablero(dificultad)
    
    else:
        # El segundo jugador recibe la dificultad del servidor
        conexion.send(dificultad.encode())
    
    # Confirmar que la configuración ha terminado
    conexion.send("Configuración completada. Esperando al siguiente turno.".encode())

    # Esperar hasta que sea el turno del jugador
    turno_event.wait()

    coordenadas_seleccionadas = set()
    conexion.send("Tablero listo. Comienza el juego.".encode())

    inicio = time.time()

    while True:
        try:
            # Intentar recibir los datos correctamente
            data = conexion.recv(4096)
            if not data:
                print(f"Conexión cerrada por el jugador {jugador_id}")
                break  # Si no se reciben datos, cerrar la conexión

            try:
                fila, columna = pickle.loads(data)  # Deserializar los datos

                # Verificar si las coordenadas ya fueron seleccionadas
                if (fila, columna) in coordenadas_seleccionadas:
                    conexion.send("coordenada ya seleccionada".encode())
                    continue  # Continuar esperando nuevas coordenadas

                # Marcar la coordenada como seleccionada
                coordenadas_seleccionadas.add((fila, columna))

                # Verificar si la coordenada pisó una mina
                if (fila, columna) in minas_pos:
                    # Revelar todas las minas
                    for mina_fila, mina_columna in minas_pos:
                        tablero_global[mina_fila][mina_columna] = "1"
                    
                    # Enviar mensaje de que se pisó una mina
                    conexion.send("mina pisada".encode())
                    conexion.send(pickle.dumps(tablero_global))  # Enviar tablero con minas reveladas
                    fin = time.time()
                    duracion = fin - inicio  
                    conexion.send(pickle.dumps(duracion))
                    break  # Terminar el juego

                else:
                    conexion.send("casilla libre".encode())
                    # Actualizar el tablero
                    tablero_global[fila][columna] = "0"
                    conexion.send(pickle.dumps(tablero_global))  # Enviar tablero actualizado

                # Verificar si ha ganado
                if all(tablero_global[fila][columna] != '_' for fila in range(len(tablero_global)) for columna in range(len(tablero_global[0])) if (fila, columna) not in minas_pos):
                    conexion.send("ganaste".encode())
                    break

                # Cambiar de turno
                if jugador_id == len(jugadores) - 1:
                    turno_event.clear()  # Bloquear el turno
                else:
                    jugadores[jugador_id + 1].set()  # Permitir el turno del siguiente jugador

            except pickle.UnpicklingError as e:
                print(f"Error al deserializar los datos: {e}")
                conexion.send("Error al procesar tus coordenadas. Intenta nuevamente.".encode())
                continue  # Volver a esperar por coordenadas válidas

        except Exception as e:
            print(f"Error al recibir los datos del jugador: {e}")
            break  # En caso de error, salir del bucle

    # Calcular y enviar la duración al final
    fin = time.time()
    duracion = fin - inicio
    print(f"Duración del juego: {duracion:.2f} segundos")
    conexion.send(pickle.dumps(duracion))
    conexion.close()

def iniciar_servidor():
    ip = "192.168.1.78"
    puerto = 54321
    servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    servidor.bind((ip, puerto))
    servidor.listen(pool_size)
    print("Esperando conexiones...")

    jugador_id = 0
    while True:
        conexion, direccion = servidor.accept()
        jugador_event = threading.Event()
        jugadores.append(jugador_event)
        threading.Thread(target=manejar_cliente, args=(conexion, direccion, jugador_id)).start()
        jugador_id += 1

if __name__ == "__main__":
    iniciar_servidor()
