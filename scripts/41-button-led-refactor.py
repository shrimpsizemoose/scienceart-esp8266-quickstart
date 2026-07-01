from time import sleep_ms

from machine import Pin

BUTTON_PIN = 5
LED_PIN = 2

# Ножки:
# - Button leg 1 -> D1 / GPIO5
# - Button leg 2 -> GND
#
# Встроенный подтягивающий резистор (когда мы его включим)
# сделает так что нажимая на кнопку мы получаем GND,
# поэтому "если нажато то значение 0"

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT, value=1)

# функции хелперы чтобы было проще уследить за логикой
# чтобы понять, какие нужны надо поэтапно понять что мы делаем:
#   надо убедиться что внешнее что-то произошло
#        -> кнопка нажата?
#   отреагировать если нажата
#        -> зажечь светодиод
#   успокоиться если нет
#        -> потушить светодиод
#   как-то определиться что делаем в промежутках
#        -> например, ждём 20 миллисекунд


def is_pressed():
    nazhato = button.value() == 0
    return nazhato


def action():
    led.value(0)


def calm():
    led.value(1)


def between_checks():
    sleep_ms(20)


# основная часть программы
# в бесконечном цикле проверяем нажата ли кнопка
# если нажато то дёргаемся если нет то нет
# между проверками ждём

while True:
    if is_pressed():
        action()
    else:
        calm()

    between_checks()
