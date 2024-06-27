import RPi.GPIO as GPIO
import time

PINS={'L_A':2, 'L_B':3 , 'R_A':4, 'R_B':17, 'SC_A':27, 'SC_B':22, 'PWM':18}

GPIO.setmode(GPIO.BCM)

for key in PINS.keys():
  GPIO.setup(PINS[key], GPIO.OUT)
PWM = GPIO.PWM ( PINS['PWM'], 50 )
PWM.start(50)

def motor(direction, power=50):
  PWM.ChangeDutyCycle( power )
  #進行方向はテンキーと同じ配列
  # 0:前進, 1:後進, 2:左旋回, 3:右��回
  if direction == 0:
    GPIO.output(PINS['L_A'], GPIO.HIGH)
    GPIO.output(PINS['L_B'], GPIO.LOW)
    GPIO.output(PINS['R_A'], GPIO.HIGH)
    GPIO.output(PINS['R_B'], GPIO.LOW)
  elif direction == 1:
    GPIO.output(PINS['L_A'], GPIO.LOW)
    GPIO.output(PINS['L_B'], GPIO.HIGH)
    GPIO.output(PINS['R_A'], GPIO.LOW)
    GPIO.output(PINS['R_B'], GPIO.HIGH)

if __name__ == '__main__':
  try:
    while True:
      for i in range(10):
        motor(0)
        time.sleep(1)
        motor(1)
        time.sleep(1)
  except KeyboardInterrupt:
    GPIO.cleanup()