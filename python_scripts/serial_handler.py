import serial
import time
import argparse
import sys
from serial.serialutil import SerialException

parser = argparse.ArgumentParser(description='Serial reading')
parser.add_argument('serial_port',
        help='serial device path')

args = parser.parse_args()
puerto_serial = serial.Serial(args.serial_port, 115200, timeout=2)  # Ajusta el nombre del puerto según tu configuración
time.sleep(2)   # Wait for grbl to initialize 
puerto_serial.flushInput()  # Flush startup text in serial input

try:
    while puerto_serial.is_open:
        # Your code here
        pass
except KeyboardInterrupt:
    # Handle keyboard interrupt if needed
    pass
finally:
    # Make sure to close the serial port when done
    if puerto_serial.is_open:
        puerto_serial.close()
    print('Comunicación serial se cerro')

'''
try:
    while True:
        try :
            data = puerto_serial.readline()
            if data.decode('utf-8').strip() != '' :
                print(data.decode('utf-8').strip())
                sys.stdout.flush()
        except SerialException as e :
              print(e)
except KeyboardInterrupt:
    print("Saliendo del bucle infinito...")
    sys.stdout.flush()
    puerto_serial.close()
'''