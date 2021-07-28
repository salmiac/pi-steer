import time
import pi_steer.cytron_md13s as pwm


print('Start PWM test\n')

while True:
    print('\rStop               ', end='')
    pwm.stop()
    time.sleep(0.5)
    pwm.start()
    for n in range(100):
        print('\r', n, ' % Right   ', end='')
        pwm.update(n, 1)
        time.sleep(0.01)
    for n in range(100, -1, -1):
        print('\r', n, ' % Right   ', end='')
        pwm.update(n, 1)
        time.sleep(0.01)
    for n in range(100):
        print('\r', n, ' % Left   ', end='')
        pwm.update(n, 0)
        time.sleep(0.01)
    for n in range(100, -1, -1):
        print('\r', n, ' % Left   ', end='')
        pwm.update(n, 0)
        time.sleep(0.01)
