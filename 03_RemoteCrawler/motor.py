import RPi.GPIO as GPIO
import time

PNO = 2 

GPIO.setmode(GPIO.BCM)
GPIO.setup(PNO, GPIO.OUT)
try:
    while True:
        GPIO.output(PNO, GPIO.HIGH) # 点灯
        time.sleep(1)
        GPIO.output(PNO, GPIO.LOW) # 消灯
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()
