import gpiozero
import time
import threading

def handler():
    activity_led = gpiozero.DigitalOutputDevice('BOARD15', active_high=False, initial_value=False)
    while True:
        if activity_led.value:
            activity_led.off()
        else:
            activity_led.on()
        time.sleep(0.5)

threading.Thread(target=handler).start()

