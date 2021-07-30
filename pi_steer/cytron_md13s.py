import gpiozero

FREQUENCY = 300

pwm = gpiozero.PWMOutputDevice('BOARD32', active_high=True, initial_value=0, frequency=FREQUENCY)
pwm_direction = gpiozero.DigitalOutputDevice('BOARD22', active_high=True, initial_value=True)

def start():
    pwm.on()

def stop():
    pwm.off()

def update(value, direction):
    pwm.value = value / 100.0
    # print('PWM', pwm.value)
    pwm_direction.value = direction
