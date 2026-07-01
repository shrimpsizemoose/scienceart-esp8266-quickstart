import argparse
import subprocess
import sys

DEFAULT_SCRIPT = "scripts/50-button-serial.py"


def clear_screen():
    print("\033[2J\033[H", end="")


def draw(state, raw_line):
    pressed = state == "pressed"
    waiting = state == "waiting"
    bg = "\033[44m" if waiting else "\033[42m" if pressed else "\033[100m"
    fg = "\033[37m" if waiting else "\033[30m" if pressed else "\033[37m"
    reset = "\033[0m"
    if waiting:
        title = " ЖДУ КНОПКУ "
    elif pressed:
        title = " КНОПКА НАЖАТА "
    else:
        title = " КНОПКА ОТПУЩЕНА "

    clear_screen()
    print(bg + fg + title.center(48) + reset)
    print()
    print("ESP8266 serial button worker")
    print()
    print("state:   %s" % state)
    print("event:   %s" % raw_line)
    print()
    print("Press Ctrl-C to quit.")


def button_state_from_line(line):
    if line == "button:pressed":
        return "pressed"
    if line == "button:released":
        return "released"
    return None


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--script", default=DEFAULT_SCRIPT)
    args = parser.parse_args()

    command = [
        sys.executable,
        "-m",
        "mpremote",
        "connect",
        args.port,
        "run",
        args.script,
    ]

    draw("waiting", "starting %s through mpremote" % args.script)

    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        bufsize=1,
    )

    try:
        assert process.stdout is not None, (
            "mpremote не установлен или что-то ещё не так с сетапом"
        )
        for raw_line in process.stdout:
            line = raw_line.strip()
            state = button_state_from_line(line)

            if state:
                draw(state, line)
            elif line:
                print(f"mpremote: {line}")

        return process.wait()
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait()


if __name__ == "__main__":
    try:
        sys.exit(main())
    except KeyboardInterrupt:
        print()
        sys.exit(0)
