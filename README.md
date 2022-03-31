# Módulo HTTP
## Semana dos y tres

### Ejecución del proxy

Para ejecutar el proxy es necesario dar como argumento el nombre de un archivo .json con la siguiente estructura:

```json
{
  "user": "user@mail.com"
  "blocked": ["adress"]
  "forbidden_words": [
    {"word": "replacement"}
  ]
}
```
Se supone así que el script será ejecutado con un argumento de este tipo, el cual debe estar en el mismo directorio que el script, donde de no suceder aquello se imprimirá el mensaje `Error when trying to read config file` y se detendrá la ejecución.

Se incluye dentro del proyecto un archivo `config.json` de ejemplo, por lo que para ejecutar el script bastaría correr (dentro del directorio):

```bash
python3 proxy_http.py config.json
```

### Estructura del código y funcionamiento del proxy

Se incluyen dos archivos de código, `utilities.py` y `proxy_http.py`, donde el primero tiene todas las definiciones necesarias para el funcionamiento del proxy, y el segundo tiene el proxy *per se*.

El proxy recibe conexiones indefinidamente; cuando llega una conexión desde el cliente ésta se acepta, y se recibe y parsea el request HTTP asociado con la función `receive_and_parse_http_message`, la cual retorna una instancia de la clase `HTTPMessage`, que es una *data class* con los campos `message_type`, `start_line`, `headers` y `body`, y representa evidentemente a un mensaje HTTP. Luego de esto guardamos el host a partir del header `Host` ubicado en los headers del mensaje (para posteriormente poder conectarnos con el servidor), e intentamos obtener la información dentro del archivo de configuración dado como argumento al script. 

A continuación procedemos a bloquear la página solicitada si es que el recurso solicitado en el start line del mensaje se encuentra dentro la lista `blocked` del archivo de configuración; en cuyo caso respondemos al cliente un mensaje HTTP con status code 403 y status text `Blocked address` (se agrega un html en el cuerpo para que el cliente tenga algo que mostrar).

Si el recurso solicitado no se encuentra bloqueado, procedemos a agregar el correo indicado en el campo `user` del archivo de configuración al header `X-ElQuePregunta`, y transformamos la request a formato HTTP como texto plano (usando la función `create_http_message`), redirigiendo así al servidor.

Realizado lo anterior recibimos y parseamos la respuesta del servidor haciendo uso nuevamente de la función `receive_and_parse_http_message`, y con el método `redact` de la clase `HTTPMessage`, reemplazamos todas las palabras prohibidas por aquellas que indica la lista `forbidden_words` del archivo de configuración.

Nuevamente transformamos la response resultante de la redacción a formato HTTP como texto plano (usando la función `create_http_message`), y redirigimos al cliente.

#### Funciones en `utilities.py`

Todas las funciones utilizadas están correctamente documentadas en el mismo archivo.
