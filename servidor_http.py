# -*- coding: utf-8 -*-
import socket
from utitlities import *



if __name__ == "__main__":
  buff_size = 64
  address = ('localhost', 8888)

  print('Creando socket - Servidor')
  # armamos el socket
  # los parámetros que recibe el socket indican el tipo de conexión
  server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # lo conectamos al server, en este caso espera mensajes localmente en el puerto 8888
  server_socket.bind(address)

  # hacemos que sea un server socket y le decimos que tenga a lo mas 3 peticiones de conexión encoladas
  # si recibiera una 4ta petición de conexión la va a rechazar
  server_socket.listen(3)

  while True:
      # cuando llega una petición de conexión la aceptamos
      # y sacamos los datos de la conexión entrante (objeto, dirección)
      connection, address = server_socket.accept()

      # luego recibimos el mensaje usando la función que programamos
      # received_message = receive_full_mesage(connection, buff_size, '\r\n\r\n')
      received_message = receive_head(connection, buff_size)

      print(parse_head(received_message, 'request'))

      # respondemos
      response_message = (received_message).encode()
      connection.send(response_message)

      # cerramos la conexión
      # notar que la dirección que se imprime indica un número de puerto distinto al 8888
      connection.close()
      print("conexión con " + str(address) + " ha sido cerrada")

      # seguimos esperando por si llegan otras conexiones