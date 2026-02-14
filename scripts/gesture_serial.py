import time
import sys
try:
    import serial
    import serial.tools.list_ports
except Exception:
    print('pyserial required. Install with: pip install pyserial')
    sys.exit(1)


def choose_port():
    ports = list(serial.tools.list_ports.comports())
    if not ports:
        print('No serial ports found')
        return None
    print('Available ports:')
    for i, p in enumerate(ports):
        print(f'{i}: {p.device} - {p.description}')
    choice = input('Select port index (enter for 0): ').strip()
    idx = int(choice) if choice else 0
    return ports[idx].device


def main():
    port = choose_port()
    if not port:
        return
    ser = serial.Serial(port, 115200, timeout=1)
    time.sleep(2)
    print(f'Listening on {port} (Ctrl-C to stop)')
    try:
        while True:
            line = ser.readline().decode(errors='ignore').strip()
            if line:
                print('Gesture:', line)
    except KeyboardInterrupt:
        pass
    finally:
        ser.close()


if __name__ == '__main__':
    main()
