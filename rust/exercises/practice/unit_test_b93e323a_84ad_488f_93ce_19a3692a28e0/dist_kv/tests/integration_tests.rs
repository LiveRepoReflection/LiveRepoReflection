use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;
use dist_kv::DistKvSystem;

#[test]
fn test_basic_put_get_delete() {
    // Create a system with 5 nodes and a replication factor of 2.
    let system = DistKvSystem::new(5, 2);

    // Basic put operation.
    assert!(system.put("key1".to_string(), "value1".to_string()).is_ok());

    // Verify that the key can be retrieved.
    let value = system.get("key1".to_string());
    assert_eq!(value, Some("value1".to_string()));

    // Delete the key.
    assert!(system.delete("key1".to_string()).is_ok());

    // Confirm that the key is no longer present.
    let value_after_delete = system.get("key1".to_string());
    assert_eq!(value_after_delete, None);
}

#[test]
fn test_fault_tolerance() {
    // Create a system with 6 nodes and a replication factor of 2.
    let mut system = DistKvSystem::new(6, 2);

    // Insert a key.
    assert!(system.put("key2".to_string(), "value2".to_string()).is_ok());

    // Retrieve the key to ensure it is stored.
    let value = system.get("key2".to_string());
    assert_eq!(value, Some("value2".to_string()));

    // Simulate failure of the primary node for "key2".
    if let Some(primary) = system.get_primary_node("key2".to_string()) {
        assert!(system.fail_node(primary).is_ok());
    }

    // With the primary failed, a replica must serve the get request.
    let value_after_failure = system.get("key2".to_string());
    assert_eq!(value_after_failure, Some("value2".to_string()));

    // Now, simulate failure of all nodes in the replication group for "key2".
    let replication_nodes = system.get_replication_nodes("key2".to_string());
    for node in replication_nodes {
        let _ = system.fail_node(node);
    }

    // With all nodes for the key failed, get should return None.
    let value_after_all_failure = system.get("key2".to_string());
    assert_eq!(value_after_all_failure, None);
}

#[test]
fn test_concurrent_operations() {
    // Create a system with 8 nodes and a replication factor of 3.
    let system = Arc::new(Mutex::new(DistKvSystem::new(8, 3)));
    let mut handles = Vec::new();

    // Spawn multiple threads to perform concurrent put and get operations.
    for i in 0..10 {
        let sys_clone = Arc::clone(&system);
        handles.push(thread::spawn(move || {
            let key = format!("key_concurrent_{}", i);
            let value = format!("value_concurrent_{}", i);
            {
                let mut sys = sys_clone.lock().unwrap();
                let put_result = sys.put(key.clone(), value.clone());
                assert!(put_result.is_ok());
            }
            // Introduce a small delay.
            thread::sleep(Duration::from_millis(10));
            {
                let sys = sys_clone.lock().unwrap();
                let fetched = sys.get(key);
                assert_eq!(fetched, Some(value));
            }
        }));
    }

    for handle in handles {
        handle.join().unwrap();
    }
}

#[test]
fn test_invalid_operations() {
    // Create a system with 4 nodes and a replication factor of 1.
    let system = DistKvSystem::new(4, 1);

    // Try to retrieve a non-existent key.
    let res = system.get("non_existent".to_string());
    assert_eq!(res, None);

    // Try to delete a non-existent key.
    let del_res = system.delete("non_existent".to_string());
    assert!(del_res.is_err());
}