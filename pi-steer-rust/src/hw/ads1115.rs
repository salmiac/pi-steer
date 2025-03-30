use rppal::i2c::I2c;
use std::error::Error;
use std::thread;
use std::time::Duration;

const ADS111X_ADDRESS0: u16 = 0x48;
const CONVERSION_REGISTER: u8 = 0x00;
const CONFIG_REGISTER: u8 = 0x01;
const CONFIG_HIGH: u8 = 0b1000_0001;
const CONFIG_LOW: u8 = 0b1110_0011;
/* Configuration
bit description
15      1b start single conversion
14:12   1xxb channel 0 - 3
11:9    000b FSR = ±6.144V
8       1b Single-shot mode or power-down state 
7:5     111b : 860SPS 
4       0b : Traditional comparator
3       0b : Active low 
2       0b : Nonlatching comparator.
1:0     11b : Disable comparator and set ALERT/RDY pin to high-impedance 
*/

pub struct ADS1115 {
    i2c: I2c,
}

impl ADS1115 {
    pub fn new() -> Result<Self, Box<dyn Error>> {
        let mut i2c = I2c::new()?;
        i2c.set_slave_address(ADS111X_ADDRESS0)?;
        Ok(ADS1115 { i2c })
    }

    pub fn read(&mut self, channel: u8) -> Result<f32, Box<dyn Error>> {
        self.i2c.write(&[CONFIG_REGISTER, ((channel & 0b000_0111) << 4) | CONFIG_HIGH, CONFIG_LOW])?;
        thread::sleep(Duration::from_micros(1000));
        let mut data = [0u8; 2];
        self.i2c.write_read(&[CONVERSION_REGISTER], &mut data)?;
        Ok(i16::from_be_bytes(data) as f32 / 32767.0 * 6.144) // Return voltage
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ads() {
        let mut ads = ADS1115::new();
        println!("ADS read: {:?}", ads.as_mut().expect("REASON").read(0));
        println!("ADS read: {:?}", ads.as_mut().expect("REASON").read(1));
        println!("ADS read: {:?}", ads.as_mut().expect("REASON").read(0));
        println!("ADS read: {:?}", ads.as_mut().expect("REASON").read(1));
        println!("ADS read: {:?}", ads.as_mut().expect("REASON").read(0));
        println!("ADS read: {:?}", ads.as_mut().expect("REASON").read(1));
    }
}
