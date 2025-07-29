use kv_distro::KVStore;
use std::fs;
use std::sync::Arc;
use std::thread;
use std::time::Duration;

#[test]
fn test_put_and_get() {
    let storage_path = "./temp_data1";
    let _ = fs::remove_dir_all(storage_path);
    let mut store = KVStore::new(3, 2, storage_path).expect("Failed to create KVStore");

    store.put("key1".to_string(), "value1".to_string());
    let val = store.get("key1".to_string());
    assert!(val.is_some(), "Expected a value for key1");
    assert_eq!(val.unwrap(), "value1".to_string(), "The retrieved value does not match");

    let _ = fs::remove_dir_all(storage_path);
}

#[test]
fn test_overwrite_value() {
    let storage_path = "./temp_data2";
    let _ = fs::remove_dir_all(storage_path);
    let mut store = KVStore::new(3, 2, storage_path).expect("Failed to create KVStore");

    store.put("key1".to_string(), "initial".to_string());
    store.put("key1".to_string(), "updated".to_string());
    let val = store.get("key1".to_string());
    assert!(val.is_some(), "Expected a value for key1");
    assert_eq!(val.unwrap(), "updated".to_string(), "Value was not updated correctly");

    let _ = fs::remove_dir_all(storage_path);
}

#[test]
fn test_delete() {
    let storage_path = "./temp_data3";
    let _ = fs::remove_dir_all(storage_path);
    let mut store = KVStore::new(3, 2, storage_path).expect("Failed to create KVStore");

    store.put("key1".to_string(), "value1".to_string());
    store.delete("key1".to_string());
    let val = store.get("key1".to_string());
    assert!(val.is_none(), "Key1 should have been deleted");

    let _ = fs::remove_dir_all(storage_path);
}

#[test]
fn test_persistence() {
    let storage_path = "./temp_data4";
    let _ = fs::remove_dir_all(storage_path);
    
    {
        let mut store = KVStore::new(3, 2, storage_path).expect("Failed to create KVStore");
        store.put("key1".to_string(), "persisted".to_string());
    }
    // Simulate node restart by creating a new instance using the same storage path.
    let store = KVStore::new(3, 2, storage_path).expect("Failed to recover KVStore");
    let val = store.get("key1".to_string());
    assert!(val.is_some(), "Persisted key1 not found after restart");
    assert_eq!(val.unwrap(), "persisted".to_string(), "Persisted value does not match");

    let _ = fs::remove_dir_all(storage_path);
}

#[test]
fn test_concurrent_operations() {
    let storage_path = "./temp_data5";
    let _ = fs::remove_dir_all(storage_path);
    let store = Arc::new(KVStore::new(5, 3, storage_path).expect("Failed to create KVStore"));
    let mut handles = vec![];

    for i in 0..10 {
        let store_clone = Arc::clone(&store);
        let handle = thread::spawn(move || {
            let key = format!("key{}", i);
            let value = format!("value{}", i);
            store_clone.put(key.clone(), value.clone());
            thread::sleep(Duration::from_millis(10));
            let retrieved = store_clone.get(key.clone());
            assert!(retrieved.is_some(), "Key {} not found in concurrent operation", key);
            assert_eq!(retrieved.unwrap(), value, "Mismatch for key {} in concurrent operation", key);
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().expect("Thread panicked during concurrent operations");
    }
    let _ = fs::remove_dir_all(storage_path);
}

#[test]
fn test_replication_and_read_repair() {
    let storage_path = "./temp_data6";
    let _ = fs::remove_dir_all(storage_path);
    // Initialize the store with a replication factor of 3 over 4 nodes.
    let mut store = KVStore::new(4, 3, storage_path).expect("Failed to create KVStore");

    store.put("key_repl".to_string(), "replicated_value".to_string());
    // Simulate a read that may trigger read repair.
    let value_first = store.get("key_repl".to_string());
    let value_second = store.get("key_repl".to_string());
    
    assert!(value_first.is_some(), "Expected value from replicated key");
    assert_eq!(value_first.unwrap(), "replicated_value".to_string(), "Replication inconsistency detected on first read");
    assert!(value_second.is_some(), "Expected value from replicated key on second read");
    assert_eq!(value_second.unwrap(), "replicated_value".to_string(), "Replication inconsistency not repaired on second read");

    let _ = fs::remove_dir_all(storage_path);
}