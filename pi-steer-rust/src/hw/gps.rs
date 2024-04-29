use serialport;
use std::thread;
use std::time::Duration;
use std::io::{BufReader, BufRead};

use crate::communication::agio::Writer;

pub struct GPS {
    // debug: bool,
    // orientation: Arc<Mutex<(f32, f32, f32, bool)>>,
}

// fn build_gga(time: &str, lat: &str, ns: &str, lon: &str, ew: &str, fix: &str, sats: &str, hdop: &str, alt: &str, geoid: &str, age: &str) -> String {
//     let data = format!("GPGGA,{},{},{},{},{},{},{},{},{},M,{},M,{},0000", time, lat, ns, lon, ew, fix, sats, hdop, alt, geoid, alt);
//     let crc: u8 = data.as_bytes().iter().skip(2).fold(0, |acc, &x| acc.wrapping_add(x));
//     format!("${}*{:X}", data, crc)
// }

impl GPS {
    pub fn new(debug: bool, port: String) -> Self {

        thread::spawn(move || Self::reader(debug, port));
        GPS {
            // debug,
            // orientation,
        }
    }

    fn reader(debug: bool, port: String) {
        let writer = Writer::new(false, debug);
        let port_name = format!("/dev/{}", port);
        let baud_rate = 115200;
        if debug { println!("Open serialport") }
        let port = serialport::new(port_name, baud_rate)
            .timeout(Duration::from_millis(100))
            .open()
            .expect("Failed to open serial port");

        let mut reader = BufReader::new(port);

        let mut line = String::new();
        let mut speed: f32 = f32::MAX;
        let mut heading: f32 = 0.0;
        loop {
            match reader.read_line(&mut line) {
                Ok(_) => {
                    let trimmed = line.trim_end();
                    if debug {
                        println!("Read: {}", trimmed); // Optional: output the line to the console
                    }

                    let part: Vec<&str> = trimmed.split(",").collect();
                    if part[0] == "$GNVTG" {
                        let course = part[1];
                        let kph = part[7];
                        if course != "" {
                            heading = course.parse::<f32>().unwrap();
                        }
                        else {
                            heading = 0.0;
                        }
                        if kph != "" {
                            speed = kph.parse::<f32>().unwrap();
                        }
                        else {
                            speed = f32::MAX;
                        }
                    }
                    else if part[0] == "$GNGGA" {
                        if part[6] != "0" && part[6] != "" {
                            let time = part[1];
                            let mut lat = part[2][0..2].parse::<f64>().unwrap() + part[2][2..].parse::<f64>().unwrap() / 60.0;
                            let ns = part[3];
                            if ns == "S" { lat = -lat; }
                            let mut lon = part[4][0..3].parse::<f64>().unwrap() + part[4][3..].parse::<f64>().unwrap() / 60.0;
                            let ew = part[5];
                            if ew == "W" { lon = -lon; }
                            let fix = part[6].parse::<u8>().unwrap();
                            let sat = part[7].parse::<u16>().unwrap();
                            let hdop = part[8].parse::<f32>().unwrap();
                            let alt = part[9].parse::<f32>().unwrap();
                            let geoid = part[11];
                            let age = part[13].parse::<f32>().unwrap();
                            writer.gps(time, lat, ns, lon, ew, fix, sat, hdop, alt, geoid, age, heading, speed);
                        }
                    }
                },
                Err(e) => {
                    if debug {
                        println!("{}", e); // Optional: output the line to the console
                    }
                }
            }
            line.clear();  // Clear the buffer for the next line
        }
        
    }

}


#[cfg(test)]
mod gps {
    use super::*;

    #[test]
    fn gps() {
        let _gps = GPS::new(true, "ttyS0".to_string());
        thread::sleep(Duration::from_millis(5000));
    }
}

