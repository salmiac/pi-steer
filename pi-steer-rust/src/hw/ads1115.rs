use rppal::i2c::I2c;
use std::{error::Error, thread, time::Duration};

const ADS111X_ADDRESS0: u16 = 0x48;
const CONVERSION_REGISTER: u8 = 0x00;
const CONFIG_REGISTER: u8 = 0x01;
const CONFIGURATION: [u8; 3] = [CONFIG_REGISTER, 0b0100_0010, 0b1010_0011];

pub struct ADS1115 {
    i2c: I2c,
}

impl ADS1115 {
    pub fn new() -> Result<Self, Box<dyn Error>> {
        let mut i2c = I2c::new()?;
        i2c.set_slave_address(ADS111X_ADDRESS0)?;
        i2c.write(&CONFIGURATION)?;
        thread::sleep(Duration::from_millis(100));
        // Optional: Implement debug functionality similar to the Python version
        Ok(ADS1115 { i2c })
    }

    pub fn read(&mut self) -> Result<i16, Box<dyn Error>> {
        let mut data = [0u8; 2];
        self.i2c.write_read(&[CONVERSION_REGISTER], &mut data)?;
        Ok(i16::from_be_bytes(data))
    }
}


#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn ads() {
        let ads = ADS1115::new();
        println!("ADS read: {:?}", ads.expect("REASON").read());
    }
}
