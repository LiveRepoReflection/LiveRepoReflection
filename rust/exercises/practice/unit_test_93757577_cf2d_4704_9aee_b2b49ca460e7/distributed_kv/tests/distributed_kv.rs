use distributed_kv::*;
use std::sync::Arc;
use std::thread;

#[test]
fn test_basic_put_get() {
    let store = DistributedStore::new(3);
    assert!(store.put(1, vec![1, 2, 3]));
    assert_eq!(store.get(1), Some(vec![1, 2, 3]));
}

#[test]
fn test_nonexistent_key() {
    let store = DistributedStore::new(3);
    assert_eq!(store.get(1), None);
}

#[test]
fn test_basic_range_query() {
    let store = DistributedStore::new(3);
    store.put(1, vec![1]);
    store.put(2, vec![2]);
    store.put(3, vec![3]);
    store.put(4, vec![4]);
    store.put(5, vec![5]);

    let result = store.range_query(2, 4);
    assert_eq!(result.len(), 3);
    assert_eq!(result[0], (2, vec![2]));
    assert_eq!(result[1], (3, vec![3]));
    assert_eq!(result[2], (4, vec![4]));
}

#[test]
fn test_empty_range_query() {
    let store = DistributedStore::new(3);
    store.put(1, vec![1]);
    store.put(5, vec![5]);
    
    let result = store.range_query(2, 4);
    assert!(result.is_empty());
}

#[test]
fn test_single_key_range() {
    let store = DistributedStore::new(3);
    store.put(1, vec![1]);
    
    let result = store.range_query(1, 1);
    assert_eq!(result.len(), 1);
    assert_eq!(result[0], (1, vec![1]));
}

#[test]
fn test_large_range() {
    let store = DistributedStore::new(5);
    for i in 0..1000 {
        store.put(i, vec![i as u8]);
    }
    
    let result = store.range_query(100, 200);
    assert_eq!(result.len(), 101);
    for (idx, (key, value)) in result.iter().enumerate() {
        assert_eq!(*key, (idx + 100) as u64);
        assert_eq!(value[0], (idx + 100) as u8);
    }
}

#[test]
fn test_concurrent_operations() {
    let store = Arc::new(DistributedStore::new(5));
    let mut handles = vec![];
    
    // Concurrent puts
    for i in 0..10 {
        let store_clone = Arc::clone(&store);
        handles.push(thread::spawn(move || {
            store_clone.put(i, vec![i as u8]);
        }));
    }
    
    // Concurrent gets
    for i in 0..10 {
        let store_clone = Arc::clone(&store);
        handles.push(thread::spawn(move || {
            let _ = store_clone.get(i);
        }));
    }
    
    // Concurrent range queries
    for i in 0..5 {
        let store_clone = Arc::clone(&store);
        handles.push(thread::spawn(move || {
            let _ = store_clone.range_query(i * 2, (i + 1) * 2);
        }));
    }
    
    for handle in handles {
        handle.join().unwrap();
    }
}

#[test]
fn test_boundary_values() {
    let store = DistributedStore::new(3);
    store.put(u64::MIN, vec![1]);
    store.put(u64::MAX, vec![2]);
    
    assert_eq!(store.get(u64::MIN), Some(vec![1]));
    assert_eq!(store.get(u64::MAX), Some(vec![2]));
    
    let result = store.range_query(u64::MIN, u64::MAX);
    assert!(result.contains(&(u64::MIN, vec![1])));
    assert!(result.contains(&(u64::MAX, vec![2])));
}

#[test]
fn test_overwrite_values() {
    let store = DistributedStore::new(3);
    store.put(1, vec![1]);
    assert_eq!(store.get(1), Some(vec![1]));
    
    store.put(1, vec![2]);
    assert_eq!(store.get(1), Some(vec![2]));
}

#[test]
fn test_different_server_counts() {
    for n in 1..=10 {
        let store = DistributedStore::new(n);
        for i in 0..100 {
            store.put(i, vec![i as u8]);
        }
        
        for i in 0..100 {
            assert_eq!(store.get(i), Some(vec![i as u8]));
        }
        
        let result = store.range_query(30, 40);
        assert_eq!(result.len(), 11);
    }
}

#[test]
fn test_server_distribution() {
    let store = DistributedStore::new(5);
    let mut key_counts = vec![0; 5];
    
    // Insert many keys and count distribution
    for i in 0..1000 {
        store.put(i, vec![1]);
        let server_idx = (store.hash(i) % 5) as usize;
        key_counts[server_idx] += 1;
    }
    
    // Check that keys are somewhat evenly distributed
    for count in key_counts {
        assert!(count > 150); // Should have roughly 200 keys each
    }
}

#[test]
#[should_panic]
fn test_zero_servers() {
    let _store = DistributedStore::new(0);
}

#[test]
fn test_range_query_ordering() {
    let store = DistributedStore::new(3);
    // Insert in reverse order
    store.put(5, vec![5]);
    store.put(4, vec![4]);
    store.put(3, vec![3]);
    store.put(2, vec![2]);
    store.put(1, vec![1]);
    
    let result = store.range_query(1, 5);
    
    // Verify results are in ascending order
    for i in 0..result.len()-1 {
        assert!(result[i].0 < result[i+1].0);
    }
}