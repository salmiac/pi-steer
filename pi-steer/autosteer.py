import time
import sys
import threading
import pi_steer.imu as imu
import pi_steer.agio
import pi_steer.settings
import pi_steer.motor_control
import pi_steer.was
import pi_steer.activity_led

settings = pi_steer.settings.Settings()
was = pi_steer.was.WAS(settings)
agio = pi_steer.agio.AgIO(settings)
motor_control = pi_steer.motor_control.MotorControl(settings, was)

def agio_reader():
    while True:
        (pgn, payload) = agio.read()
        if pgn is not None:
            if pgn == 0xfb:
                settings.settings.update(payload)
                settings.save_settings()
            if pgn == 0xfc:
                settings.settings.update(payload)
                settings.save_settings()
            if pgn == 0xfe:
                motor_control.set_control(payload)

def main():
    threading.Thread(target=agio_reader).start()

    while True:
        # print('\r H {: = 7.2f} R {: = 7.2f}'.format(imu.heading, imu.roll), end='')
        # agio.alive()
        if motor_control.switch.value:
            switch = 0x00
        else:
            switch = 0xff
        heading = imu.heading # 0 # Disable heading
        roll = imu.roll # 0
        
        agio.from_autosteer(was.angle, heading, roll, switch, motor_control.pwm_display())
        time.sleep(0.02)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt as e:
        print(e)
        # pwm.stop()
        # GPIO.cleanup()
        sys.exit(0)
