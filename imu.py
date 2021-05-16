import time
import board

import busio
import adafruit_bno055

import spidev as SPI
import SSD1306

from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont

header = 'Otsikko'

class IMU():
    def __init__(self) -> None:
        self.i2c = busio.I2C(board.SCL, board.SDA)
        self.imu = adafruit_bno055.BNO055_I2C(self.i2c)
        time.sleep(0.1) # short pause after ads1015 class creation recommended
        print('{: ^25s} | {: ^28s} | {: ^25s} | {: ^39s} | {: ^26s} | {: ^22s} | {: ^22s}'.format(
            'Accelerometer (m/s^2)', 'Magnetometer (microteslas)', 'Gyroscope (rad/sec)', 'Euler angle', 'Quaternion', 'Linear acceleration (m/s^2)', 'Gravity (m/s^2)'
        ))
        self.missed_values = 0
        self.tic = time.time()
        self.heading = 0

    def read_all(self):
        """
        print("Accelerometer (m/s^2): {}".format(self.imu.acceleration))
        print("Magnetometer (microteslas): {}".format(self.imu.magnetic))
        print("Gyroscope (rad/sec): {}".format(self.imu.gyro))
        print("Euler angle: {}".format(self.imu.euler))
        print("Quaternion: {}".format(self.imu.quaternion))
        print("Linear acceleration (m/s^2): {}".format(self.imu.linear_acceleration))
        print("Gravity (m/s^2): {}".format(self.imu.gravity))
        """
        (accx, accy, accz) = self.imu.acceleration
        (magx, magy, magz ) = self.imu.magnetic
        (gyrox, gyroy, gyroz) = self.imu.gyro
        (heading, rollx, rolly) = self.imu.euler
        (quat1, quat2, quat3, quat4) = self.imu.quaternion
        (linx, liny, linz) = self.imu.linear_acceleration
        (gravx, gravy, gravz) = self.imu.gravity

        try:
            print("\r{: = 7.2f}, {: = 7.2f}, {: = 7.2f} : {: = 8.2f}, {: = 8.2f}, {: = 8.2f} : {: = 7.2f}, {: = 7.2f}, {: = 7.2f} : Head {:6.2f} rollx {: = 7.2f} rolly {: = 7.2f} : {: = 5.2f}, {: = 5.2f}, {: = 5.2f}, {: = 5.2f} :  {: = 7.2f}, {: = 7.2f}, {: = 7.2f}  : {: = 6.2f}, {: = 6.2f}, {: = 6.2f} : miss {: =3d}".format(
                accx, accy, accz,
                magx, magy, magz,
                gyrox, gyroy, gyroz,
                heading, rollx, rolly,
                quat1, quat2, quat3, quat4,
                linx, liny, linz,
                gravx, gravy, gravz,
                self.missed_values
            ), end='')
            if heading < 0 or heading > 360:
                raise TypeError
            toc = time.time()
            print(' {: 5.3f}'.format(toc - self.tic), end='')
            self.missed_values = 0
            self.tic = toc
            print(' {: = 7.2f}'.format(heading - self.heading), end='')
            self.heading = heading
        except TypeError:
            self.missed_values += 1
    
    def euler(self):
        return self.imu.euler

class DISP():
    def __init__(self) -> None:
        # Raspberry Pi pin configuration:
        RST = 19
        # Note the following are only used with SPI:
        DC = 16
        bus = 0
        device = 0

        # 128x64 display with hardware SPI:
        self.disp = SSD1306.SSD1306(RST, DC, SPI.SpiDev(bus,device))

        # Initialize library.
        self.disp.begin()

        # Clear display.
        self.disp.clear()
        self.disp.display()

        # Create blank image for drawing.
        # Make sure to create image with mode '1' for 1-bit color.
        self.width = self.disp.width
        self.height = self.disp.height
        self.image = Image.new('1', (self.width, self.height))

        # Get drawing object to draw on image.
        self.draw = ImageDraw.Draw(self.image)

        # Draw a black filled box to clear the image.
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

        # Draw some shapes.
        # First define some constants to allow easy resizing of shapes.
        padding = 1
        top = padding
        x = padding
        # Load default font.
        self.font = ImageFont.load_default()

        # Alternatively load a TTF font.
        # Some other nice fonts to try: http://www.dafont.com/bitmap.php
        #font = ImageFont.truetype('Minecraftia.ttf', 8)

        self.lines = [header]

    def clear(self):
        self.draw.rectangle((0,0,self.width,self.height), outline=0, fill=0)

    def print_lines(self):
        self.clear()
        line_number = 0
        for line in self.lines:
            self.print_in_line(line, line_number)
            line_number += 1
        self.display()
        self.lines = [header]

    def print_in_line(self, text, line=0):
        margin = 3
        self.draw.text((margin, line * 10 + margin), text, font=self.font, fill=255)
        self.display()

    def display(self):
        # Display image.
        self.disp.image(self.image)
        self.disp.display()


def main():
    imu = IMU()
    disp = DISP()
    try:
        while True:
            imu.read_all()
            """
            disp.lines.append('accl: ' + str(imu.imu.acceleration) + ' magn: ' + str(imu.imu.magnetic))
            disp.lines.append('gyro: ' + str(imu.imu.gyro) + ' eule: ' + str(imu.imu.euler))
            disp.lines.append('quar: ' + str(imu.imu.quaternion) + ' line: ' + str(imu.imu.linear_acceleration))
            disp.lines.append('grav: ' + str(imu.imu.gravity))
            disp.print_lines()
            """
            time.sleep(0.001)
    except KeyboardInterrupt:
        pass

if __name__ == "__main__":
    main()
