import socket

class InvalidHTTPMessageType(Exception):
  pass
 
def receive_head(connection_socket: socket, buff_size: int) -> str:
    """Funcion que dado un socket y un tamaño de buffer, recibe solo el HEAD de un
    mensaje http.

    Parameters:
      connection_socket (socket): Socket orientado a conexión donde recibir el mensaje http.
      buff_size (int): Tamaño en bytes del buffer donde se va almacenando el mensaje.

    Return:
      (str): HEAD del mensaje http.
    """

    # recibimos la primera parte del mensaje
    buffer = connection_socket.recv(buff_size)
    end_sequence = '\r\n\r\n'
    head = buffer.decode()

    head_is_complete = contains_end_of_message(head, end_sequence)

    # si el HEAD están completos (o sea que contienes la secuencia "\r\n\r\n") removemos 
    # la secuencia de fin de mensaje
    if head_is_complete:
        head = head[0:(len(head) - len("\r\n\r\n"))]

    # si el HEAD no están completos (no contienen la secuencia "\r\n\r\n")
    else:
        # entramos a un while para recibir el resto y seguimos esperando información
        # mientras el buffer no contenga secuencia de fin de mensaje
        while not head_is_complete:
            # recibimos un nuevo trozo del mensaje
            buffer = connection_socket.recv(buff_size)
            # y lo añadimos al HEAD "completo"
            head += buffer.decode()

            # verificamos si es la última parte del HEAD
            head_is_complete = contains_end_of_message(head, end_sequence)
            if head_is_complete:
                # removemos la secuencia de fin de HEAD
                head = head[0:(len(head) - len(end_sequence))]

    # finalmente retornamos el HEAD
    return head

def receive_body(connection_socket: socket, content_length: int, buff_size: int) -> str:
  """Funcion que dado un socket y un tamaño de buffer, recibe un mensaje de
  largo content_length (en bytes) desde el socket (correspondiente al BODY de un
  mensaje http).

  Parameters:
  connection_socket (socket): Socket orientado a conexión donde recibir el mensaje.
  content_length (int): largo en bytes del mensaje a recibir desde el socket.
  buff_size (int): Tamaño en bytes del buffer donde se va almacenando el mensaje.

  Returns:
  (str): Mensaje de largo content_length (en bytes) recibido desde el socket. 
  """
  body: str = ""
  bytes_processed: int = 0
  while bytes_processed < content_length:
    buffer = connection_socket.recv(buff_size)
    bytes_processed += len(buffer)
    body += buffer.decode()
  return body

def parse_head(raw_head: str, message_type: str) -> dict:
  http_msg = {}
  http_msg['message_type'] = message_type
  http_msg['start_line'] = {}
  head_list = raw_head.split('\r\n')
  start_line_list = head_list[0].split(' ')

  if message_type == 'request':
    http_msg['start_line']['method'] = start_line_list[0]
    http_msg['start_line']['resource'] = start_line_list[1]
    http_msg['start_line']['http_version'] = start_line_list[2]

  elif message_type == 'response':
    http_msg['start_line']['http_version'] = start_line_list[0]
    http_msg['start_line']['status_code'] = start_line_list[1]
    http_msg['start_line']['status_text'] = start_line_list[2]

  else:
    raise InvalidHTTPMessageType(f"Invalid HTTP message type {message_type}")

  http_msg['headers'] = {}
  for header_line in head_list[1:]:
    header_tuple = header_line.split(': ')
    field = header_tuple[0]
    http_msg['headers'][field] = header_tuple[1]

  return http_msg

def parse_body(raw_body: str, http_msg: dict):
  return

def parse_http_request(connection_socket: socket, buff_size: int):
  raw_head = receive_head(connection_socket, buff_size)
  http_msg = parse_head(raw_head, message_type='request')
  
  return


def contains_end_of_message(message, end_sequence):
    if end_sequence == message[(len(message) - len(end_sequence)):len(message)]:
        return True
    else:
        return False