import serial
import time

puerto_serial = serial.Serial()  # Ajusta el nombre del puerto según tu configuración
puerto_serial.port = '/dev/ttyACM0'
puerto_serial.baudrate = 115200
if not puerto_serial.is_open :
    puerto_serial.open()
try :
    ctrl_x = chr(24)
    #comando = 'G90G0X0.Y10.\n'
    puerto_serial. reset_input_buffer()
    comando = '$X\n'
    # Tu lógica para enviar comandos al puerto serial
    puerto_serial.write(comando.encode('utf-8'))
except Exception as e :
    print(e)