use std::io::{BufRead, BufReader, Write};
use std::net::{TcpListener, TcpStream};
use std::sync::atomic::{AtomicBool, Ordering};
use std::sync::Arc;
use std::thread;
use std::time::{Duration, Instant};

/// Helper struct to hold dummy server data.
struct DummyServer {
    addr: String,
    running: Arc<AtomicBool>,
    handle: thread::JoinHandle<()>,
}

/// Spawns a dummy HTTP server with configurable behavior for different endpoints.
fn spawn_dummy_server(
    ack_on_prepare: bool,
    prepare_delay: Option<Duration>,
    commit_delay: Option<Duration>,
    rollback_delay: Option<Duration>,
) -> DummyServer {
    let running = Arc::new(AtomicBool::new(true));
    let running_clone = Arc::clone(&running);
    // Bind to port 0 to have the OS assign an available port.
    let listener = TcpListener::bind("127.0.0.1:0").expect("Failed to bind TcpListener");
    listener
        .set_nonblocking(true)
        .expect("Cannot set non-blocking");
    let addr = listener.local_addr().unwrap().to_string();

    let handle = thread::spawn(move || {
        // Run until running flag is false.
        while running_clone.load(Ordering::Relaxed) {
            match listener.accept() {
                Ok((mut stream, _)) => {
                    // Spawn a thread to handle each connection.
                    let ack_on_prepare = ack_on_prepare;
                    let prepare_delay = prepare_delay.clone();
                    let commit_delay = commit_delay.clone();
                    let rollback_delay = rollback_delay.clone();
                    thread::spawn(move || {
                        handle_connection(
                            &mut stream,
                            ack_on_prepare,
                            prepare_delay,
                            commit_delay,
                            rollback_delay,
                        )
                    });
                }
                Err(ref e) if e.kind() == std::io::ErrorKind::WouldBlock => {
                    // No connection ready, sleep briefly
                    thread::sleep(Duration::from_millis(10));
                }
                Err(_) => break,
            }
        }
    });

    DummyServer { addr, running, handle }
}

/// Handles an incoming HTTP connection and responds based on the request path.
fn handle_connection(
    stream: &mut TcpStream,
    ack_on_prepare: bool,
    prepare_delay: Option<Duration>,
    commit_delay: Option<Duration>,
    rollback_delay: Option<Duration>,
) {
    let mut reader = BufReader::new(stream.try_clone().expect("Failed to clone stream"));
    let mut first_line = String::new();
    if reader.read_line(&mut first_line).is_err() {
        return;
    }
    // Expected request example: "GET /prepare HTTP/1.1"
    let request_parts: Vec<&str> = first_line.split_whitespace().collect();
    if request_parts.len() < 2 {
        let _ = write_response(stream, "400 Bad Request", "Bad Request");
        return;
    }
    let path = request_parts[1];

    // Decide response based on endpoint.
    match path {
        "/prepare" => {
            if let Some(delay) = prepare_delay {
                thread::sleep(delay);
            }
            let body = if ack_on_prepare { "ACK" } else { "NACK" };
            let _ = write_response(stream, "200 OK", body);
        }
        "/commit" => {
            if let Some(delay) = commit_delay {
                thread::sleep(delay);
            }
            let _ = write_response(stream, "200 OK", "OK");
        }
        "/rollback" => {
            if let Some(delay) = rollback_delay {
                thread::sleep(delay);
            }
            let _ = write_response(stream, "200 OK", "OK");
        }
        _ => {
            let _ = write_response(stream, "404 Not Found", "Not Found");
        }
    }
}

/// Writes a simple HTTP response to the stream.
fn write_response(stream: &mut TcpStream, status: &str, body: &str) -> std::io::Result<()> {
    let response = format!(
        "HTTP/1.1 {}\r\nContent-Length: {}\r\n\r\n{}",
        status,
        body.len(),
        body
    );
    stream.write_all(response.as_bytes())?;
    stream.flush()?;
    Ok(())
}

/// Helper to stop a dummy server.
fn stop_dummy_server(server: DummyServer) {
    server.running.store(false, Ordering::Relaxed);
    // Allow some time for server thread to exit.
    let _ = server.handle.join();
}

// These tests assume that the atomic_tx module exposes a function with the following signature:
// pub fn run_transaction(service_urls: Vec<String>, timeout: Duration) -> Result<(), String>
// The tests simulate dummy HTTP services for prepare, commit, and rollback endpoints.

#[cfg(test)]
mod tests {
    use super::*;
    use std::time::Duration;

    // Import the public API from the atomic_tx crate.
    use atomic_tx;

    #[test]
    fn test_successful_transaction() {
        // Spawn two dummy services that always respond with ACK and respond quickly.
        let server1 = spawn_dummy_server(true, None, None, None);
        let server2 = spawn_dummy_server(true, None, None, None);

        let service_urls = vec![
            format!("http://{}{}", server1.addr, "/prepare"),
            format!("http://{}{}", server2.addr, "/prepare"),
        ];
        let timeout = Duration::from_millis(500);
        let result = atomic_tx::run_transaction(service_urls, timeout);
        assert!(result.is_ok(), "Expected transaction to commit successfully");

        // Stop the servers.
        stop_dummy_server(server1);
        stop_dummy_server(server2);
    }

    #[test]
    fn test_nack_transaction() {
        // Spawn one service that returns NACK and one that returns ACK.
        let server1 = spawn_dummy_server(false, None, None, None);
        let server2 = spawn_dummy_server(true, None, None, None);

        let service_urls = vec![
            format!("http://{}{}", server1.addr, "/prepare"),
            format!("http://{}{}", server2.addr, "/prepare"),
        ];
        let timeout = Duration::from_millis(500);
        let result = atomic_tx::run_transaction(service_urls, timeout);
        assert!(
            result.is_err(),
            "Expected transaction to rollback due to NACK in prepare phase"
        );

        stop_dummy_server(server1);
        stop_dummy_server(server2);
    }

    #[test]
    fn test_timeout_transaction() {
        // Spawn a service that delays its prepare response beyond the timeout.
        let server = spawn_dummy_server(true, Some(Duration::from_millis(600)), None, None);

        let service_urls = vec![format!("http://{}{}", server.addr, "/prepare")];
        let timeout = Duration::from_millis(500);
        let start = Instant::now();
        let result = atomic_tx::run_transaction(service_urls, timeout);
        let elapsed = start.elapsed();
        // The transaction should fail due to timeout.
        assert!(
            result.is_err(),
            "Expected transaction to rollback due to prepare timeout"
        );
        // Check that the timeout roughly matches the expected duration.
        assert!(
            elapsed >= timeout,
            "Elapsed time should be at least the timeout duration"
        );

        stop_dummy_server(server);
    }

    #[test]
    fn test_concurrent_transactions() {
        // Test handling of multiple concurrent transactions.
        // For each transaction, spawn two dummy services that return ACK.
        let server1_tx1 = spawn_dummy_server(true, None, None, None);
        let server2_tx1 = spawn_dummy_server(true, None, None, None);
        let server1_tx2 = spawn_dummy_server(true, None, None, None);
        let server2_tx2 = spawn_dummy_server(true, None, None, None);

        let service_urls_tx1 = vec![
            format!("http://{}{}", server1_tx1.addr, "/prepare"),
            format!("http://{}{}", server2_tx1.addr, "/prepare"),
        ];
        let service_urls_tx2 = vec![
            format!("http://{}{}", server1_tx2.addr, "/prepare"),
            format!("http://{}{}", server2_tx2.addr, "/prepare"),
        ];

        let timeout = Duration::from_millis(500);
        let handle1 = thread::spawn(move || {
            let res = atomic_tx::run_transaction(service_urls_tx1, timeout);
            assert!(res.is_ok(), "Transaction 1 should commit successfully");
        });
        let handle2 = thread::spawn(move || {
            let res = atomic_tx::run_transaction(service_urls_tx2, timeout);
            assert!(res.is_ok(), "Transaction 2 should commit successfully");
        });

        handle1.join().unwrap();
        handle2.join().unwrap();

        stop_dummy_server(server1_tx1);
        stop_dummy_server(server2_tx1);
        stop_dummy_server(server1_tx2);
        stop_dummy_server(server2_tx2);
    }
}