import RPi.GPIO as GPIO
import time

PINS={'L_F':3, 'L_R':2 , 'R_F':17, 'R_R':4, 'SC_A':27, 'SC_B':22, 'PWM':18}

GPIO.setmode(GPIO.BCM)

start_time = time.time()
prev_command = 0

for key in PINS.keys():
  GPIO.setup(PINS[key], GPIO.OUT)
  GPIO.output(PINS[key], GPIO.LOW)
PWM = GPIO.PWM ( PINS['PWM'], 50 )
PWM.start(50)

def motor(direction, power=50):
  PWM.ChangeDutyCycle( power )
  #進行方向はテンキーと同じ配列
  if direction == 1:
    print("↙")
    GPIO.output(PINS['L_F'], GPIO.LOW)
    GPIO.output(PINS['L_R'], GPIO.LOW)
    GPIO.output(PINS['R_F'], GPIO.HIGH)
    GPIO.output(PINS['R_R'], GPIO.LOW)
  elif direction == 2:
    print("↓")
    GPIO.output(PINS['L_F'], GPIO.LOW)
    GPIO.output(PINS['L_R'], GPIO.HIGH)
    GPIO.output(PINS['R_F'], GPIO.LOW)
    GPIO.output(PINS['R_R'], GPIO.HIGH)
  elif direction == 3:
    print("↘")
    GPIO.output(PINS['L_F'], GPIO.LOW)
    GPIO.output(PINS['L_R'], GPIO.HIGH)
    GPIO.output(PINS['R_F'], GPIO.LOW)
    GPIO.output(PINS['R_R'], GPIO.LOW)
  elif direction == 4:
    print("⟲")
    GPIO.output(PINS['L_F'], GPIO.LOW)
    GPIO.output(PINS['L_R'], GPIO.HIGH)
    GPIO.output(PINS['R_F'], GPIO.HIGH)
    GPIO.output(PINS['R_R'], GPIO.LOW)
  elif direction == 6:
    print("⟳")
    GPIO.output(PINS['L_F'], GPIO.HIGH)
    GPIO.output(PINS['L_R'], GPIO.LOW)
    GPIO.output(PINS['R_F'], GPIO.LOW)
    GPIO.output(PINS['R_R'], GPIO.HIGH)
  elif direction == 7:
    print("↖")
    GPIO.output(PINS['L_F'], GPIO.LOW)
    GPIO.output(PINS['L_R'], GPIO.LOW)
    GPIO.output(PINS['R_F'], GPIO.HIGH)
    GPIO.output(PINS['R_R'], GPIO.LOW)
  elif direction == 8:
    print("↑")
    GPIO.output(PINS['L_F'], GPIO.HIGH)
    GPIO.output(PINS['L_R'], GPIO.LOW)
    GPIO.output(PINS['R_F'], GPIO.HIGH)
    GPIO.output(PINS['R_R'], GPIO.LOW)
  elif direction == 9:
    print("↗")
    GPIO.output(PINS['L_F'], GPIO.HIGH)
    GPIO.output(PINS['L_R'], GPIO.LOW)
    GPIO.output(PINS['R_F'], GPIO.LOW)
    GPIO.output(PINS['R_R'], GPIO.LOW)
  elif direction == 10:
    print("▲")
    GPIO.output(PINS['SC_A'], GPIO.HIGH)
    GPIO.output(PINS['SC_B'], GPIO.LOW)
  elif direction == 11:
    print("▼")
    GPIO.output(PINS['SC_A'], GPIO.LOW)
    GPIO.output(PINS['SC_B'], GPIO.HIGH)
  else:
    print("STOP")
    PWM.ChangeDutyCycle(0)
    GPIO.output(PINS['L_F'], GPIO.LOW)
    GPIO.output(PINS['L_R'], GPIO.LOW)
    GPIO.output(PINS['R_F'], GPIO.LOW)
    GPIO.output(PINS['R_R'], GPIO.LOW)
    GPIO.output(PINS['SC_A'], GPIO.LOW)
    GPIO.output(PINS['SC_B'], GPIO.LOW)

  if prev_command != direction and ( direction <= 9 and direction != 5):
    time.sleep(0.5)
  prev_command = direction

if __name__ == '__main__':
  try:
    while True:
      for i in range(5):
        motor(1)
        time.sleep(1)
        motor(2)
        time.sleep(1)
        motor(3)
        time.sleep(1)
        motor(4)
        time.sleep(1)
        motor(6)
        time.sleep(1)
        motor(7)
        time.sleep(1)
        motor(8)
        time.sleep(1)
        motor(9)
        time.sleep(1)
  except KeyboardInterrupt:
    print('Release GPIO')
    GPIO.output(PINS['L_F'], GPIO.LOW)
    GPIO.output(PINS['L_R'], GPIO.LOW)
    GPIO.output(PINS['R_F'], GPIO.LOW)
    GPIO.output(PINS['R_R'], GPIO.LOW)
    GPIO.output(PINS['SC_A'], GPIO.LOW)
    GPIO.output(PINS['SC_B'], GPIO.LOW)
    GPIO.cleanup()