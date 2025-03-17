use chrono::Local;

pub fn write(text: &str) {
    let local = Local::now();
    println!("\n{} {}", local.format("%H:%M:%S"), text);
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_write() {
        write("Moe!");
    }
}