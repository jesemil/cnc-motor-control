import serial
import time

puerto_serial = serial.Serial('/dev/ttyACM0', 115200)  # Ajusta el nombre del puerto según tu configuración

ctrl_x = chr(24)
comando = '$X\n'
# Tu lógica para enviar comandos al puerto serial
puerto_serial.write(comando.encode('utf-8'))
time.sleep(1)