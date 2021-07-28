import gpiozero

FREQUENCY = 20000

pwm = gpiozero.PWMOutputDevice('BOARD32', active_high=True, initial_value=0, frequency=FREQUENCY)
pwm_direction = gpiozero.DigitalOutputDevice('BOARD22', active_high=True, initial_value=True)

def start():
    pwm.on()

def stop():
    pwm.off()

def update(value, direction):
    pwm.value = value / 100.0
    pwm_direction.value = direction
