import serial

class SerialHandler:
    def __init__(self, port, BAUD_RATE):
        self.s = None
        self.BAUD_RATE = BAUD_RATE 
        self.port = port
    def open_connection (self) :
        if self.s is None or not self.s.is_open:
            print(self.s)
            self.s = serial.Serial(self.port, baudrate=self.BAUD_RATE)
            print('Conexión serial iniciada')
            return True
        return False
    def set_port(self, new_port) :
        if self.port != new_port :
            self.port = new_port
    def send_command(self, command):
        self.s.write(command.encode())
    def read_response(self):
        r=self.s.readline().decode()
        return r
    def flush_serial(self):
        self.s.flushInput()
    def close_connection(self):
        self.s.close()
if 'global_serial_handler' not in globals():
    global_serial_handler = SerialHandler(port=None,BAUD_RATE=115200)