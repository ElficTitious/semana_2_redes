# -*- coding: utf-8 -*-
import socket

def receive_full_message


 
 
def receive_header(connection_socket, buff_size):
    """
    """

    # recibimos la primera parte del mensaje
    buffer = connection_socket.recv(buff_size)
    header = buffer.decode()

    # verificamos si llegó el mensaje completo o si aún faltan partes del mensaje
    is_crlf = contains_end_of_message(header)

    # si el mensaje llegó completo (o sea que contiene la secuencia de fin de mensaje) removemos la secuencia de fin de mensaje
    if is_end_of_message:
        full_message = full_message[0:(len(full_message) - len(end_of_message))]

    # si el mensaje no está completo (no contiene la secuencia de fin de mensaje)
    else:
        # entramos a un while para recibir el resto y seguimos esperando información
        # mientras el buffer no contenga secuencia de fin de mensaje
        while not is_end_of_message:
            # recibimos un nuevo trozo del mensaje
            buffer = connection_socket.recv(buff_size)
            # y lo añadimos al mensaje "completo"
            full_message += buffer.decode()

            # verificamos si es la última parte del mensaje
            is_end_of_message = contains_end_of_message(full_message, end_of_message)
            if is_end_of_message:
                # removemos la secuencia de fin de mensaje
                full_message = full_message[0:(len(full_message) - len(end_of_message))]

    # finalmente retornamos el mensaje
    return full_message


def contains_end_of_message(message):
    if '\r\n\r\n' == message[(len(message) - len('\r\n\r\n')):len(message)]:
        return True
    else:
        return False

buff_size = 64
end_of_message = "\r\n\r\n"
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
    received_message = receive_full_mesage(connection, buff_size, end_of_message)

    print(' -> Se ha recibido el siguiente mensaje: ' + received_message)

    # respondemos
    response_message = ("Mensaje \"{}\" ha sido recibido con éxito".format(received_message)).encode()
    connection.send(response_message)

    # cerramos la conexión
    # notar que la dirección que se imprime indica un número de puerto distinto al 8888
    connection.close()
    print("conexión con " + str(address) + " ha sido cerrada")

    # seguimos esperando por si llegan otras conexiones