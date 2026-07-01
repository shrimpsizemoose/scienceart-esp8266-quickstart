from time import sleep_ms

from machine import Pin

# Схема:
# - кнопка 1 -> D1 / GPIO5
# - кнопка 2 -> GND
#
# Встроенный подтягивающий резистр на The internal pull-up keeps the pin at 1 when released.
# Pressing the button connects it to GND, so pressed == 0.
BUTTON_PIN = 5
LED_PIN = 2

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)
led = Pin(LED_PIN, Pin.OUT, value=1)


while True:
    if button.value() == 0:
        led.value(0)
    else:
        led.value(1)

    sleep_ms(20)
