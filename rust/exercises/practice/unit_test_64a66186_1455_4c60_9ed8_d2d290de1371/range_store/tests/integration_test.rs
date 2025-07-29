use range_store::RangeStore;

#[test]
fn test_put_and_get() {
    let mut store = RangeStore::new(4, 2);
    store.put("apple".to_string(), "red".to_string());
    store.put("banana".to_string(), "yellow".to_string());
    assert_eq!(store.get("apple".to_string()), Some("red".to_string()));
    assert_eq!(store.get("banana".to_string()), Some("yellow".to_string()));
    assert_eq!(store.get("cherry".to_string()), None);
}

#[test]
fn test_range_query_sorted() {
    let mut store = RangeStore::new(4, 2);
    store.put("apple".to_string(), "red".to_string());
    store.put("banana".to_string(), "yellow".to_string());
    store.put("cherry".to_string(), "dark red".to_string());
    store.put("date".to_string(), "brown".to_string());
    let result = store.range_query("banana".to_string(), "date".to_string());
    let expected = vec![
        ("banana".to_string(), "yellow".to_string()),
        ("cherry".to_string(), "dark red".to_string()),
        ("date".to_string(), "brown".to_string()),
    ];
    assert_eq!(result, expected);
}

#[test]
fn test_update_value() {
    let mut store = RangeStore::new(3, 2);
    store.put("kiwi".to_string(), "green".to_string());
    assert_eq!(store.get("kiwi".to_string()), Some("green".to_string()));
    store.put("kiwi".to_string(), "brown".to_string());
    assert_eq!(store.get("kiwi".to_string()), Some("brown".to_string()));
}

#[test]
fn test_empty_range_query() {
    let mut store = RangeStore::new(3, 2);
    store.put("lemon".to_string(), "yellow".to_string());
    let result = store.range_query("orange".to_string(), "zucchini".to_string());
    let expected: Vec<(String, String)> = vec![];
    assert_eq!(result, expected);
}

#[test]
fn test_node_failure_handling() {
    let mut store = RangeStore::new(5, 3);
    store.put("alpha".to_string(), "first".to_string());
    store.put("beta".to_string(), "second".to_string());
    store.put("gamma".to_string(), "third".to_string());
    assert_eq!(store.get("alpha".to_string()), Some("first".to_string()));
    // Simulate failure of a node (node_id 2)
    store.simulate_node_failure(2);
    // Data should still be retrievable via replicas
    assert_eq!(store.get("alpha".to_string()), Some("first".to_string()));
    let result = store.range_query("alpha".to_string(), "gamma".to_string());
    let expected = vec![
        ("alpha".to_string(), "first".to_string()),
        ("beta".to_string(), "second".to_string()),
        ("gamma".to_string(), "third".to_string()),
    ];
    assert_eq!(result, expected);
}

#[test]
fn test_concurrent_access() {
    use std::sync::{Arc, Barrier, Mutex};
    use std::thread;

    let store = Arc::new(Mutex::new(RangeStore::new(6, 3)));
    let barrier = Arc::new(Barrier::new(4));
    let keys = vec!["a", "b", "c", "d", "e", "f"];
    let mut handles = Vec::new();

    for i in 0..4 {
        let store_clone = Arc::clone(&store);
        let barrier_clone = Arc::clone(&barrier);
        let keys_clone = keys.clone();
        let handle = thread::spawn(move || {
            barrier_clone.wait();
            for key in keys_clone.iter() {
                let value = format!("val_{}_{}", key, i);
                let mut store_locked = store_clone.lock().unwrap();
                store_locked.put(key.to_string(), value);
            }
        });
        handles.push(handle);
    }

    for handle in handles {
        handle.join().unwrap();
    }

    let store_locked = store.lock().unwrap();
    for key in keys.iter() {
        let value = store_locked.get(key.to_string());
        assert!(value.is_some());
    }
}