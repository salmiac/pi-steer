import pi_steer.pwm
import pi_steer.automation_hat as hat
import json

ANGLE_GAIN = 0.1 # 10 degrees = full power * gain %

def get_switch():
    if hat.input1():
        switch = 0x00
        hat.output3(True)
    else:
        switch = 0xff
        hat.output3(False)
    return switch

class MotorControl(): 
    def __init__(self, settings):
        self.pwm = pi_steer.pwm.PWM()
        self.settings = settings
        self.running = False
        self.value_changed = True
        self.direction = 1 # 1 = right, 0 = left
        self.switch = 0xff
        self.target_angle = 0
        self.ok_to_run = False

    def update_motor(self, wheel_angle):
        self.switch = get_switch() 
        start = False
        stop = False

        if self.switch == 0x00 and not self.running and self.ok_to_run:
            start = True
        if self.running and (self.switch == 0xff or not self.ok_to_run):
            stop = True

        if self.running or start:
            self.calculate_pwm(wheel_angle)
        if stop:
            print('Stop!')
            self.pwm.stop()
            self.pwm.pwm_value = 0
            self.running = False
            return
        if self.value_changed:
            self.value_changed = False
            print('Set: pwm:', self.pwm.pwm_value, ', switch: ', self.switch, ', direction:', self.pwm.direction, ', wheel angle:', wheel_angle)
            self.pwm.update()
            return
        if start:
            print('Start!')
            self.pwm.start()
            self.running = True

    def calculate_pwm(self, wheel_angle):
        delta_angle = self.target_angle - wheel_angle
        pwm = delta_angle * self.settings.settings['gainP'] * ANGLE_GAIN
        if pwm < 0:
            pwm = -pwm
            self.pwm.direction = 0
        else:
            self.pwm.direction = 1
        if pwm > self.settings.settings['highPWM'] / 2.55:
            pwm = self.settings.settings['highPWM'] / 2.55
        if pwm < self.settings.settings['minPWM'] / 2.55:
            pwm = self.settings.settings['minPWM'] / 2.55
        if self.pwm.pwm_value != pwm:
            self.value_changed = True
            self.pwm.pwm_value = pwm

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
        return int(self.pwm.pwm_value * 2.55)
