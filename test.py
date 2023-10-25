print("hello world")

import OPi.GPIO as GPIO
import time


# Note that we use SUNXI mappings here because its way less confusing than
# board mappsings. For example, these are all the same pin:
# sunxi: PD15 (the label on the board)
# board: 29
# gpio:  7

GPIO.setmode(GPIO.SUNXI)
GPIO.setwarnings(False)
GPIO.setup('PD15', GPIO.OUT)

while True:
    GPIO.output('PD15', GPIO.HIGH)
    time.sleep(1)
    GPIO.output('PD15', GPIO.LOW)
    time.sleep(1)