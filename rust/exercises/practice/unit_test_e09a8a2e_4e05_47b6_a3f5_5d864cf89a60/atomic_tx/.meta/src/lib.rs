use std::io::{Read, Write, BufReader, BufRead};
use std::net::{TcpStream, ToSocketAddrs};
use std::time::{Duration, SystemTime};
use std::fs::OpenOptions;
use std::fmt::Write as FmtWrite;

/// Executes a distributed transaction using a Two-Phase Commit protocol.
/// Expects a list of service URLs pointing to the /prepare endpoints.
/// For each service, if the prepare phase returns "ACK", the transaction is eligible to be committed.
/// Otherwise, the transaction is rolled back.
///
/// Transaction logging is persisted to "transaction.log" in JSON format.
pub fn run_transaction(service_urls: Vec<String>, timeout: Duration) -> Result<(), String> {
    let tx_id = generate_transaction_id();
    let mut prepare_results = Vec::new();
    let mut handles = Vec::new();

    // Phase 1: Prepare - send GET requests concurrently.
    for url in service_urls.iter() {
        let url_clone = url.clone();
        let timeout_clone = timeout;
        let handle = std::thread::spawn(move || {
            send_http_get(&url_clone, timeout_clone)
        });
        handles.push((url.clone(), handle));
    }

    for (url, handle) in handles {
        let res = handle.join().map_err(|_| "Thread panicked".to_string())?;
        prepare_results.push((url, res));
    }

    // Check prepare phase responses.
    let mut all_ack = true;
    for (_url, resp) in &prepare_results {
        match resp {
            Ok(body) if body.trim() == "ACK" => {},
            _ => {
                all_ack = false;
                break;
            }
        }
    }

    let decision;
    if all_ack {
        // Phase 2: Commit the transaction.
        for url in &service_urls {
            let commit_url = url.replace("/prepare", "/commit");
            let res = send_http_get(&commit_url, timeout)?;
            if res.trim() != "OK" {
                return Err(format!("Commit failed for service: {}", commit_url));
            }
        }
        decision = "commit";
    } else {
        // Phase 2: Rollback the transaction.
        for url in &service_urls {
            let rollback_url = url.replace("/prepare", "/rollback");
            let _ = send_http_get(&rollback_url, timeout);
        }
        decision = "rollback";
        log_transaction(&tx_id, &service_urls, &prepare_results, decision);
        return Err("Transaction rolled back due to prepare failure".to_string());
    }

    log_transaction(&tx_id, &service_urls, &prepare_results, decision);
    Ok(())
}

/// Generates a unique transaction ID using the current system time.
fn generate_transaction_id() -> String {
    match SystemTime::now().duration_since(SystemTime::UNIX_EPOCH) {
        Ok(dur) => format!("{}", dur.as_millis()),
        Err(_) => "unknown".to_string(),
    }
}

/// Logs the transaction details to a durable file in JSON format.
fn log_transaction(
    tx_id: &str,
    service_urls: &Vec<String>,
    prepare_results: &Vec<(String, Result<String, String>)>,
    decision: &str,
) {
    let mut log_line = String::new();
    // Create a JSON formatted log line.
    let _ = write!(&mut log_line, "{{\"transaction_id\": \"{}\", \"services\": [", tx_id);
    let mut first = true;
    for (url, res) in prepare_results {
        if !first {
            log_line.push_str(", ");
        }
        first = false;
        match res {
            Ok(body) => {
                let _ = write!(&mut log_line, "{{\"url\": \"{}\", \"response\": \"{}\"}}", url, body.trim());
            }
            Err(err) => {
                let _ = write!(&mut log_line, "{{\"url\": \"{}\", \"error\": \"{}\"}}", url, err);
            }
        }
    }
    let _ = write!(&mut log_line, "], \"decision\": \"{}\"}}", decision);

    if let Ok(mut file) = OpenOptions::new().create(true).append(true).open("transaction.log") {
        let _ = writeln!(file, "{}", log_line);
    }
}

/// Sends a simple HTTP GET request to the specified URL and returns the response body as a String.
/// The URL is expected to be in the format "http://host:port/path".
fn send_http_get(url: &str, timeout: Duration) -> Result<String, String> {
    // Ensure the URL starts with "http://"
    if !url.starts_with("http://") {
        return Err("Only http:// URLs are supported".to_string());
    }
    let without_scheme = &url[7..];
    let parts: Vec<&str> = without_scheme.splitn(2, '/').collect();
    if parts.len() < 2 {
        return Err("Invalid URL format".to_string());
    }
    let host_port = parts[0];
    let path = format!("/{}", parts[1]);

    let mut addrs_iter = host_port.to_socket_addrs().map_err(|e| format!("Address resolution error: {}", e))?;
    let addr = addrs_iter.next().ok_or("No socket address found")?;

    let stream = TcpStream::connect_timeout(&addr, timeout)
        .map_err(|e| format!("Connection error: {}", e))?;
    stream
        .set_read_timeout(Some(timeout))
        .map_err(|e| format!("Read timeout error: {}", e))?;
    stream
        .set_write_timeout(Some(timeout))
        .map_err(|e| format!("Write timeout error: {}", e))?;

    let request = format!(
        "GET {} HTTP/1.1\r\nHost: {}\r\nConnection: close\r\n\r\n",
        path, host_port
    );

    let mut stream = stream;
    stream.write_all(request.as_bytes()).map_err(|e| format!("Write error: {}", e))?;
    stream.flush().map_err(|e| format!("Flush error: {}", e))?;

    let mut reader = BufReader::new(stream);
    let mut response = String::new();
    reader.read_to_string(&mut response).map_err(|e| format!("Read error: {}", e))?;

    let parts: Vec<&str> = response.split("\r\n\r\n").collect();
    if parts.len() < 2 {
        return Err("Invalid HTTP response".to_string());
    }
    let body = parts[1];
    Ok(body.to_string())
}