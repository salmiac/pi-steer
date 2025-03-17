use rppal::gpio::{Gpio, InputPin, OutputPin};
use std::time::{Duration, Instant};

const NOZZLE_CONSTANT: f32 = 2.3095; // Reverse engineered constant.
const PRESSURE_DIFFERENCE_ACCURACY: f32 = 0.01; // relative pressure difference
const PRESSURE_DIFFERENCE_FULL_CONTROL: f32 = 0.2; // 20 % relative pressure difference to adjust pressure without a break.
const PRESSURE_WAIT_TIME: u64 = 500; // milliseconds
const ON_TIME_MULTIPLIER: f32 = 1000.0; // milliseconds

pub struct PressureControl {
    pub enabled: bool,
    pub active: bool,
    pub nominal_pressure: f32,
    pub target_pressure: f32,
    pub current_pressure: f32,
    pub constant_pressure: bool,
    up_gpio: OutputPin,
    down_gpio: OutputPin,
    pub nozzle_size: f32,
    pub nozzle_spacing: f32, // m
    pub litres_per_ha: f32,
    pub min_pressure: f32, // bar
    pub max_pressure: f32, // bar
    on_timer: Instant,
    off_timer: Instant,
    control_on: bool,
    pub speed: f32,
    pub boom_gpio: InputPin
}

impl PressureControl {
    pub fn new(enabled: bool, up_gpio_pin: u8, down_gpio_pin: u8, boom_gpio_pin: u8) -> Self {
        let gpio = Gpio::new().unwrap();
        let boom_gpio = gpio.get(boom_gpio_pin).expect("Failed to access GPIO pin").into_input_pullup();
        let mut up_gpio = gpio.get(up_gpio_pin).unwrap().into_output();
        let mut down_gpio = gpio.get(down_gpio_pin).unwrap().into_output();
        up_gpio.set_high();
        down_gpio.set_high();
    PressureControl {
            enabled,
            active: false,
            nominal_pressure: 0.0,
            target_pressure: 0.0,
            current_pressure: 0.0,
            constant_pressure: true,
            up_gpio: up_gpio,
            down_gpio: down_gpio,
            nozzle_size: 0.3,
            nozzle_spacing: 0.5,
            litres_per_ha: 0.0,
            min_pressure: 1.0,
            max_pressure: 8.0,
            on_timer: Instant::now(),
            off_timer: Instant::now(),
            control_on: false,
            speed: 0.0,
            boom_gpio
        }
    }

    pub fn update_control(&mut self) {
        let relative_pressure_difference = (1.0 - self.current_pressure/self.target_pressure).abs();
        if relative_pressure_difference < PRESSURE_DIFFERENCE_ACCURACY {
            self.off();
            return
        }

        if self.enabled && self.active {
            if relative_pressure_difference > PRESSURE_DIFFERENCE_FULL_CONTROL {
                self.set_control();
                self.reset_timers();
            }
            else {
                if self.control_on {
                    let on_wait: u64 = (relative_pressure_difference * ON_TIME_MULTIPLIER) as u64;
                    if self.on_timer.elapsed() < Duration::from_millis(on_wait) {
                        self.set_control();
                    }
                    else { self.off(); }
                }
                else {
                    if self.off_timer.elapsed() > Duration::from_millis(PRESSURE_WAIT_TIME) {
                        self.set_control();
                        self.reset_timers();
                    }
                }
    
            }
        }
        else {
            self.off();
        }
    }

    fn set_control(&mut self) {
        if self.target_pressure > self.current_pressure {
            self.up();
        }
        else { self.down(); }
        self.control_on = true;
    }

    fn up(&mut self) {
        self.up_gpio.set_low();
        self.down_gpio.set_high();
    }

    fn down(&mut self) {
        self.up_gpio.set_high();
        self.down_gpio.set_low();
    }

    fn off(&mut self) {
        self.up_gpio.set_high();
        self.down_gpio.set_high();
        self.control_on = false;
        self.reset_timers();
    }

    fn reset_timers(&mut self) {
        self.on_timer = Instant::now();
        self.off_timer = Instant::now();

    }

    // km/h
    pub fn set_speed(&mut self, speed: f32) {
        if self.enabled && self.active && !self.constant_pressure 
        {
            // let litres_min = speed * self.litres_ha * self.nozzle_spacing / 600.0;
            // let pressure = (litres_min / (NOZZLE_CONSTANT * self.nozzle_size)).powi(2);
            self.target_pressure = ( (speed * self.litres_per_ha * self.nozzle_spacing) / (NOZZLE_CONSTANT * self.nozzle_size * 600.0)).powi(2);
            // self.update_control(self.target_pressure);
        }
        self.speed = speed;
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn motortest() {
        let _pressure_control = PressureControl::new(true,  20, 1, 8);
    }
}

