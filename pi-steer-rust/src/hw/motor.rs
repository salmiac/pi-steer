use std::sync::{Arc, Mutex};
use rppal::gpio::{Gpio, InputPin};

use crate::config::settings::Settings;

const ANGLE_GAIN: f32 = 1.0; // 10 degrees = full power * gain %

pub struct MotorControl {
    pub switch: InputPin,
    running: bool,
    target_angle: f32,
    ok_to_run: bool,
    settings: Arc<Mutex<Settings>>,
    debug: bool
}

impl MotorControl {
    pub fn new(settings: Arc<Mutex<Settings>>, debug: bool) -> Self {
        let gpio = Gpio::new().unwrap();
        let switch = gpio.get(27).unwrap().into_input_pullup();
        
        MotorControl {
            switch,
            running: false,
            target_angle: 0.0,
            ok_to_run: false,
            settings,
            debug
        }
    }

    fn calculate_pwm(&mut self, wheel_angle: f32) -> (bool, f32){
        let settings = self.settings.lock().unwrap();
        let delta_angle = self.target_angle - wheel_angle;
        let mut pwm_value = delta_angle * settings.gain_p as f32 * ANGLE_GAIN;

        let direction = if pwm_value < 0.0 {
            pwm_value = -pwm_value;
            settings.invert_steer
        } else {
            !settings.invert_steer
        };

        if pwm_value > settings.high_pwm as f32 / 2.55 {
            pwm_value = settings.high_pwm as f32 / 2.55;
        }

        if pwm_value < settings.min_pwm as f32 / 2.55 {
            pwm_value = settings.min_pwm as f32 / 2.55;
        }
        drop(settings);

        (direction, pwm_value)
    }

    pub fn update_motor(&mut self, wheel_angle: f33) -> (bool, f32) {
        if self.switch.is_low() && !self.running && self.ok_to_run {
            self.running = true;
            if self.debug {
                println!("Start motor");
            }
        }

        if !self.ok_to_run || self.switch.is_high() && self.running {
            self.running = false;
            if self.debug {
                println!("Stop motor");
            }
        }

        let mut pwm_value = 0.0;
        let mut direction = false;
        if self.running {
            (direction, pwm_value) = self.calculate_pwm(wheel_angle);
            if self.debug {
                println!("PWM {}", pwm_value);
            }
        }

        (direction, pwm_value)
    }

    pub fn set_control(&mut self, steer_angle: f32, status: bool) {
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
        let _motor_control = MotorControl::new(Arc::clone(&settings_arc), true);
    }
}

