use std::collections::HashMap;
use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::{Arc, Mutex, Condvar};
use std::thread;
use std::time::{Duration, Instant};

const HEARTBEAT_TIMEOUT: Duration = Duration::from_millis(1000);

struct LockEntry {
    owner: String,
    count: usize,
    last_heartbeat: Instant,
}

struct LockManager {
    locks: Mutex<HashMap<String, LockEntry>>,
    condvar: Condvar,
}

impl LockManager {
    fn new() -> LockManager {
        LockManager {
            locks: Mutex::new(HashMap::new()),
            condvar: Condvar::new(),
        }
    }

    fn acquire_lock(&self, resource: &str, service_id: &str, timeout: Duration) -> Result<(), String> {
        let mut locks = self.locks.lock().unwrap();
        let start_time = Instant::now();
        let mut remaining = timeout;
        loop {
            if let Some(entry) = locks.get_mut(resource) {
                if entry.owner == service_id {
                    entry.count += 1;
                    entry.last_heartbeat = Instant::now();
                    return Ok(());
                }
            } else {
                locks.insert(resource.to_string(), LockEntry {
                    owner: service_id.to_string(),
                    count: 1,
                    last_heartbeat: Instant::now(),
                });
                return Ok(());
            }
            let now = Instant::now();
            let (guard, wait_result) = self.condvar.wait_timeout(locks, remaining).unwrap();
            locks = guard;
            let elapsed = now.elapsed();
            if elapsed >= remaining {
                return Err("Timeout while waiting for lock".to_string());
            }
            remaining = timeout.checked_sub(start_time.elapsed()).unwrap_or(Duration::from_millis(0));
        }
    }

    fn release_lock(&self, resource: &str, service_id: &str) -> Result<(), String> {
        let mut locks = self.locks.lock().unwrap();
        if let Some(entry) = locks.get_mut(resource) {
            if entry.owner != service_id {
                return Err("Service does not own the lock".to_string());
            }
            if entry.count > 1 {
                entry.count -= 1;
                entry.last_heartbeat = Instant::now();
            } else {
                locks.remove(resource);
                self.condvar.notify_all();
            }
            Ok(())
        } else {
            Err("Lock not held".to_string())
        }
    }

    fn heartbeat(&self, resource: &str, service_id: &str) -> Result<(), String> {
        let mut locks = self.locks.lock().unwrap();
        if let Some(entry) = locks.get_mut(resource) {
            if entry.owner != service_id {
                return Err("Service does not own the lock".to_string());
            }
            entry.last_heartbeat = Instant::now();
            Ok(())
        } else {
            Err("Lock not held".to_string())
        }
    }

    fn expire_locks(manager: Arc<LockManager>) {
        loop {
            thread::sleep(Duration::from_millis(200));
            let mut locks = manager.locks.lock().unwrap();
            let now = Instant::now();
            let mut expired_resources = vec![];
            for (resource, entry) in locks.iter() {
                if now.duration_since(entry.last_heartbeat) > HEARTBEAT_TIMEOUT {
                    expired_resources.push(resource.clone());
                }
            }
            if !expired_resources.is_empty() {
                for resource in expired_resources {
                    locks.remove(&resource);
                }
                manager.condvar.notify_all();
            }
        }
    }
}

fn process_command(manager: Arc<LockManager>, command: &str) -> String {
    let parts: Vec<&str> = command.trim().split_whitespace().collect();
    if parts.is_empty() {
        return "ERROR Empty command".to_string();
    }
    match parts[0] {
        "ACQUIRE" => {
            if parts.len() != 4 {
                return "ERROR Invalid ACQUIRE command".to_string();
            }
            let resource = parts[1];
            let service_id = parts[2];
            let timeout_ms: u64 = match parts[3].parse() {
                Ok(val) => val,
                Err(_) => return "ERROR Invalid timeout value".to_string(),
            };
            match manager.acquire_lock(resource, service_id, Duration::from_millis(timeout_ms)) {
                Ok(_) => "OK".to_string(),
                Err(e) => format!("ERROR {}", e),
            }
        }
        "RELEASE" => {
            if parts.len() != 3 {
                return "ERROR Invalid RELEASE command".to_string();
            }
            let resource = parts[1];
            let service_id = parts[2];
            match manager.release_lock(resource, service_id) {
                Ok(_) => "OK".to_string(),
                Err(e) => format!("ERROR {}", e),
            }
        }
        "HEARTBEAT" => {
            if parts.len() != 3 {
                return "ERROR Invalid HEARTBEAT command".to_string();
            }
            let resource = parts[1];
            let service_id = parts[2];
            match manager.heartbeat(resource, service_id) {
                Ok(_) => "OK".to_string(),
                Err(e) => format!("ERROR {}", e),
            }
        }
        _ => "ERROR Unknown command".to_string(),
    }
}

pub fn run_server(address: &str) -> std::io::Result<()> {
    let listener = TcpListener::bind(address)?;
    let manager = Arc::new(LockManager::new());
    {
        let manager_clone = Arc::clone(&manager);
        thread::spawn(move || {
            LockManager::expire_locks(manager_clone);
        });
    }
    for stream in listener.incoming() {
        match stream {
            Ok(stream) => {
                let manager_clone = Arc::clone(&manager);
                thread::spawn(move || {
                    handle_client(manager_clone, stream);
                });
            }
            Err(e) => {
                eprintln!("Connection failed: {}", e);
            }
        }
    }
    Ok(())
}

fn handle_client(manager: Arc<LockManager>, mut stream: TcpStream) {
    let peer_addr = stream.peer_addr();
    let mut reader = BufReader::new(stream.try_clone().unwrap());
    let mut line = String::new();
    while match reader.read_line(&mut line) {
        Ok(n) if n > 0 => {
            let response = process_command(Arc::clone(&manager), &line);
            if let Err(e) = stream.write_all(format!("{}\n", response).as_bytes()) {
                eprintln!("Failed to write to client {:?}: {}", peer_addr, e);
                return;
            }
            line.clear();
            true
        }
        _ => false
    } {}
}