import socket
import pickle

def imprimir_tablero(tablero):
    columnas = "   " + " ".join([chr(65 + i) for i in range(len(tablero[0]))])
    print(columnas)
    for i, fila in enumerate(tablero):
        print(f"{i + 1:<2} " + " ".join(fila))

def convertir_coordenadas(entrada):
    entrada = entrada.strip().replace("(", "").replace(")", "").split(',')
    fila_numero = int(entrada[0].strip()) - 1
    columna_letra = entrada[1].strip().upper()
    fila = fila_numero
    columna = ord(columna_letra) - 65
    return fila, columna

def jugar():
    ip = "192.168.56.1"  # Cambia a la IP del servidor
    puerto = 54321

    cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    cliente.connect((ip, puerto))

    while True:
        try:
            # Intentar recibir los primeros 1024 bytes
            mensaje = cliente.recv(1024)
            if not mensaje:  # Verifica si el servidor cerró la conexión
                print("Conexión cerrada por el servidor.")
                break
            # Verificar si es texto o datos serializados
            try:
                mensaje_decodificado = mensaje.decode()  # Intentar decodificar como texto
                if mensaje_decodificado.startswith("¡Un jugador") or mensaje_decodificado.startswith("Tablero"):
                    print(mensaje_decodificado)
                    tablero = pickle.loads(cliente.recv(4096))  # Recibir el tablero serializado
                    imprimir_tablero(tablero)
                elif mensaje_decodificado.startswith("Elige") or mensaje_decodificado.startswith("Es tu turno"):
                    print(mensaje_decodificado)
                    entrada = input("> ")
                    cliente.send(entrada.encode())
                elif mensaje_decodificado == "No es tu turno":
                    print(mensaje_decodificado)
                elif mensaje == "¡Un jugador ha pisado una mina! Juego terminado.":
                    print(mensaje.decode())  # Mostrar el mensaje de fin del juego
                    # Recibir y mostrar el tablero actualizado
                    datos_tablero = cliente.recv(4096)
                    tablero = pickle.loads(datos_tablero)
                    imprimir_tablero(tablero)
                    print("Cerrando conexión...")
                    break  # Termina el juego
                else:
                    print(f"Mensaje desconocido: {mensaje_decodificado}")
            except UnicodeDecodeError:
                # Si no es texto, debe ser un objeto serializado
                tablero = pickle.loads(mensaje)
                imprimir_tablero(tablero)

        except Exception as e:
            print(f"Error en el cliente: {e}")
            break

    cliente.close()

if __name__ == "__main__":
    jugar()
