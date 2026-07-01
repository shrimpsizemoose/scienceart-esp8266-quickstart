import socket

import network
from machine import Pin

# поменяй SSID чтобы не путаться
SSID = "science-art-esp8266"
PASSWORD = "scienceart"

# встроенные светодиод
# value=0 включает, value=1 выключает
led = Pin(2, Pin.OUT, value=1)


# эту функцию будем вызывать чтобы включить светодиод
def led_on():
    led.value(0)


# эту функцию будем вызывать чтобы выключить светодиод
def led_off():
    led.value(1)


# эта функция нам нужна чтобы понять состояние светодиода
def tell_led_state():
    is_on = led.value() == 0
    return "ВКЛЮЧЕН" if is_on else "ВЫКЛЮЧЕН"


# этой функцией мы собираем страничку
# страница это proto_head + html
# между ними должна быть пустая строка!
#
# на страничке текущий статус светодиода и две кнопки:
#
# +-------------------------------+
# | ESP8266 Светодоид             |
# | Меня зовут Матвей             |
# |                               |
# | Светодиод ВКЛЮЧЕН             |
# |                               |
# | [ Включить ]  [ Выключить ]   |
# +-------------------------------+
#
def page():
    proto_head = """
HTTP/1.1 200 OK
Content-Type: text/html
Connection: close
"""
    html = """
<!doctype html>
<html>
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>ESP8266 СВЕТОДИОД</title>
    <style>
      body {
          font-family: sans-serif;
          margin: 2rem;
          line-height: 1.4;
      }
      a {
          display: inline-block;
          padding: 0.8rem 1rem;
          margin-right: 0.5rem;
          background: #111;
          color: white;
          text-decoration: none;
      }
    </style>
  </head>
  <body>
    <h1>ESP8266 Светодиод</h1>
    <p>Меня зовут %(name)s</p>
    <p>Светодиод: <strong>%(state)s</strong>.</p>
    <p><a href="/on">Включить</a><a href="/off">Выключить</a></p>
  </body>
</html>"""

    # ключ словаря state тиакой же как в строке
    # где мы делаем %(state)s
    # (s на конце после скобки тоже важно)
    context = {
        "state": tell_led_state(),
        "name": "Матвей",
    }
    page = proto_head + "\n" + html % context
    return page


### код основной программы
# настроить сеть (делается до цикла)
# обрабатывать подключения-выключения

ap = network.WLAN(network.AP_IF)
ap.active(True)
ap.config(essid=SSID, password=PASSWORD)

addr = socket.getaddrinfo("0.0.0.0", 80)[0][-1]
server = socket.socket()
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind(addr)
server.listen(1)

print("Wi-Fi:", SSID)
print("Password:", PASSWORD)
print("http://%s/" % ap.ifconfig()[0])

while True:
    client, _ = server.accept()
    request = client.recv(1024)

    # когда кто-то нажал на кнопку то мы обработали ссылку и вызвали функцию
    # тут важен `b` перед кавычкой
    if b"GET /on " in request:
        led_on()
    elif b"GET /off " in request:
        led_off()

    # в конце всё равно отправляем страницу
    client.send(page())
    client.close()
