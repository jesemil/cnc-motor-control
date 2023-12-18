#!/usr/bin/env python
"""\

Stream g-code to grbl controller

This script differs from the simple_stream.py script by 
tracking the number of characters in grbl's serial read
buffer. This allows grbl to fetch the next line directly
from the serial buffer and does not have to wait for a 
response from the computer. This effectively adds another
buffer layer to prevent buffer starvation.

CHANGELOG:
- 20170531: Status report feedback at 1.0 second intervals.
    Configurable baudrate and report intervals. Bug fixes.
- 20161212: Added push message feedback for simple streaming
- 20140714: Updated baud rate to 115200. Added a settings
  write mode via simple streaming method. MIT-licensed.

TODO: 
- Add realtime control commands during streaming.

---------------------
The MIT License (MIT)

Copyright (c) 2012-2017 Sungeun K. Jeon

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

import serial
import re
import time
import sys
import argparse
import threading

RX_BUFFER_SIZE = 128
BAUD_RATE = 115200
ENABLE_STATUS_REPORTS = True
REPORT_INTERVAL = 1.0 # seconds

is_run = True # Controls query timer

# Define command line argument interface
parser = argparse.ArgumentParser(description='Stream g-code file to grbl. (pySerial and argparse libraries required)')
parser.add_argument('gcode_file', type=argparse.FileType('r'),
        help='g-code filename to be streamed')
parser.add_argument('device_file',
        help='serial device path')
parser.add_argument('-q','--quiet',action='store_true', default=False, 
        help='suppress output text')
parser.add_argument('-s','--settings',action='store_true', default=False, 
        help='settings write mode')        
parser.add_argument('-c','--check',action='store_true', default=False,
        help='stream in check mode')
args = parser.parse_args()

# Periodic timer to query for status reports
# TODO: Need to track down why this doesn't restart consistently before a release.
def send_status_query():
    unicode_string_status='?'
    byte_string_status = unicode_string_status.encode('utf-8')
    s.write(byte_string_status)
    
def periodic_timer() :
    while is_run:
      send_status_query()
      time.sleep(REPORT_INTERVAL)
  

# Initialize
#s = serial.Serial(args.device_file,BAUD_RATE)
s = serial.Serial()
s.port = args.device_file
s.baudrate = BAUD_RATE
if not s.is_open :
    s.open()
f = args.gcode_file
verbose = True
if args.quiet : verbose = False
settings_mode = False
if args.settings : settings_mode = True
check_mode = False
if args.check : check_mode = True

# Wake up grbl
print("Initializing Grbl...")
sys.stdout.flush()
#unicode_string_init = '\r\n\r\n'
#byte_string_init = unicode_string_init.encode('utf-8')
#s.write(byte_string_init)


# Wait for grbl to initialize and flush startup text in serial input
#time.sleep(2)
#s.flushInput()

#s.write(("$X" + "\n").encode('utf-8'))
#time.sleep(2)   # Wait for grbl to initialize 
#s.flushInput()  # Flush startup text in serial input


if check_mode :
    print ("Enabling Grbl Check-Mode: SND: [$C]",)
    sys.stdout.flush()
    s.write(("$C\n").encode('utf-8'))
    while 1:
        grbl_out = s.readline().decode('utf-8').strip() # Wait for grbl response with carriage return
        if grbl_out.find('error') >= 0 :
            print ("REC:",grbl_out)
            sys.stdout.flush()
            print ("  Failed to set Grbl check-mode. Aborting...")
            sys.stdout.flush()
            quit()
        elif grbl_out.find('ok') >= 0 :
            if verbose: print ('REC:',grbl_out)
            sys.stdout.flush()
            break

start_time = time.time()

# Start status report periodic timer
if ENABLE_STATUS_REPORTS :
    timerThread = threading.Thread(target=periodic_timer)
    timerThread.daemon = True
    timerThread.start()

# Stream g-code to grbl
l_count = 0
error_count = 0
if settings_mode:
    # Send settings file via simple call-response streaming method. Settings must be streamed
    # in this manner since the EEPROM accessing cycles shut-off the serial interrupt.
    print ("SETTINGS MODE: Streaming", args.gcode_file.name, " to ", args.device_file)
    for line in f:
        l_count += 1 # Iterate line counter    
        # l_block = re.sub('\s|\(.*?\)','',line).upper() # Strip comments/spaces/new line and capitalize
        l_block = line.strip() # Strip all EOL characters for consistency
        if verbose: print("SND>"+str(l_count)+": \"" + l_block + "\"")
        sys.stdout.flush()
        unicode_string_stream = l_block + '\n'
        byte_string_stream = unicode_string_stream.encode('utf-8')
        s.write(byte_string_stream) # Send g-code block to grbl
        while 1:
            grbl_out = s.readline().decode('utf-8').strip() # Wait for grbl response with carriage return
            if grbl_out.find('ok') >= 0 :
                if verbose: print ("  REC<"+str(l_count)+": \""+grbl_out+"\"")
                sys.stdout.flush()
                break
            elif grbl_out.find('error') >= 0 :
                if verbose: print ("  REC<"+str(l_count)+": \""+grbl_out+"\"")
                sys.stdout.flush()
                error_count += 1
                break
            else:
                print ("    MSG: \""+grbl_out+"\"")
                sys.stdout.flush()
else:    
    # Send g-code program via a more agressive streaming protocol that forces characters into
    # Grbl's serial read buffer to ensure Grbl has immediate access to the next g-code command
    # rather than wait for the call-response serial protocol to finish. This is done by careful
    # counting of the number of characters sent by the streamer to Grbl and tracking Grbl's 
    # responses, such that we never overflow Grbl's serial read buffer. 
    g_count = 0
    c_line = []
    alarm_flag=False
    for line in f:
        l_count += 1 # Iterate line counter
        l_block = re.sub('\s|\(.*?\)','',line).upper() # Strip comments/spaces/new line and capitalize
        # l_block = line.strip()
        c_line.append(len(l_block)+1) # Track number of characters in grbl serial read buffer
        grbl_out = '' 
        while sum(c_line) >= RX_BUFFER_SIZE-1 | s.inWaiting() :
            out_temp = s.readline().decode('utf-8').strip() # Wait for grbl response
            print(out_temp)
            sys.stdout.flush()
            if ('ALARM:1') in out_temp or ('Grbl 1.1h' in out_temp):
                print ("Entre aca") # Debug response
                sys.stdout.flush()
                alarm_flag=True
            if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
                print ("    MSG: \""+out_temp+"\"") # Debug response
                sys.stdout.flush()
            else :
                if out_temp.find('error') >= 0 : error_count += 1
                g_count += 1 # Iterate g-code counter
                if verbose: print ("  REC<"+str(g_count)+": \""+out_temp+"\"")
                sys.stdout.flush()
                del c_line[0] # Delete the block character count corresponding to the last 'ok'
            if alarm_flag :
                break
        if alarm_flag :
                break
        unicode_string_stream = l_block + '\n'
        byte_string_stream = unicode_string_stream.encode('utf-8')
        s.write(byte_string_stream) # Send g-code block to grbl
        if verbose: print ("SND>"+str(l_count)+": \"" + l_block + "\"")
        sys.stdout.flush()
    # Wait until all responses have been received.
    while l_count > g_count :
        if alarm_flag : break
        out_temp = s.readline().decode('utf-8').strip() # Wait for grbl response
        if out_temp.find('ok') < 0 and out_temp.find('error') < 0 :
            print ("    MSG: \""+out_temp+"\"") # Debug response
            sys.stdout.flush()
        else :
            if out_temp.find('error') >= 0 : error_count += 1
            g_count += 1 # Iterate g-code counter
            del c_line[0] # Delete the block character count corresponding to the last 'ok'
            if verbose: print ("  REC<"+str(g_count)+": \""+out_temp + "\"")
            sys.stdout.flush()

# Wait for user input after streaming is completed
print ("\nG-code streaming finished!")
sys.stdout.flush()
end_time = time.time()
is_run = False
print (" Time elapsed: ",end_time-start_time,"\n")
if check_mode :
    if error_count > 0 :
        print ("CHECK FAILED:",error_count,"errors found! See output for details.\n")
    else :
        print ("CHECK PASSED: No errors found in g-code program.\n")
else :
   print ("WARNING: Wait until Grbl completes buffered g-code blocks before exiting.")
   #input("  Press <Enter> to exit and disable Grbl.") 

# Close file and serial port
f.close()
#s.close()