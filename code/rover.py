import RPi.GPIO as GPIO
import math
import xbox
import time
import json
from throttle import throttle

# define joystick
joy = xbox.Joystick()

# send message to console
class msgOut:
    def __init__(self,message):
        self.msg = {
            "type": "session_log",
            "session_log": {
                "body": message,
                "created_at": time.time()
            }

        }

    def send(self):
        j = json.dumps(self.__dict__)
        print(j)

class statusOut:
    def __init__(self,**kwargs):
        self.status = {
            "type": "vehicle_output",
            "vehicle_output": {
            }
        }
        for key, value in kwargs.items():
            self.status["vehicle_output"][key] = value

    @throttle(1)
    def send(self):
        j = json.dumps(self.__dict__)
        print(j)

# define pins
GPIO_LED_RED    = 22    # armed indicator
GPIO_LED_YELLOW = 27    # unarmed indicator
GPIO_LED_GREEN  = 23    # accelerator indicator
GPIO_SERVO_PIN  = 25    # front wheels steering

# define strings
message_arm     = "Press 'START' to arm or 'B' to end program"
message_disarm  = "Press 'BACK' to disarm"

# set GPIO naming mode
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# prepare pins
GPIO.setup(GPIO_LED_RED, GPIO.OUT)
GPIO.setup(GPIO_LED_YELLOW, GPIO.OUT)
GPIO.setup(GPIO_LED_GREEN, GPIO.OUT)
GPIO.setup(GPIO_SERVO_PIN, GPIO.OUT)

# update throttle
def updatePWM(pwm, value):
    duty = float(value)
    pwm.ChangeDutyCycle(duty)

# find throttle from trigger value
def throttleFromTrigger(trigger_value): # 0.0 to 1.0
        throttle = 0.0
        if trigger_value > 0.0 and trigger_value <= 1.0:
            throttle = trigger_value * 100
        return throttle

# find servo angle
def angleFromX(x):
    angle = 0.0
    x = x / 2
    if x >= 0.0:
        angle = 90.0 * (1.0 - x)            # right turn
    elif x < 0.0:
        angle = 90.0 * (-1.0 * x) + 90.0    # left turn
    return angle

if __name__ == '__main__':

    # define initial values
    running = True
    armed   = False

    # set LED initial states to off
    led_state_red       = GPIO.LOW
    led_state_yellow    = GPIO.LOW

    # prep pwm
    pwm_led_green       = GPIO.PWM(GPIO_LED_GREEN, 100)
    pwm_servo           = GPIO.PWM(GPIO_SERVO_PIN, 100)
    pwm_led_green_init  = False
    pwm_servo_init      = False

    # print initial arming instructions
    msgOut(message_arm).send()

    while running: 

        # update LEDs
        GPIO.output(GPIO_LED_RED, led_state_red)
        GPIO.output(GPIO_LED_YELLOW, led_state_yellow)

        # grab inputs
        input_right_trigger                     = joy.rightTrigger()
        input_left_stick_x, input_left_stick_y  = joy.leftStick()
        input_back                              = joy.Back()
        input_start                             = joy.Start()
        input_b                                 = joy.B()

        # send current status
        statusOut(armed = armed, input_right_trigger = input_right_trigger, input_left_stick_x  = input_left_stick_y).send()

        # check for armed status
        if armed == True:

            # set LED warning state
            led_state_red       = GPIO.HIGH
            led_state_yellow    = GPIO.LOW

            # disarm if BACK is pressed
            if input_back:
                armed = False
                time.sleep(0.1)
                msgOut(message_arm).send()

            # start components
            if not pwm_led_green_init:
                pwm_led_green.start(0)
                pwm_led_green_init = True
            if not pwm_servo_init:
                pwm_servo.start(5)
                pwm_servo_init = True

            # convert inputs into appropriate values
            throttle    = throttleFromTrigger(input_right_trigger)
            servo_angle = angleFromX(input_left_stick_x)

            # update green led
            updatePWM(pwm_led_green, throttle)

            # update servo
            servo_angle_safe = servo_angle / 10.0 + 2.5
            updatePWM(pwm_servo, servo_angle_safe)

        else :

            # power down components
            if pwm_led_green_init:
                pwm_led_green.stop()
                pwm_led_green_init = False
            if pwm_servo_init:
                servo_angle = 90
                servo_angle_safe = servo_angle / 10.0 + 2.5
                updatePWM(pwm_servo, servo_angle_safe)
                # pwm_servo.stop()
                # pwm_servo_init = False

            # set LED low-warning state
            led_state_red       = GPIO.LOW
            led_state_yellow    = GPIO.HIGH

            # arm if 'START' is pressed
            if input_start:
                armed = True
                time.sleep(0.1)
                msgOut(message_disarm).send()

            # stop running if 'B' is pressed
            if input_b:
                running = False

    msgOut('Closing joystick').send()
    joy.close()
    msgOut('Cleaning up GPIO').send()
    GPIO.cleanup()
    msgOut('Program ended safely').send()





