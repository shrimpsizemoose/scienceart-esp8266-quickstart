from time import sleep

from machine import Pin

MESSAGE = "SCIENCE ART"

# сколько горит точка, в секундах
UNIT_SECONDS = 0.15

MORSE = {
    "A": ".-",
    "B": "-...",
    "C": "-.-.",
    "D": "-..",
    "E": ".",
    "F": "..-.",
    "G": "--.",
    "H": "....",
    "I": "..",
    "J": ".---",
    "K": "-.-",
    "L": ".-..",
    "M": "--",
    "N": "-.",
    "O": "---",
    "P": ".--.",
    "Q": "--.-",
    "R": ".-.",
    "S": "...",
    "T": "-",
    "U": "..-",
    "V": "...-",
    "W": ".--",
    "X": "-..-",
    "Y": "-.--",
    "Z": "--..",
}

# встроенный светодиод NodeMCU ESP8266
# обычно на GPIO2 / D4.
# active-low: value=0 включает, value=1 выключает
led = Pin(2, Pin.OUT, value=1)


# если сложно запомнить что где то можно сделать
# вспомогательные функции
def led_on():
    led.value(0)


def led_off():
    led.value(1)


def flash_symbol(symbol):
    led_on()
    if symbol == ".":
        sleep(UNIT_SECONDS)
    else:  # тире в три раза дольше точки
        sleep(UNIT_SECONDS * 3)
    led_off()
    sleep(UNIT_SECONDS)


# бесконечный цикл программы
# по кругу моргаем светодиодом
# или точку или тире
# или ждём между символами
# или ждём пробел между словами
while True:
    for char in MESSAGE:
        if char == " ":
            sleep(UNIT_SECONDS * 7)
            continue

        for symbol in MORSE[char]:
            flash_symbol(symbol)

        sleep(UNIT_SECONDS * 2)

    sleep(UNIT_SECONDS * 10)
