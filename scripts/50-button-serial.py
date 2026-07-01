from time import sleep_ms, ticks_diff, ticks_ms

from machine import Pin

# Wiring:
# - Button leg 1 -> D1 / GPIO5
# - Button leg 2 -> GND
#
# The internal pull-up keeps the pin at 1 when released.
# Pressing the button connects it to GND, so pressed == 0.
BUTTON_PIN = 5
DEBOUNCE_MS = 30
HEARTBEAT_MS = 1000

button = Pin(BUTTON_PIN, Pin.IN, Pin.PULL_UP)


def is_pressed():
    return button.value() == 0


def send_state(pressed):
    if pressed:
        print("button:pressed")
    else:
        print("button:released")


last_state = is_pressed()
last_report_ms = ticks_ms()
send_state(last_state)

while True:
    current_state = is_pressed()

    if current_state != last_state:
        sleep_ms(DEBOUNCE_MS)
        current_state = is_pressed()

        if current_state != last_state:
            last_state = current_state
            last_report_ms = ticks_ms()
            send_state(last_state)

    if ticks_diff(ticks_ms(), last_report_ms) >= HEARTBEAT_MS:
        last_report_ms = ticks_ms()
        send_state(last_state)

    sleep_ms(10)
