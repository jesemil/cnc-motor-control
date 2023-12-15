import serial
import time
import argparse
import sys

parser = argparse.ArgumentParser(description='Serial reading')
parser.add_argument('serial_port',
        help='serial device path')
parser.add_argument('-s','--stop',action='store_true', default=False, 
        help='stop serial communication')

args = parser.parse_args()

puerto_serial = serial.Serial(args.serial_port, 115200)  # Ajusta el nombre del puerto según tu configuración

try:
    while True:
        # Tu lógica para leer/escribir en el puerto serial
        data = puerto_serial.readline()
        print(data.decode('utf-8'), flush=True)
        sys.stdout.flush()
        time.sleep(1)

except KeyboardInterrupt:
    print("Saliendo del bucle infinito...")
    sys.stdout.flush()
    puerto_serial.close()