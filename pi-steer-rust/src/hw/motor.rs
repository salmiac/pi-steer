use rppal::gpio::{Gpio, InputPin, OutputPin};
use rppal::pwm::{Channel, Polarity, Pwm};
// use std::{error::Error};
// use std::cell::RefCell;
// use std::rc::Rc;
use std::sync::{Arc, Mutex};

use crate::config::settings::Settings;

const ANGLE_GAIN: f64 = 1.0; // 10 degrees = full power * gain %

pub struct MotorControl {
    pwm: Pwm,
    pub switch: InputPin,
    running: bool,
    direction_pin: OutputPin, // Assuming a GPIO pin controls the direction
    target_angle: f64,
    ok_to_run: bool,
    pub pwm_value: f64,
    settings: Arc<Mutex<Settings>>,
}

impl MotorControl {
    pub fn new(settings: Arc<Mutex<Settings>>) -> Self {
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
            pwm_value: 0.0,
            settings,
        }
    }

    fn calculate_pwm(&mut self, wheel_angle: f64) {
        let settings = self.settings.lock().unwrap();
        let delta_angle = self.target_angle - wheel_angle;
        self.pwm_value = delta_angle * settings.gain_p as f64 * ANGLE_GAIN;

        let direction = if self.pwm_value < 0.0 {
            self.pwm_value = -self.pwm_value;
            settings.invert_steer
        } else {
            !settings.invert_steer
        };

        if self.pwm_value > settings.high_pwm as f64 / 2.55 {
            self.pwm_value = settings.high_pwm as f64 / 2.55;
        }

        if self.pwm_value < settings.min_pwm as f64 / 2.55 {
            self.pwm_value = settings.min_pwm as f64 / 2.55;
        }

        self.pwm.set_duty_cycle(self.pwm_value / 100.0).unwrap(); // Assuming the duty cycle is set as a percentage
        self.direction_pin.write(if direction { rppal::gpio::Level::High } else { rppal::gpio::Level::Low });
    }

    pub fn update_motor(&mut self, wheel_angle: f64) {
        if self.switch.is_high() && !self.running && self.ok_to_run {
            self.running = true;
            // Optionally log "Start!"
        }

        if self.running {
            self.calculate_pwm(wheel_angle);
        }

        if !self.ok_to_run || self.switch.is_low() && self.running {
            self.running = false;
            self.pwm.disable().unwrap();
            // Optionally log "Stop!"
        }
    }

    pub fn set_control(&mut self, steer_angle: f64, status: bool) {
        self.target_angle = steer_angle;
        self.ok_to_run = status;
    }        
}


#[cfg(test)]
mod tests {
    // use super::*;

    #[test]
    fn motortest() {

        // let settings = Settings::default(); // Assume you have some default or configured settings
        // let mut motor_control = MotorControl::new(Channel::Pwm0, 27, 22, &settings)?; // Example pins
        
        // motor_control.update_motor(0.0, &settings); // Replace 0.0 with actual wheel angle from sensor
    }
}

