use std::error::Error;
use crate::hw::ads1115::ADS1115;

pub struct PressureSensor {
    enabled: bool,
    device: ADS1115,
    p_multiplier: f32,
    p_add: f32,
}

impl PressureSensor {
    pub fn new(enabled: bool, p_multiplier: f32, p_add: f32) -> Result<Self, Box<dyn Error>> {
        let device = ADS1115::new()?;
        Ok(PressureSensor { 
            enabled,
            device, 
            p_multiplier, 
            p_add 
        })
    }

    pub fn read(&mut self) -> f32 {
        if self.enabled {
            let adc = self.device.read(1).unwrap_or(0.0);
            adc * self.p_multiplier + self.p_add
        }
        else {0.0}
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn p_sensor() {
        let _pressure_sensor = PressureSensor::new(true, 2.51, -1.33);
        println!("read pressure: {:?}", _pressure_sensor.expect("REASON").read());
    }
}
