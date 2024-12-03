# P3_multijugador
# Buscaminas Multijugador en Python

## Descripción

Este proyecto implementa una versión multijugador del clásico juego de **Buscaminas** utilizando **sockets TCP** en **Python**. El servidor maneja la lógica del juego y los clientes interactúan con el tablero, haciendo jugadas hasta que un jugador pisa una mina, lo que termina el juego.

## Características

- **Servidor**:
  - Genera y gestiona el tablero con minas.
  - Controla el turno de los jugadores.
  - Envía mensajes de estado y actualizaciones del tablero a todos los clientes.
  - Termina el juego cuando un jugador pisa una mina.
  
- **Cliente**:
  - Permite a los jugadores seleccionar casillas y enviar sus jugadas al servidor.
  - Recibe actualizaciones del tablero y notificaciones del estado del juego.

## Requisitos

- Python 3.8 o superior.
- Librerías estándar de Python:
  - `socket`
  - `threading`
  - `pickle`
  - `random`
  - `time`

## Instalación

1. Clona este repositorio:
   ```bash
   git clone https://github.com/tu_usuario/buscaminas-multijugador.git
   cd buscaminas-multijugador
## Ejecución

### Servidor

1. Abre el archivo `servidor.py`.
2. Configura la IP y puerto del servidor en las variables `host` y `port`.
3. Ejecuta el servidor:
    `python servidor.py`
### Cliente
1. Abre el archivo `cliente.py`.
2. Configura la IP y puerto del servidor en las variables `ip` y `puerto`.
3. Ejecuta el cliente:
    `python cliente.py`
## Estructura del Proyecto

### `servidor.py`

**Descripción**: Este archivo contiene la lógica del servidor, que gestiona el tablero, el flujo del juego y la comunicación con los clientes.

#### Funciones principales:

- **`generate_board(difficulty)`**: Genera el tablero con las minas, dependiendo de la dificultad seleccionada.
- **`broadcast(message)`**: Envía un mensaje a todos los clientes conectados.
- **`broadcast_board()`**: Serializa y envía el tablero actualizado a todos los clientes.
- **`handle_client(client_socket, player_id)`**: Maneja la interacción con cada cliente durante el juego.
- **`pass_turn()`**: Pasa el turno al siguiente jugador.
- **`remove_client(client_socket)`**: Elimina un cliente desconectado.
- **`start()`**: Inicia el servidor y acepta conexiones de los clientes.

### `cliente.py`

**Descripción**: Este archivo contiene la lógica del cliente, que interactúa con el servidor para hacer jugadas y recibir actualizaciones del tablero.

#### Funciones principales:

- **`imprimir_tablero(tablero)`**: Muestra el tablero en la consola.
- **`convertir_coordenadas(entrada)`**: Convierte las coordenadas ingresadas por el jugador en índices de fila y columna.
- **`jugar()`**: Gestiona el ciclo principal del cliente, incluyendo la recepción de mensajes del servidor y el envío de jugadas.

---

## Flujo del Juego

1. **Conexión**:
    
    - El servidor espera que los jugadores se conecten y configura el juego.
    - Los jugadores deben elegir la dificultad y el número de jugadores.
2. **Inicio del juego**:
    
    - El servidor genera el tablero con minas y lo distribuye a los clientes.
    - Los jugadores se turnan para hacer jugadas. Se les solicita ingresar coordenadas para seleccionar una casilla.
3. **Fin del juego**:
    
    - Si un jugador selecciona una mina, el juego termina y se muestra un mensaje a todos los jugadores.
    - El tablero se actualiza y se revela la ubicación de las minas.
