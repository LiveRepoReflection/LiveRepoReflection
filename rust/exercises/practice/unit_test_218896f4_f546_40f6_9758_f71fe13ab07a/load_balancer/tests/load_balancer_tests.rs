use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use load_balancer::{LoadBalancer, RequestStatus};

#[test]
fn test_basic_assignment() {
    let lb = Arc::new(Mutex::new(LoadBalancer::new()));
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.add_server(1, 10);
        lb_guard.add_server(2, 10);
        lb_guard.new_request(101, 5);
    }
    thread::sleep(Duration::from_millis(100));
    {
        let lb_guard = lb.lock().unwrap();
        match lb_guard.get_request_status(101) {
            RequestStatus::Processing(server_id) => {
                let loads = lb_guard.get_server_loads();
                let load = loads
                    .iter()
                    .find(|&&(id, _)| id == server_id)
                    .map(|&(_, load)| load)
                    .unwrap_or(0);
                assert_eq!(load, 5, "Server {} should have load 5", server_id);
            }
            _ => panic!("Request 101 should be in processing state"),
        }
    }
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.complete_request(101);
    }
    {
        let lb_guard = lb.lock().unwrap();
        assert_eq!(lb_guard.get_request_status(101), RequestStatus::Completed);
    }
}

#[test]
fn test_server_failover() {
    let lb = Arc::new(Mutex::new(LoadBalancer::new()));
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.add_server(1, 10);
        lb_guard.add_server(2, 10);
        lb_guard.new_request(201, 8);
    }
    thread::sleep(Duration::from_millis(100));
    let initial_server;
    {
        let lb_guard = lb.lock().unwrap();
        match lb_guard.get_request_status(201) {
            RequestStatus::Processing(sid) => {
                initial_server = sid;
            }
            _ => panic!("Request 201 should be processing"),
        }
    }
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.remove_server(initial_server);
    }
    thread::sleep(Duration::from_millis(100));
    {
        let lb_guard = lb.lock().unwrap();
        match lb_guard.get_request_status(201) {
            RequestStatus::Processing(new_server) => {
                assert_ne!(new_server, initial_server, "Request 201 should be reassigned to a different server");
            }
            RequestStatus::Queued => {
                // Acceptable alternative: the request may be requeued if no server is immediately available.
            }
            _ => panic!("Unexpected request status for 201 after server failure"),
        }
    }
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.complete_request(201);
    }
    {
        let lb_guard = lb.lock().unwrap();
        assert_eq!(lb_guard.get_request_status(201), RequestStatus::Completed);
    }
}

#[test]
fn test_no_server_available() {
    let mut lb = LoadBalancer::new();
    lb.new_request(301, 4);
    thread::sleep(Duration::from_millis(100));
    assert_eq!(lb.get_request_status(301), RequestStatus::Queued, "Request 301 should remain queued when no server is available");
    // Now add a server and check that the queued request gets processed.
    lb.add_server(3, 10);
    thread::sleep(Duration::from_millis(100));
    match lb.get_request_status(301) {
        RequestStatus::Processing(_) => {},
        _ => panic!("Request 301 should be processing after a server becomes available"),
    }
    lb.complete_request(301);
    assert_eq!(lb.get_request_status(301), RequestStatus::Completed);
}

#[test]
fn test_concurrent_requests() {
    let lb = Arc::new(Mutex::new(LoadBalancer::new()));
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.add_server(1, 20);
        lb_guard.add_server(2, 20);
        lb_guard.add_server(3, 20);
    }
    let mut handles = vec![];
    for i in 0..10 {
        let lb_clone = Arc::clone(&lb);
        handles.push(thread::spawn(move || {
            let request_id = 400 + i;
            {
                let mut lb = lb_clone.lock().unwrap();
                lb.new_request(request_id, 5);
            }
            thread::sleep(Duration::from_millis(50));
            {
                let mut lb = lb_clone.lock().unwrap();
                lb.complete_request(request_id);
            }
            request_id
        }));
    }
    for handle in handles {
        let rid = handle.join().expect("Thread panicked");
        let lb_guard = lb.lock().unwrap();
        assert_eq!(lb_guard.get_request_status(rid), RequestStatus::Completed, "Request {} should be completed", rid);
    }
    let lb_guard = lb.lock().unwrap();
    let loads = lb_guard.get_server_loads();
    for &(server_id, load) in loads.iter() {
        assert_eq!(load, 0, "Server {} should have zero load after all requests are completed", server_id);
    }
}

#[test]
fn test_recover_server() {
    let lb = Arc::new(Mutex::new(LoadBalancer::new()));
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.add_server(10, 15);
        lb_guard.new_request(501, 10);
    }
    thread::sleep(Duration::from_millis(100));
    let server_id;
    {
        let lb_guard = lb.lock().unwrap();
        match lb_guard.get_request_status(501) {
            RequestStatus::Processing(sid) => {
                server_id = sid;
            }
            _ => panic!("Request 501 should be processing"),
        }
    }
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.remove_server(server_id);
    }
    thread::sleep(Duration::from_millis(100));
    {
        let lb_guard = lb.lock().unwrap();
        match lb_guard.get_request_status(501) {
            RequestStatus::Queued => {},
            _ => panic!("Request 501 should be queued after its server is removed"),
        }
    }
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.recover_server(server_id);
    }
    thread::sleep(Duration::from_millis(100));
    {
        let lb_guard = lb.lock().unwrap();
        match lb_guard.get_request_status(501) {
            RequestStatus::Processing(new_sid) => {
                // The recovered server may reassume the request.
                assert_eq!(new_sid, server_id, "Recovered server should process request 501");
            },
            _ => panic!("Request 501 should be processing after server recovery"),
        }
    }
    {
        let mut lb_guard = lb.lock().unwrap();
        lb_guard.complete_request(501);
    }
    {
        let lb_guard = lb.lock().unwrap();
        assert_eq!(lb_guard.get_request_status(501), RequestStatus::Completed);
    }
}