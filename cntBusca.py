import socket
import pickle

# Función para imprimir el tablero con filas como números y columnas como letras
def imprimir_tablero(tablero):
    columnas = "   " + " ".join([chr(65 + i) for i in range(len(tablero[0]))])  # Imprimir letras para las columnas
    print(columnas)  # Imprimir las letras de las columnas
    for i, fila in enumerate(tablero):
        print(f"{i + 1:<2} " + " ".join(fila))  # Imprimir los números de las filas

# Función para convertir coordenadas en el formato (número, letra) a índices
def convertir_coordenadas(entrada):
    entrada = entrada.strip().replace("(", "").replace(")", "").split(',')
    fila_numero = int(entrada[0].strip())
    columna_letra = entrada[1].strip().upper()
    
    fila = fila_numero - 1  # Restar 1 para convertir a índice basado en 0
    columna = ord(columna_letra) - 65  # Convertir la letra a índice (A=0, B=1, ...)

    return fila, columna

def jugar():
    # Solicitar dirección y puerto del servidor
    ip = "192.168.56.1"  # Cambia a la IP del servidor
    puerto = 54321  # El puerto a utilizar

    # Crear el socket y conectarse al servidor
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip, puerto))

    while True:
        # Esperar mensajes del servidor
        mensaje = cliente.recv(1024).decode()

        if mensaje.startswith("Elige la dificultad"):
            # El primer jugador configura el juego
            print(mensaje)
            dificultad = input("> ").lower()
            cliente.send(dificultad.encode())
        elif mensaje.startswith("Elige el número de jugadores"):
            print(mensaje)
            num_jugadores = input("> ")
            cliente.send(num_jugadores.encode())
        elif mensaje == "Esperando que todos los jugadores se conecten...":
            print(mensaje)
        elif mensaje == "¡El juego ha comenzado!":
            print(mensaje)
            # Recibir el tablero actualizado del servidor
            tablero_serializado = cliente.recv(4096)  # Recibe el tablero serializado
            tablero = pickle.loads(tablero_serializado)  # Deserializa el tablero
            # Imprimir el tablero
            imprimir_tablero(tablero)  # Imprime el tablero con filas y columnas
        elif mensaje == "Es tu turno. Da las coordenadas (número, letra): ":
            print(mensaje)
            coordenadas = input("> ")
            try:
                fila, columna = convertir_coordenadas(coordenadas)
                cliente.send(pickle.dumps((fila, columna)))  # Enviar las coordenadas serializadas
            except ValueError:
                print("Coordenadas inválidas. Intenta nuevamente.")
        elif mensaje == "¡Un jugador ha pisado una mina! Juego terminado.":
            print(mensaje)
            # Recibir y mostrar el tablero actualizado
            datos_tablero = cliente.recv(4096)
            tablero = pickle.loads(datos_tablero)
            imprimir_tablero(tablero)
            break
        elif mensaje.startswith("Tablero actualizado"):
            # Recibir y mostrar el tablero actualizado
            datos_tablero = cliente.recv(4096)
            tablero = pickle.loads(datos_tablero)
            imprimir_tablero(tablero)
        elif mensaje == "¡Felicidades, has ganado!":
            print(mensaje)
            break
        else:
            print(f"Mensaje desconocido: {mensaje}")

    cliente.close()

if __name__ == "__main__":
    jugar()
