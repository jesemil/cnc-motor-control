from serial_handler import global_serial_handler
import time
import sys
global_serial_handler.set_port('/dev/ttyACM0')

v=False
v = global_serial_handler.open_connection()
if v :
    r = global_serial_handler.read_response()
    print(r)
    time.sleep(2)
    global_serial_handler.flush_serial()


def send_grbl(command) :
    try :
        print('Sending: ' + command)
        sys.stdout.flush()
        global_serial_handler.send_command(command) # Send g-code block to grbl
        #grbl_out=''
        #while grbl_out != None:
        grbl_out = global_serial_handler.read_response() # Wait for grbl response with carriage return
        print(grbl_out.strip())
        sys.stdout.flush()
    except Exception as e:
        print(e)
        sys.stdout.flush()

send_grbl('G0X1.\n')