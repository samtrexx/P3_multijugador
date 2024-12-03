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

