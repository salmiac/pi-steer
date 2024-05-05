use serialport::{self, SerialPort};
use std::thread;
use std::time::Duration;
use std::io::{BufReader, BufRead};
use std::net::UdpSocket;

use crate::communication::agio::Writer;

pub struct GPS {
    // debug: bool,
    // orientation: Arc<Mutex<(f32, f32, f32, bool)>>,
    // port: SerialPortBuilder
}

// fn build_gga(time: &str, lat: &str, ns: &str, lon: &str, ew: &str, fix: &str, sats: &str, hdop: &str, alt: &str, geoid: &str, age: &str) -> String {
//     let data = format!("GPGGA,{},{},{},{},{},{},{},{},{},M,{},M,{},0000", time, lat, ns, lon, ew, fix, sats, hdop, alt, geoid, alt);
//     let crc: u8 = data.as_bytes().iter().skip(2).fold(0, |acc, &x| acc.wrapping_add(x));
//     format!("${}*{:X}", data, crc)
// }

impl GPS {
    pub fn new(debug: bool, serialport: String) -> Self {
        let port_name = format!("/dev/{}", serialport);
        let baud_rate = 115200;
        if debug { println!("Open serialport") }
        let port = serialport::new(port_name, baud_rate)
            .timeout(Duration::from_millis(100))
            .open()
            .expect("Failed to open serial port");
        let port_clone = port.try_clone().expect("Failed to clone");

        thread::spawn(move || Self::reader(debug, port_clone ));
        thread::spawn(move || Self::udp_reader(debug, port ));
        GPS {
            // debug,
            // orientation,
            // port
        }
    }

    fn reader(debug: bool, port: Box<dyn SerialPort> ) {

        let writer = Writer::new(false, debug);

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
                            heading = course.parse::<f32>().unwrap_or(0.0);
                        }
                        else {
                            heading = 0.0;
                        }
                        if kph != "" {
                            speed = kph.parse::<f32>().unwrap_or(0.0);
                        }
                        else {
                            speed = f32::MAX;
                        }
                    }
                    else if part[0] == "$GNGGA" {
                        if part[6] != "0" && part[6] != "" && part[1] != "" && part[2] != "" && part[4] != "" {
                            let time = part[1];
                            let mut lat = part[2][0..2].parse::<f64>().unwrap_or(0.0) + part[2][2..].parse::<f64>().unwrap_or(0.0) / 60.0;
                            let ns = part[3];
                            if ns == "S" { lat = -lat; }
                            let mut lon = part[4][0..3].parse::<f64>().unwrap_or(0.0) + part[4][3..].parse::<f64>().unwrap_or(0.0) / 60.0;
                            let ew = part[5];
                            if ew == "W" { lon = -lon; }
                            let fix = part[6].parse::<u8>().unwrap_or(0);
                            let sat = part[7].parse::<u16>().unwrap_or(0);
                            let hdop = part[8].parse::<f32>().unwrap_or(0.0);
                            let alt = part[9].parse::<f32>().unwrap_or(0.0);
                            let geoid = part[11];
                            let age = part[13].parse::<f32>().unwrap_or(99.9); // Panic
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

    pub fn udp_reader(_debug: bool, mut port: Box<dyn SerialPort> ) {
        let server = UdpSocket::bind("0.0.0.0:2233").unwrap();
        server.set_broadcast(true).unwrap();
        server.set_nonblocking(true).unwrap();
        // let mut writer = BufWriter::new(port);

        let mut buf = [0u8; 1024];
    
        // Reader thread to listen for incoming messages
        loop {
            match server.recv_from(&mut buf) {
                Ok((size, _addr)) => {
                    let _ = port.write_all(&buf[..size]);
                },
                Err(e) if e.kind() != std::io::ErrorKind::WouldBlock => {
                    eprintln!("Read socket error: {:?}", e);
                    break;
                },
                _ => {}
            }
            thread::sleep(Duration::from_millis(1));
        }
    }


}


#[cfg(test)]
mod gps {
    use super::*;

    #[test]
    fn gps() {
        let _gps = GPS::new(true, "serial0".to_string());
        thread::sleep(Duration::from_millis(5000));
    }
}

