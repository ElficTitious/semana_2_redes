from dataclasses import dataclass
import socket

class InvalidHTTPMessageType(Exception):
  """Error arrojado al intentar parsear un mensaje cuyo tipo
  no es indicado como request o response.
  """
  pass

@dataclass
class HTTPMessage:
  """Clase usada para representar un mensaje HTTP

  Attributes:
    message_type (str): Tipo del mensaje, request o response.
    start_line (dict): Start Line del mensaje, su estructura depende
                       del tipo del mensaje.
    headers (dict): Headers del mensaje en formato diccionario.
    body (str): cuerpo del mensaje, se asume que es texto plano (el formato
                se debe corresponder con el header Content-Type, y su largo 
                en bytes con el header Content-Length)
  """

  message_type: str
  start_line: dict
  headers: dict
  body: str

  def redact(self, forbidden_words: list) -> None:
    """Método que redacta el campo body de acuerdo a la lista de diccionarios
    forbidden_words. Por ejemplo, teniendo un cuerpo 'Hello World', y dada
    la lista [{'Hello': '[X]'}, {'World': [Y]}], éste método cambia el cuerpo
    a '[X] [Y]'.

    Parameters:
      forbidden_words (dict): Lista de diccionarios con las palabras a cambiar
                              y su reemplazos.
    """
    for dict in forbidden_words:
      for word in dict.keys():
        self.body = self.body.replace(word, dict[word])
    
    if "Content-Length" in self.headers.keys():
      # Debemos actualizar el content length para reflejar el cambio realizado.
      self.headers["Content-Length"] = str(len(self.body.encode()))

def contains_end_of_message(message, end_sequence):
  """Función que dado un string message, verifica si es que end_sequence es un
  substring de message.

  Parameters:
    message (str): Mensaje en el cual buscar la secuencia end_sequence.
    end_sequence (str): Secuencia que buscar en el string message.

  Returns:
    bool: True si end_sequence es substring de message y False de lo contrario.
  """
  return False if message.find(end_sequence) == -1 else True
 
def receive_head(connection_socket: socket, buff_size: int) -> tuple[str, str]:
  """Funcion que dado un socket y un tamaño de buffer, recibe solo el HEAD de un
  mensaje http, retornando el mismo como str junto con el comienzo del cuerpo (ésto
  pues luego de terminar de consumir el HEAD, dentro del último buffer irá el comienzo
  del cuerpo, el cual no puede ser recuperado por el método encargado de consumir el cuerpo
  a no ser que esta función lo transmita).

  Parameters:
    connection_socket (socket): Socket orientado a conexión donde recibir el mensaje http.
    buff_size (int): Tamaño en bytes del buffer donde se va almacenando el mensaje.

  Return:
    tuple[str, str]: HEAD del mensaje http junto con el comienzo del cuerpo
  """

  # recibimos la primera parte del mensaje
  buffer = connection_socket.recv(buff_size)
  end_sequence = '\r\n\r\n'
  head = buffer.decode()

  head_is_complete = contains_end_of_message(head, end_sequence)

  first_part_body: str

  # si el HEAD está completo (o sea que contiene la secuencia "\r\n\r\n") dejamos
  # la cabeza hasta el comienzo de dicha secuencia y definimos el comienzo del cuerpo
  # como el string que comienza luego de la secuencia.
  if head_is_complete:
      first_part_body = head[(head.find(end_sequence) + len(end_sequence)):]
      head = head[0:head.find(end_sequence)]
      

  # si el HEAD no está completo (no contienen la secuencia "\r\n\r\n")
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
              # nuevamente dejamos la cabeza hasta el comienzo de dicha secuencia y definimos
              # el comienzo del cuerpo como el string que comienza luego de la secuencia.
              first_part_body = head[(head.find(end_sequence) + len(end_sequence)):]
              head = head[0:head.find(end_sequence)]

  # finalmente retornamos el HEAD junto a la primera parte del body
  return head, first_part_body

def receive_body(connection_socket: socket, content_length: int, buff_size: int, first_part_body: str) -> str:
  """Funcion que dado un socket, un tamaño de buffer y el comienzo del cuerpo (consumido por
  la función receive head) recibe el resto del cuerpo hasta alcanzar un largo en bytes
  igual content_length desde el socket (correspondiente al BODY de un
  mensaje http).

  Parameters:
    connection_socket (socket): Socket orientado a conexión donde recibir el mensaje.
    content_length (int): largo en bytes del mensaje a recibir desde el socket.
    buff_size (int): Tamaño en bytes del buffer donde se va almacenando el mensaje.
    first_part_body (str): Primera parte del body (consumido por receive_head).

  Returns:
    (str): Mensaje de largo content_length (en bytes) recibido desde el socket. 
  """

  # Inicializamos el cuerpo como la primera parte del cuerpo, en bytes, transmitida
  # como parametro, y los bytes procesados como el largo de el cuerpo (que ya está en bytes).  
  body: bytes = first_part_body.encode()
  bytes_processed: int = len(first_part_body.encode())
  # Seguimos consumiendo desde el socket mientras no hayamos alcanzado content_length.
  while bytes_processed < content_length:
    buffer = connection_socket.recv(buff_size)
    bytes_processed += len(buffer)
    body += buffer
  
  body = body.decode()
  
  return body

def parse_head(raw_head: str, message_type: str) -> HTTPMessage:
  """Función que dado el HEAD de un mensaje HTTP y su tipo (request o response),
  parsea el HEAD acorde al tipo y lo devuelve como una instancia de la clase
  HTTPMessage.

  Parameters:
    raw_head (str): HEAD de un mensaje HTTP en formato string.
    message_type (str): Tipo del mensaje (request o response).
    
  Returns:
    (HTTPMessage): Instancia de HTTPMessage que representa al mensaje
                   dado como parámetro.
  
  Raises:
    InvalidHTTPMessageType: Si el tipo de mensaje dado como parámetro no
                            corresponde a request o response.
  """
  # Inicializamos el mensaje.
  http_msg = HTTPMessage(message_type, {}, {}, "")
  # Transformamos el HEAD en una lista, donde cada elemento corresponde a 
  # una linea dentro del HEAD.
  head_list = raw_head.split('\r\n')
  # Extraemos a una lista todos los miembros del start line.
  start_line_list = head_list[0].split(' ')

  # De acuerdo al tipo de mensaje llevamos la información del start line a
  # la estructura de datos generada.
  if message_type == 'request':
    http_msg.start_line['method'] = start_line_list[0]
    http_msg.start_line['resource'] = start_line_list[1]
    http_msg.start_line['http_version'] = start_line_list[2]

  elif message_type == 'response':
    http_msg.start_line['http_version'] = start_line_list[0]
    http_msg.start_line['status_code'] = start_line_list[1]
    http_msg.start_line['status_text'] = start_line_list[2]

  else:
    raise InvalidHTTPMessageType(f"Invalid HTTP message type {message_type}")

  # Finalmente extraemos los headers a la estructura de datos y la retornamos.
  for header_line in head_list[1:]:
    header_tuple = header_line.split(': ')
    field = header_tuple[0]
    http_msg.headers[field] = header_tuple[1]

  return http_msg

def parse_body(raw_body: str, http_msg: HTTPMessage) -> HTTPMessage:
  """Función que dado el body de un mensaje HTTP (como string), y una instancia
  de HTTPMessage, asigna como cuerpo del mismo el string dado como parámetro y devuelve
  la instancia de HTTPMessage.

  Parameters:
    raw_body (str): Cuerpo de un mensaje HTTP como string.
    http_message (HTTPMessage): Instancia inicializada de HTTPMessage a la cual asignar el
                                body.
  
  Returns:
    HTTPMessage: Misma instancia de HTTPMessage dada como parámetro, pero con el campo body
                 asignado al string dado.
  """
  http_msg.body = raw_body
  return http_msg

def receive_and_parse_http_message(connection_socket: socket, buff_size: int, message_type: str) -> HTTPMessage:
  """Función encargada de recibir un mensaje HTTP completo desde un socket y parsearlo.

  Parameters:
    connection_socket (socket): socket TCP desde donde recibir el mensaje.
    buff_size (int): Tamaño del buffer donde recibir el socket.
    message_type (str): Tipo del mensaje a recibir (request o response).

  Returns:
    HTTPMessage: Mensaje HTTP recibido representado como una instancia de la clase
                 HTTPMessage.
  """
  # Recibimos el HEAD completo del mensaje.
  raw_head, first_part_body = receive_head(connection_socket, buff_size)
  # Intentamos parsear la cabeza, donde lo que puede fallar es que el tipo del
  # mensaje dado como parámetro no corresponda a request o response.
  try :
    http_msg = parse_head(raw_head, message_type)
  except InvalidHTTPMessageType as e:
    print(repr(e))
  # Si se consigue parsear el mensaje:
  else:
    # De existir el header Content-Length, recibimos el cuerpo del mensaje y lo parseamos.
    if "Content-Length" in http_msg.headers.keys():
      raw_body = receive_body(connection_socket, int(http_msg.headers["Content-Length"]), buff_size, first_part_body)
      http_msg = parse_body(raw_body, http_msg)
    return http_msg

def create_http_msg(http_msg: HTTPMessage) -> str:
  """Función que dada una instancia de HTTPMessage (representando un mensaje
  http), retorna el mismo mensaje pero en formato HTTP.

  Parameters:
    http_message (HTTPMessage): Instancia de HTTPMessage para transformar a
                                formato HTTP.
  
  Returns:
    str: El mismo mensaje que aquel dado como parámetro pero en formato HTTP.
  """
  # Reconstruimos el string correspondiente a la start line del mensaje.
  start_line = ""
  counter = 1
  for key in http_msg.start_line.keys():
    start_line += http_msg.start_line[key]
    # Separamos cada campo con un espacio, donde para el caso del ultimo campo
    # agregamos una secuencia de fin de linea.
    if counter != len(http_msg.start_line):
      start_line += " "
    else:
      start_line += "\r\n"

    counter += 1
  
  # Ahora reconstruimos los headers
  headers = ""
  for header in http_msg.headers.items():
    headers += header[0] + ": " + header[1] + "\r\n"
  headers += "\r\n"

  # Finalmente el body se corresponde directamente con el campo body del parametro
  # http_msg
  body = http_msg.body

  # El resultado final es la concatenación del start_line, headears y body
  return start_line + headers + body
