set dotenv-load

PORT := env("PORT", "/dev/ttyUSB0")
FLASH_BAUD := env("FLASH_BAUD", "460800")
FIRMWARE_URL := env("FIRMWARE_URL", "https://micropython.org/resources/firmware/ESP8266_GENERIC-20260406-v1.28.0.bin")
FIRMWARE := env("FIRMWARE", "firmware/esp8266-micropython.bin")
UV_CACHE_DIR := env("UV_CACHE_DIR", ".uv-cache")
SCRIPT := env("SCRIPT", "scripts/10-blink.py")
BUTTON_SCRIPT := env("BUTTON_SCRIPT", "scripts/50-button-serial.py")

_:
  @just --list

# Create local venv, install tools
[group("prep")]
install-deps:
  test -d .venv || UV_CACHE_DIR="{{UV_CACHE_DIR}}" uv venv
  UV_CACHE_DIR="{{UV_CACHE_DIR}}" uv pip install esptool mpremote

# Download MicroPython for ESP8266
[group("prep")]
download-firmware:
  mkdir -p firmware
  curl -L "{{FIRMWARE_URL}}" -o "{{FIRMWARE}}"

# Show likely serial ports
ports:
  @ls /dev/ttyUSB* /dev/ttyACM* 2>/dev/null || true

# Erase the ESP8266 flash
[group("prep")]
erase: install-deps
  .venv/bin/python -m esptool --chip esp8266 --port "{{PORT}}" erase_flash

# Flash MicroPython firmware to the ESP8266
flash: install-deps download-firmware
  .venv/bin/python -m esptool --chip esp8266 --port "{{PORT}}" --baud "{{FLASH_BAUD}}" write_flash --flash_size=detect 0 "{{FIRMWARE}}"
  sleep 3

# Open the MicroPython serial REPL
[group("prep")]
repl: install-deps
  echo "Чтобы зайти в репл, нажми Ctrl-C"
  echo "!!! ВЫХОДИ ИЗ РЕПЛА ПО Ctrl-]"
  sleep 2
  .venv/bin/python -m mpremote connect "{{PORT}}" repl

# Copy SCRIPT to the board as main.py and soft-reset
put-script: install-deps
  @set -eu; \
  for attempt in 1 2 3 4 5; do \
    echo "copying {{SCRIPT}} to main.py, attempt $attempt..."; \
    if .venv/bin/python -m mpremote connect "{{PORT}}" sleep 1 fs cp "{{SCRIPT}}" :main.py; then \
      .venv/bin/python -m mpremote connect "{{PORT}}" reset; \
      exit 0; \
    fi; \
    sleep 2; \
  done; \
  echo "failed to enter raw REPL; try pressing RESET, then run: PORT={{PORT}} SCRIPT={{SCRIPT}} just put-script"; \
  exit 1

# Copy `scripts/10-blink.py` to the board as main.py and soft-reset
[group("examples")]
put-blink:
  just SCRIPT=scripts/10-blink.py put-script

# Copy `scripts/40-button-led.py` to the board as main.py and soft-reset
[group("examples")]
put-button-led:
  just SCRIPT=scripts/40-button-led.py put-script

# Copy `scripts/50-button-serial.py` to the board as main.py and soft-reset
[group("examples")]
put-button-serial:
  just SCRIPT=scripts/50-button-serial.py put-script

# Read button events from the ESP8266 and update this terminal
[group("examples")]
button-worker: install-deps
  .venv/bin/python laptop/button_worker.py --port "{{PORT}}" --script "{{BUTTON_SCRIPT}}"

# Read button events and send OSC for Max / TouchDesigner
[group("examples")]
button-osc-worker: install-deps
  .venv/bin/python laptop/button_osc_worker.py --port "{{PORT}}" --script "{{BUTTON_SCRIPT}}"

# Flash firmware, install blink as main.py, then open the REPL
[group("prep")]
setup: flash put-blink repl
