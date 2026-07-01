import argparse
import socket
import struct
import subprocess
import sys

DEFAULT_SCRIPT = "scripts/50-button-serial.py"


# собираеим пакет в нужном формтае
def osc_string(value):
    data = value.encode("utf-8") + b"\0"
    padding = (4 - len(data) % 4) % 4
    return data + (b"\0" * padding)


def osc_int_message(path, value):
    return osc_string(path) + osc_string(",i") + struct.pack(">i", value)


# кастуем состояние из строки к инту
def button_value_from_line(line):
    if line == "button:pressed":
        return 1
    if line == "button:released":
        return 0
    return None


def add_arguments(parser):
    parser.add_argument("--port", default="/dev/ttyUSB0")
    parser.add_argument("--script", default=DEFAULT_SCRIPT)
    parser.add_argument("--osc-host", default="127.0.0.1")
    parser.add_argument("--osc-port", type=int, default=8000)
    parser.add_argument("--osc-path", default="/esp/button")


def main():
    parser = argparse.ArgumentParser()
    add_arguments(parser)
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

    print(f"running {args.script} on {args.port}")
    print(f"sending OSC {args.osc_path} -> {args.osc_host}:{args.osc_port}")
    print("press Ctrl-C to quit")

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        errors="replace",
        bufsize=1,
    )

    try:
        assert process.stdout is not None
        for raw_line in process.stdout:
            line = raw_line.strip()
            value = button_value_from_line(line)

            if value is None:
                if line:
                    print(f"mpremote: {line}" % line)
                continue

            message = osc_int_message(args.osc_path, value)
            sock.sendto(message, (args.osc_host, args.osc_port))
            print(f"{args.osc_path} {value}")

        return process.wait()
    finally:
        sock.close()
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
