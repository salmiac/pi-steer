import time

FREQUENCY = 8000

def write(file, command):
    try:
        with open(file, 'w') as newport:
            newport.write(command)
    except Exception as err:
        print('Can not write to ', file, err)
        return False
    return True

write('/sys/class/pwm/pwmchip0/export', '0')
time.sleep(1)
write('/sys/class/pwm/pwmchip0/pwm0/period', str(int(1000000000/FREQUENCY)) )
time.sleep(0.1)
write('/sys/class/pwm/pwmchip0/pwm0/duty_cycle', '0')
time.sleep(0.001)
write('/sys/class/pwm/pwmchip0/pwm0/enable', '0')
time.sleep(0.001)

write('/sys/class/gpio/export', '16')
time.sleep(1)
write('/sys/class/gpio/gpio16/direction', 'out')
time.sleep(0.1)
write('/sys/class/gpio/gpio16/value', '0')
time.sleep(0.001)

def start():
    write('/sys/class/pwm/pwmchip0/pwm0/enable', '1')

def stop():
    write('/sys/class/pwm/pwmchip0/pwm0/enable', '0')

def update(value, direction):
    write('/sys/class/gpio/gpio16/value', str(direction))
    write('/sys/class/pwm/pwmchip0/pwm0/duty_cycle', str(int(1000000000/FREQUENCY * value / 100.0)))


'''
The following code is much cleaner, but it uses software PWM and higher frequencies cannot be used.
It is here jus as a reminder.

import gpiozero
FREQUENCY = 300

pwm_direction = gpiozero.DigitalOutputDevice('BOARD22', active_high=True, initial_value=True)
pwm = gpiozero.PWMOutputDevice('BOARD32', active_high=True, initial_value=0, frequency=FREQUENCY)

def start():
    pwm.on()

def stop():
    pwm.off()

def update(value, direction):
    pwm.value = value / 100.0
    # print('PWM', pwm.value)
    pwm_direction.value = direction
'''
