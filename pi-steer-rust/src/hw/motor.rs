use rppal::gpio::{Gpio, InputPin, OutputPin};
use rppal::pwm::{Channel, Polarity, Pwm};
// use std::{error::Error};
// use std::cell::RefCell;
// use std::rc::Rc;
use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

use crate::config::settings::Settings;

const ANGLE_GAIN: f64 = 1.0; // 10 degrees = full power * gain %

pub struct MotorControl {
    pwm: Pwm,
    pub switch: InputPin,
    running: bool,
    direction_pin: OutputPin, // Assuming a GPIO pin controls the direction
    target_angle: f64,
    ok_to_run: bool,
    settings: Arc<Mutex<Settings>>,
    debug: bool
}

impl MotorControl {
    pub fn new(settings: Arc<Mutex<Settings>>, debug: bool) -> Self {
        let pwm = Pwm::with_frequency(Channel::Pwm0, 8000.0, 0.0, Polarity::Normal, true).unwrap();
        let gpio = Gpio::new().unwrap();
        let switch = gpio.get(27).unwrap().into_input_pullup();
        let direction_pin = gpio.get(16).unwrap().into_output(); // Example direction control
        
        MotorControl {
            pwm,
            switch,
            running: false,
            direction_pin,
            target_angle: 0.0,
            ok_to_run: false,
            settings,
            debug
        }
    }

    fn calculate_pwm(&mut self, wheel_angle: f64) -> f64{
        let settings = self.settings.lock().unwrap();
        let delta_angle = self.target_angle - wheel_angle;
        let mut pwm_value = delta_angle * settings.gain_p as f64 * ANGLE_GAIN;

        let direction = if pwm_value < 0.0 {
            pwm_value = -pwm_value;
            settings.invert_steer
        } else {
            !settings.invert_steer
        };

        if pwm_value > settings.high_pwm as f64 / 2.55 {
            pwm_value = settings.high_pwm as f64 / 2.55;
        }

        if pwm_value < settings.min_pwm as f64 / 2.55 {
            pwm_value = settings.min_pwm as f64 / 2.55;
        }
        drop(settings);

        self.set_motor_pwm(direction, pwm_value);
        pwm_value
    }

    pub fn set_motor_pwm(&mut self, direction: bool, pwm_value: f64) {
        if self.debug {
            println!("Direction: {}, pwm: {}", direction, pwm_value);
        }
        self.direction_pin.write(if direction { rppal::gpio::Level::High } else { rppal::gpio::Level::Low });
        self.pwm.set_duty_cycle(pwm_value / 100.0).unwrap(); // Assuming the duty cycle is set as a percentage
        thread::sleep(Duration::from_millis(100));
    }

    pub fn update_motor(&mut self, wheel_angle: f64) -> f64 {
        if self.switch.is_low() && !self.running && self.ok_to_run {
            self.running = true;
            if self.debug {
                println!("Start motor");
            }
        }

        let mut pwm_value = 0.0;
        if self.running {
            pwm_value = self.calculate_pwm(wheel_angle);
            if self.debug {
                println!("PWM {}", pwm_value);
            }
            thread::sleep(Duration::from_millis(50));
        }

        if !self.ok_to_run || self.switch.is_high() && self.running {
            self.running = false;
            self.pwm.disable().unwrap();
            if self.debug {
                println!("Stop motor");
            }
        }
        pwm_value
    }

    pub fn set_control(&mut self, steer_angle: f64, status: bool) {
        self.target_angle = steer_angle;
        self.ok_to_run = status;
        if self.debug{
            println!("Target {}, status  {}", self.target_angle, self.ok_to_run);
        }
    }        
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn motortest() {
        let settings_arc = Arc::new(Mutex::new(Settings::new(true)));
        let mut motor_control = MotorControl::new(Arc::clone(&settings_arc), true);
        for n in 1..255{
            thread::sleep(Duration::from_millis(50));
            motor_control.set_motor_pwm(true, f64::from(n));
        }
        for n in 1..255{
            thread::sleep(Duration::from_millis(50));
            motor_control.set_motor_pwm(false, f64::from(n));
        }
        motor_control.set_motor_pwm(true, 0.0);
    }
}

