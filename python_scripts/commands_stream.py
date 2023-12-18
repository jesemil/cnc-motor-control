#!/usr/bin/env python
"""\
Simple g-code streaming script for grbl

Provided as an illustration of the basic communication interface
for grbl. When grbl has finished parsing the g-code block, it will
return an 'ok' or 'error' response. When the planner buffer is full,
grbl will not send a response until the planner buffer clears space.

G02/03 arcs are special exceptions, where they inject short line 
segments directly into the planner. So there may not be a response 
from grbl for the duration of the arc.

---------------------
The MIT License (MIT)

Copyright (c) 2012 Sungeun K. Jeon

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN
THE SOFTWARE.
---------------------
"""

import sys
import serial
import time
import argparse

BAUD_RATE = 115200

parser = argparse.ArgumentParser(description='Stream g-code commands to grbl.')
parser.add_argument('serial_port',
        help='serial device path')
parser.add_argument('-s','--status',action='store_true', default=False, 
        help='machine status plus location')
parser.add_argument('-hm','--homing',action='store_true', default=False, 
        help='init homing cycle')   
parser.add_argument('-x','--hold',action='store_true', default=False, 
        help='holding grbl')
parser.add_argument('-rs','--reset',action='store_true', default=False, 
        help='Reset grbl')
parser.add_argument('-r','--resume',action='store_true', default=False, 
        help='resume grbl')     
parser.add_argument('-u','--update',action='store_true', default=False,
        help='update settings')
parser.add_argument('-m','--move',action='store_true', default=False,
        help='move commands')
parser.add_argument('-c','--close',action='store_true', default=False,
        help='close serial connection')
parser.add_argument('-mm','--move_mask',type=int, choices=range(8), help='move direction')
parser.add_argument('--speed', type=int, help='speed argument for update mode')
parser.add_argument('--block_x', type=int, help='block x argument for update mode')
parser.add_argument('--block_y', type=int, help='block y argument for update mode')
# Adding homing_mode with choices for 4-bit mask
parser.add_argument('--homing_mode', type=int, choices=range(16), help='homing mode argument for update mode (4-bit mask)')
args = parser.parse_args()

s = serial.Serial()  # Ajusta el nombre del puerto según tu configuración
s.port = '/dev/ttyACM0'
s.baudrate = 115200
if not s.is_open :
    s.open()

#s = serial.Serial(args.serial_port,BAUD_RATE)
#s.write(("\r\n\r\n").encode('utf-8'))
#time.sleep(2)   # Wait for grbl to initialize 
#s.flushInput()  # Flush startup text in serial input
#s.write(("$X\n").encode('utf-8'))
#time.sleep(2)   # Wait for grbl to initialize 
#s.flushInput()
def send_grbl(command) :
    try :
        print('Sending: ' + command)
        sys.stdout.flush()
        s.write((command).encode('utf-8')) # Send g-code block to grbl
        grbl_out = s.readline().decode('utf-8') # Wait for grbl response with carriage return
        print(grbl_out.strip())
        sys.stdout.flush()
    except Exception as e:
        print(e)
        sys.stdout.flush()

if args.hold :
    s.write(('!').encode('utf-8')) # Send g-code block to grbl
if args.reset :
    ctrl_x = chr(24)
    send_grbl(ctrl_x) # Send g-code block to grbl
    time.sleep(2)
    s.flushInput()
    send_grbl('?') # Send g-code block to grbl
if args.resume :
    s.write(('~').encode('utf-8')) # Send g-code block to grbl
if args.status : 
    send_grbl('$X\n')
    s.flushInput()
    send_grbl('?')
if args.homing : 
    send_grbl('$H\n')
if args.update :
    send_grbl('$110='+str(args.speed)+'\n')
    send_grbl('$111='+str(args.speed)+'\n')
    send_grbl('$25='+str(args.homing_mode)+'\n')
    send_grbl('$130='+str(args.block_x)+'\n')
    send_grbl('$131='+str(args.block_y)+'\n')
if args.move :
    if args.move_mask == 0 : #up
        send_grbl('G91G0X0Y10.\n')
    if args.move_mask == 1 : #down
        send_grbl('G91G0Y-10.\n')
    if args.move_mask == 2 : #right
        send_grbl('G91G0X10.\n')
    if args.move_mask == 3 : #left
        send_grbl('G91G0X-10.\n')
    if args.move_mask == 4 : #up-right
        send_grbl('G91G0X7.Y7.\n')
    if args.move_mask == 5 : #up-left
        send_grbl('G91G0X-7.Y7\n')
    if args.move_mask == 6 : #down-right
        send_grbl('G91G0X7.Y-7.\n')
    if args.move_mask == 7 : #down-left
        send_grbl('G91G0X-7.Y-7.\n')
if args.close :
    s.close()
    s.__del__()
#if args.check : 
#    check_mode = True
# Open g-code file
#f = open('grbl.gcode','r');

# Wake up grbl


#s.write(("$X" + "\n").encode('utf-8'))
#time.sleep(2)   # Wait for grbl to initialize 
#s.flushInput()  # Flush startup text in serial input


# Stream g-code to grbl
'''
for line in f:
    l = line.strip() # Strip all EOL characters for consistency
    print 'Sending: ' + l,
    s.write(l + '\n') # Send g-code block to grbl
    grbl_out = s.readline() # Wait for grbl response with carriage return
    print ' : ' + grbl_out.strip()
'''


#input("  Press <Enter> to exit and disable grbl.") 

# Close file and serial port
#f.close()
#s.close()    