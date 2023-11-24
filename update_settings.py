import argparse

parser = argparse.ArgumentParser(description='update settings file')
parser.add_argument('gcode_file', type=str,
        help='settigs codes')
args = parser.parse_args()

## Default settings

step_pulse=10 	        #microseconds
step_idle_delay=25      #milliseconds
step_port_invert=0      #mask
direction_port_invert=0 #mask
'''
mask    Invert X    Invert Y
0       N           N
1       Y           N
2       N           Y
3       Y           Y
'''
step_enamble_invert=0   #boolean
limit_pins_invert=0 	#boolean
probe_pin_invert=0 	    #boolean
status_report=1 	    #mask
junction_deviation=0.010#mm
arc_tolerance=0.002 	#mm
report_inches=0 	    #boolean
soft_limits=0 	        #boolean
hard_limits=0           #boolean
homing_cycle=1 	        #boolean
homing_dir_invert=0 	#mask
homing_feed=25.000 	    #mm/min
homing_seek=500.000 	#mm/min
homing_debounce=250 	#milliseconds
homing_pull_off=1.000 	#mm
max_spindle_speed=1000. #RPM
min_spindle_speed=0. 	#RPM
laser_mode=0 	        #boolean
x_steps=250.000 	    #mm
y_steps=250.000 	    #mm
z_steps=250.000 	    #mm
x_max_rate=500.000 	    #mm/min
y_max_rate=500.000 	    #mm/min
z_max_rate=500.000      #mm/min
x_acceleration=10.000 	#mm/sec^2
y_acceleration=10.000 	#mm/sec^2
z_accleration=10.000 	#mm/sec^2
x_max_travel=200.000 	#mm
y_max_travel=200.000 	#mm
z_max_travel=200.000 	#mm