import time
import threading
import pi_steer.pwm_motor as pwm
import pi_steer.debug as db
import gpiozero

ANGLE_GAIN = 1 # 10 degrees = full power * gain %

class MotorControl(): 
    def __init__(self, settings, debug=False):
        self.settings = settings
        self.debug = debug
        self.running = False
        self.value_changed = True
        self.direction = 1 # 1 = right, 0 = left
        self.target_angle = 0
        self.ok_to_run = False
        self.switch = gpiozero.DigitalInputDevice('BOARD13', pull_up=True, active_state=None, bounce_time=None)
        self.active_led = gpiozero.DigitalOutputDevice('BOARD15', active_high=False, initial_value=False)
        self.direction_led = gpiozero.DigitalOutputDevice('BOARD24', active_high=False, initial_value=False)
        self.pwm_value = 0

    def calculate_pwm(self, wheel_angle):
        delta_angle = self.target_angle - wheel_angle
        pwm_value = delta_angle * self.settings.settings['gainP'] * ANGLE_GAIN
        if pwm_value < 0:
            pwm_value = -pwm_value
            direction = 1 if self.settings.settings['invertSteer'] else 0
        else:
            direction = 0 if self.settings.settings['invertSteer'] else 1
        if pwm_value > self.settings.settings['highPWM'] / 2.55:
            pwm_value = self.settings.settings['highPWM'] / 2.55
        if pwm_value < self.settings.settings['minPWM'] / 2.55:
            pwm_value = self.settings.settings['minPWM'] / 2.55
        if self.pwm_value != pwm_value or direction != self.direction:
            self.value_changed = True
            self.pwm_value = pwm_value
            self.direction = direction

    def update_motor(self, wheel_angle):
        print('Start motor controller.')
        while True:
            self.moe += 1
            self.active_led.value = self.switch.value
            start = False
            stop = False

            self.was.read()
            if self.switch.value == 1 and not self.running and self.ok_to_run:
                start = True
            if self.running and (self.switch.value == 0 or not self.ok_to_run):
                stop = True

            if self.running or start:
                self.calculate_pwm(wheel_angle)
            if stop:
                if self.debug:
                    db.write('Stop!')
                pwm.stop()
                self.pwm_value = 0
                self.running = False
                continue
            if self.value_changed:
                self.value_changed = False
                if self.debug:
                    db.write('Set: pwm: {}, switch: {}, direction: {}'.format(self.pwm_value, self.switch_active, self.direction))
                pwm.update(self.pwm_value, self.direction)
                self.direction_led.value = self.direction
            if start:
                if self.debug:
                    db.write('Stop!')
                print('Start!')
                pwm.start()
                self.running = True
            time.sleep(0.005)

    def set_control(self, auto_steer_data):
        # auto_steer_data['Speed']
        # auto_steer_data['Status']
        # auto_steer_data['SteerAngle']
        # auto_steer_data['SC']
        self.target_angle = auto_steer_data['SteerAngle']

        if auto_steer_data['Status']:
            self.ok_to_run = True
        else:
            self.ok_to_run = False

    def pwm_display(self):
        return int(self.pwm_value * 2.55)
