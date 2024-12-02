import socket
import pickle

def imprimir_tablero(tablero):
    columnas = "   " + " ".join([chr(65 + i) for i in range(len(tablero[0]))])
    print(columnas)
    for i, fila in enumerate(tablero):
        print(f"{i + 1:<2} " + " ".join(fila))

def convertir_coordenadas(entrada):
    entrada = entrada.strip().replace("(", "").replace(")", "").split(',')
    fila_numero = int(entrada[0].strip())
    columna_letra = entrada[1].strip().upper()
    fila = fila_numero - 1
    columna = ord(columna_letra) - 65
    return fila, columna

def recibir_datos(cliente):
    datos = bytearray()
    while True:
        parte = cliente.recv(4096)
        if not parte:
            break
        datos.extend(parte)
    return datos

def jugar():
    ip = "192.168.1.78"
    puerto = 54321
    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip, puerto))

    # Verificar si es el primer jugador (jugador 0)
    es_primer_jugador = cliente.recv(1024).decode()

    if es_primer_jugador == "0":
        # Si es el primer jugador, preguntar la dificultad y tamaño del POOL
        dificultad = input("Elige la dificultad (principiante/avanzado): ").lower()
        cliente.send(dificultad.encode())

        pool_size = input("Introduce el tamaño del POOL (número de jugadores): ").strip()
        cliente.send(pool_size.encode())
    else:
        # Si no es el primer jugador, recibir la dificultad del servidor
        dificultad = cliente.recv(1024).decode()
        print(f"Dificultad recibida del servidor: {dificultad}")

    # Recibir confirmación del servidor
    confirmacion = cliente.recv(1024).decode()
    print(confirmacion)

    # Recibir y mostrar el tablero
    if dificultad == "principiante":
        tablero = [['_' for _ in range(9)] for _ in range(9)]
    else:
        tablero = [['_' for _ in range(16)] for _ in range(16)]
    imprimir_tablero(tablero)

    # Esperar hasta que sea el turno
    while True:
        cliente.send("Es tu turno".encode())
        coordenada = input("Ingresa las coordenadas (ejemplo: (3, A)): ")
        fila, columna = convertir_coordenadas(coordenada)

        cliente.send(pickle.dumps((fila, columna)))
        respuesta = cliente.recv(1024).decode()

        if respuesta == "mina pisada":
            datos_tablero = recibir_datos(cliente)
            try:
                tablero = pickle.loads(datos_tablero)  # Intentar deserializar
                imprimir_tablero(tablero)
                print("¡Has pisado una mina!")
                break
            except pickle.UnpicklingError as e:
                print(f"Error al deserializar el tablero: {e}")
                break  # Si falla la deserialización, terminar el juego
        elif respuesta == "casilla libre":
            datos_tablero = recibir_datos(cliente)
            try:
                tablero = pickle.loads(datos_tablero)  # Intentar deserializar
                imprimir_tablero(tablero)
            except pickle.UnpicklingError as e:
                print(f"Error al deserializar el tablero: {e}")
                break  # Si falla la deserialización, terminar el juego
        elif respuesta == "ganaste":
            print("¡Felicidades, ganaste!")
            break
    cliente.close()

if __name__ == "__main__":
    jugar()
