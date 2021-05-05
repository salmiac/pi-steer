import time
import sys
import json
import pi_steer.imu
import pi_steer.agio
import pi_steer.settings
import pi_steer.motor_control
from pi_steer import was

def main():
    imu = pi_steer.imu.IMU()
    settings = pi_steer.settings.Settings()
    agio = pi_steer.agio.AgIO(settings)
    motor_control = pi_steer.motor_control.MotorControl(settings)

    while True:
        (heading, roll, yawn) = imu.euler()
        wheel_angle = was.angle()

        if heading is None or roll is None or yawn is None:
            motor_control.update_motor(wheel_angle)
            continue
        # print('Euler: ', heading, roll, yawn)

        (pgn, payload) = agio.read()
        if pgn is not None:
            if pgn == 0xfc:
                settings.settings = payload
                settings.save_settings()
            if pgn == 0xfe:
                motor_control.set_control(payload)
        motor_control.update_motor(wheel_angle)
        agio.alive()
        switch = motor_control.switch
        pwm_display = motor_control.pwm_display()
        heading = 0 # Disable heading
        agio.from_autosteer(wheel_angle, heading, roll, switch, pwm_display)

        time.sleep(0.01)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print(e)
        # pwm.stop()
        # GPIO.cleanup()
        sys.exit(0)

