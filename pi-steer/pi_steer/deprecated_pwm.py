FREQUENCY = 20000

def write(file, command):
    try:
        with open(file, 'w') as newport:
            newport.write(command)
    except:
        return False
    return True

class PWM():
    def __init__(self):
        write('/sys/class/pwm/pwmchip0/export', '0')
        write('/sys/class/pwm/pwmchip0/pwm0/period', str(int(1000000000/FREQUENCY)) )
        write('/sys/class/pwm/pwmchip0/pwm0/duty_cycle', '0')
        write('/sys/class/pwm/pwmchip0/pwm0/enable', '0')

        write('/sys/class/gpio/export', '25')
        write('/sys/class/gpio/gpio25/direction', 'out')
        write('/sys/class/gpio/gpio25/value', '0')

        self.pwm_value = 0
        self.direction = 0

    def start(self):
        write('/sys/class/pwm/pwmchip0/pwm0/enable', '1')

    def stop(self):
        write('/sys/class/pwm/pwmchip0/pwm0/enable', '0')

    def update(self):
        write('/sys/class/gpio/gpio25/value', str(self.direction))
        write('/sys/class/pwm/pwmchip0/pwm0/duty_cycle', str(int(1000000000/FREQUENCY * self.pwm_value / 100.0)))
