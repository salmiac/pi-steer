use std::error::Error;

pub struct PressureSensor {
    enabled: bool,
    p_multiplier: f32,
    p_add: f32,
}

impl PressureSensor {
    pub fn new(enabled: bool, p_multiplier: f32, p_add: f32) -> Result<Self, Box<dyn Error>> {
        Ok(PressureSensor { 
            enabled,
            p_multiplier, 
            p_add 
        })
    }

    pub fn pressure(&mut self, voltage: f32) -> f32 {
        if self.enabled {
            voltage * self.p_multiplier + self.p_add
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
        println!("read pressure: {:?}", _pressure_sensor.expect("REASON").pressure(2.5));
    }
}
