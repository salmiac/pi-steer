import time
import sys
import pi_steer.imu as imu
import pi_steer.agio
import pi_steer.settings
import pi_steer.motor_control
import pi_steer.was
import pi_steer.activity_led

def main():
    settings = pi_steer.settings.Settings()
    was = pi_steer.was.WAS(settings)
    agio = pi_steer.agio.AgIO(settings)
    motor_control = pi_steer.motor_control.MotorControl(settings)

    while True:
        # print('\r H {: = 7.2f} R {: = 7.2f}'.format(imu.heading, imu.roll), end='')
        (pgn, payload) = agio.read()
        if pgn is not None:
            if pgn == 0xfc:
                settings.settings = payload
                settings.save_settings()
            if pgn == 0xfe:
                motor_control.set_control(payload)
        (switch, pwm) = motor_control.update_motor(was.angle)
        # agio.alive()
        if switch:
            switch = 0x00
        else:
            switch = 0xff
        pwm_display = int(pwm * 2.55)
        # heading = 0 # Disable heading
        # roll = 0
        agio.from_autosteer(was.angle, imu.heading, imu.roll, switch, pwm_display)

        time.sleep(0.01)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print(e)
        # pwm.stop()
        # GPIO.cleanup()
        sys.exit(0)

