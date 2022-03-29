# -*- coding: utf-8 -*-
from email import header
import socket
import sys
import json
from utilities import *


if __name__ == "__main__":
  buff_size = 1024
  address = ('localhost', 8888)

  # armamos el socket
  # los parámetros que recibe el socket indican el tipo de conexión
  client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

  # asociamos el socket a la dirección definida
  client_socket.bind(address)
  client_socket.listen(3)

  while True:

      # cuando llega una petición de conexión la aceptamos
      # y sacamos los datos de la conexión entrante (objeto, dirección)
      client_connection, _ = client_socket.accept()

      # luego recibimos y parseamos el mensaje usando la función que programamos
      received_request = receive_and_parse_http_message(client_connection, buff_size, 'request')

      # Guardamos el host
      host = received_request.headers["Host"]
      # print(host)

      try:
        # Si recibimos un archivo json por consola leemos sus contenido
        # y lo parseamos, de no resultar arrojamos un error.
        f = open(sys.argv[1])
        config = json.load(f)
        f.close()

      except:
        print("Error when trying to read config file")

      else:

        if received_request.start_line['resource'] in config['blocked']:
          
          body = "<h1>Error 403, Blocked address</h1>"

          response = create_http_msg(HTTPMessage(
            message_type='response',
            start_line={'http_version':received_request.start_line['http_version'],
                        'status_code':'403',
                        'status_text':'Blocked address'},
            headers={'Content-Length':str(len(body.encode()))},
            body=body
          ))
          response = response.encode()
          client_connection.send(response)
        
        else:

          # Agregamos nuestro correo a los headers del request
          received_request.headers["X-ElQuePregunta"] = config["user"]

          # Lo transformamos nuevamente a formato http
          received_request = create_http_msg(received_request)

          # Y lo redireccionamos al servidor, para lo cual primero es necesario crear un socket
          # y asociarlo al host recibido en el request

          server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
          server_socket.connect((host, 80))

          received_request = (received_request).encode()
          server_socket.send(received_request)

          received_response = receive_and_parse_http_message(server_socket, buff_size, 'response')

          received_response.redact(config['forbidden_words'])

          received_response = create_http_msg(received_response)
          received_response = (received_response).encode()
          client_connection.send(received_response)
          # cerramos la conexión
          # notar que la dirección que se imprime indica un número de puerto distinto al 8888

          # seguimos esperando por si llegan otras conexiones

          server_socket.close()

        client_connection.close()
