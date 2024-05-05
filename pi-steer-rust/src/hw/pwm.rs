use rppal::gpio::{Gpio, OutputPin};
use rppal::pwm::{Channel, Polarity, Pwm};

pub struct PwmControl {
    pwm: Pwm,
    direction_pin: OutputPin,
}

impl PwmControl {
    pub fn new(direction_gpio: u8) -> Self{
        let pwm = Pwm::with_frequency(Channel::Pwm0, 8000.0, 0.0, Polarity::Normal, true).unwrap();
        let gpio = Gpio::new().unwrap();
        let direction_pin = gpio.get(direction_gpio).unwrap().into_output(); // Example direction control

        PwmControl {
            pwm,
            direction_pin,
        }
    }

    pub fn set(&mut self, direction: bool, pwm_value: f64) {
        self.direction_pin.write(if direction { rppal::gpio::Level::High } else { rppal::gpio::Level::Low });
        self.pwm.set_duty_cycle(pwm_value / 100.0).unwrap(); // Assuming the duty cycle is set as a percentage
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    use std::thread;
    use std::time::{Duration};

    #[test]
    fn pwm() {
        let mut pwm_control = PwmControl::new(16);
        for n in 1..255{
            thread::sleep(Duration::from_millis(50));
            pwm_control.set(true, f64::from(n));
        }
        for n in 1..255{
            thread::sleep(Duration::from_millis(50));
            pwm_control.set(false, f64::from(n));
        }
        pwm_control.set(true, 0.0);
    }
}

