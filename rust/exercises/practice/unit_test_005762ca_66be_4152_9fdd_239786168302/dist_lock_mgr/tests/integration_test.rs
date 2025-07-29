use std::io::{BufRead, BufReader, Write};
use std::net::TcpStream;
use std::sync::Once;
use std::thread;
use std::time::{Duration, Instant};

static INIT: Once = Once::new();

fn start_server() {
    INIT.call_once(|| {
        // Start the server in a background thread on 127.0.0.1:4000.
        // The run_server function is assumed to block and serve connections.
        let addr = "127.0.0.1:4000".to_string();
        thread::spawn(move || {
            // Assuming the server function returns a Result<(), Error>
            dist_lock_mgr::run_server(&addr).unwrap();
        });
        // Allow some time for the server to be up and listening.
        thread::sleep(Duration::from_millis(150));
    });
}

fn send_command(command: &str) -> String {
    // Connect to the server, send the command and return the trimmed response line.
    let mut stream = TcpStream::connect("127.0.0.1:4000").expect("Failed to connect to server");
    stream
        .write_all(format!("{}\n", command).as_bytes())
        .expect("Failed to write command");
    let mut reader = BufReader::new(stream);
    let mut response = String::new();
    reader
        .read_line(&mut response)
        .expect("Failed to read response");
    response.trim().to_string()
}

#[test]
fn test_acquire_and_release() {
    start_server();
    // Service "A" acquires a lock on "resource1" with a timeout of 1000ms.
    let response = send_command("ACQUIRE resource1 A 1000");
    assert_eq!(response, "OK");

    // Now, release the lock.
    let response = send_command("RELEASE resource1 A");
    assert_eq!(response, "OK");
}

#[test]
fn test_reentrant_lock() {
    start_server();
    // Service "A" acquires lock "resource2" twice (reentrant).
    let response = send_command("ACQUIRE resource2 A 1000");
    assert_eq!(response, "OK");

    let response = send_command("ACQUIRE resource2 A 1000");
    assert_eq!(response, "OK");

    // Release it once; lock should still be held.
    let response = send_command("RELEASE resource2 A");
    assert_eq!(response, "OK");

    // Release it again; lock should finally be released.
    let response = send_command("RELEASE resource2 A");
    assert_eq!(response, "OK");
}

#[test]
fn test_acquire_timeout() {
    start_server();
    // Service "A" acquires lock "resource3" with a long timeout.
    let response = send_command("ACQUIRE resource3 A 2000");
    assert_eq!(response, "OK");

    // In another thread, service "B" tries to acquire the same lock with a short timeout.
    let handle = thread::spawn(|| {
        let start = Instant::now();
        let response = send_command("ACQUIRE resource3 B 300");
        let elapsed = start.elapsed();
        // The response should be an error message indicating timeout.
        // We also check that it waited approximately for 300ms.
        assert!(elapsed >= Duration::from_millis(300));
        // The error message format is assumed to be "ERROR <message>"
        assert!(response.starts_with("ERROR"));
        response
    });

    // Wait a bit to ensure B is waiting.
    thread::sleep(Duration::from_millis(400));
    // Now, service "A" releases the lock.
    let response = send_command("RELEASE resource3 A");
    assert_eq!(response, "OK");

    // Wait for thread B to finish.
    let _ = handle.join().expect("Thread panicked");
}

#[test]
fn test_heartbeat_keepalive() {
    start_server();
    // Service "A" acquires lock "resource4" with a timeout of 2000ms.
    let response = send_command("ACQUIRE resource4 A 2000");
    assert_eq!(response, "OK");

    // In a separate thread, simulate service "A" sending periodic heartbeats.
    let heartbeat_handle = thread::spawn(|| {
        for _ in 0..5 {
            thread::sleep(Duration::from_millis(300));
            let res = send_command("HEARTBEAT resource4 A");
            assert_eq!(res, "OK");
        }
    });

    // Meanwhile, service "B" attempts to acquire the same lock.
    // It should block until service "A" stops sending heartbeats and releases the lock.
    // Here, we simulate service B with a timeout that exceeds the heartbeat period.
    // We wait 2000ms first then release the lock from service A.
    thread::sleep(Duration::from_millis(1800));

    // Service "A" now releases the lock.
    let response = send_command("RELEASE resource4 A");
    assert_eq!(response, "OK");

    // Now, service "B" attempts to acquire the lock.
    let response = send_command("ACQUIRE resource4 B 1000");
    assert_eq!(response, "OK");

    let _ = heartbeat_handle.join().expect("Heartbeat thread panicked");

    // Clean up: release the lock from service B.
    let response = send_command("RELEASE resource4 B");
    assert_eq!(response, "OK");
}

#[test]
fn test_invalid_release() {
    start_server();
    // Service "A" acquires lock "resource5".
    let response = send_command("ACQUIRE resource5 A 1000");
    assert_eq!(response, "OK");

    // Service "B" attempts to release lock "resource5", which it does not own.
    let response = send_command("RELEASE resource5 B");
    // Expected to get an error stating that service B is not the owner.
    assert!(response.starts_with("ERROR"));

    // Cleanup: Service "A" releases the lock.
    let response = send_command("RELEASE resource5 A");
    assert_eq!(response, "OK");
}

#[test]
fn test_multiple_clients_fairness() {
    start_server();
    // Service "A" acquires lock "resource6".
    let response = send_command("ACQUIRE resource6 A 2000");
    assert_eq!(response, "OK");

    // Spawn multiple clients attempting to acquire the same lock.
    let handles: Vec<_> = ["B", "C", "D"]
        .iter()
        .map(|&service| {
            thread::spawn(move || {
                let resp = send_command(&format!("ACQUIRE resource6 {} 1500", service));
                (service, resp)
            })
        })
        .collect();

    // Allow some time to ensure all clients are waiting.
    thread::sleep(Duration::from_millis(500));

    // Release the lock held by service A.
    let response = send_command("RELEASE resource6 A");
    assert_eq!(response, "OK");

    // Collect responses from the waiting clients.
    let mut results = vec![];
    for handle in handles {
        let (service, resp) = handle.join().expect("Thread panicked");
        results.push((service, resp));
    }

    // At least one client should eventually acquire the lock successfully.
    let ok_clients: Vec<_> = results.iter().filter(|(_, resp)| resp == "OK").collect();
    assert!(ok_clients.len() >= 1);

    // Cleanup: For any client that acquired the lock, release it.
    for (service, resp) in results {
        if resp == "OK" {
            let release_resp = send_command(&format!("RELEASE resource6 {}", service));
            assert_eq!(release_resp, "OK");
        }
    }
}