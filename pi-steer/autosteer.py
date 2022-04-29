import time
import sys
import getopt
import gpiozero
import pi_steer.imu
import pi_steer.agio
import pi_steer.settings
import pi_steer.motor_control
import pi_steer.was
import pi_steer.debug as db


def main(argv):
    work_switch = gpiozero.DigitalInputDevice(13, pull_up=True)

    try:
        options, arguments = getopt.getopt(argv, "d")
    except getopt.GetoptError:
        pass

    print('options', argv, options)
    debug = False
    if '-d' in argv:
        # Debug log file
        print('Debug on')
        debug = True

    imu = pi_steer.imu.IMU(debug=debug)
    settings = pi_steer.settings.Settings(debug=False)
    was = pi_steer.was.WAS(settings, debug=False)
    motor_control = pi_steer.motor_control.MotorControl(settings, debug=False)
    agio = pi_steer.agio.AgIO(settings, motor_control, debug=False)

    blinker = 0
    if debug:
        db.write('Start loop.')

    while True:
        blinker += 1
        imu_reading = imu.read()
        wheel_angle = was.read()

        if imu_reading is not None and imu_reading[0] is not None and wheel_angle is not None:
            (heading, roll, pitch) = imu_reading
            motor_control.update_motor(wheel_angle)
            if motor_control.switch.value:
                switch = 0b1111_1101
            else:
                switch = 0b1111_1111
            if work_switch.value == 0:
                switch &= 0b1111_1110
            
            agio.from_autosteer(wheel_angle, heading, roll, switch, motor_control.pwm_display())

        else:
            agio.alive()

        time.sleep(0.01)
        if blinker % 32 == 0:
            if debug:
                db.write('.')


if __name__ == '__main__':
    try:
        main(sys.argv[1:])
    except KeyboardInterrupt as e:
        print(e)
        sys.exit(0)

