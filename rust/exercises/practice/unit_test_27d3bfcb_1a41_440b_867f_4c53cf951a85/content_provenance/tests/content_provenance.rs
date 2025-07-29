use content_provenance::ContentProvenance;

#[test]
fn test_store_content() {
    let cp = ContentProvenance::new();
    assert!(cp.store_content(1, 100, String::from("Hello World"), 1700000000));
    assert!(!cp.store_content(1, 200, String::from("Duplicate ID"), 1700000000));
}

#[test]
fn test_verify_content() {
    let cp = ContentProvenance::new();
    let content = String::from("Hello World");
    cp.store_content(1, 100, content.clone(), 1700000000);
    
    assert!(cp.verify_content(1, content));
    assert!(!cp.verify_content(1, String::from("Modified content")));
    assert!(!cp.verify_content(2, String::from("Non-existent content")));
}

#[test]
fn test_get_author() {
    let cp = ContentProvenance::new();
    cp.store_content(1, 100, String::from("Hello World"), 1700000000);
    
    assert_eq!(cp.get_author(1), Some(100));
    assert_eq!(cp.get_author(2), None);
}

#[test]
fn test_endorse_content() {
    let cp = ContentProvenance::new();
    cp.store_content(1, 100, String::from("Hello World"), 1700000000);
    
    assert!(cp.endorse_content(1, 200, String::from("Signature1")));
    assert!(cp.endorse_content(1, 300, String::from("Signature2")));
    assert!(!cp.endorse_content(2, 200, String::from("Invalid content")));
}

#[test]
fn test_get_endorsements() {
    let cp = ContentProvenance::new();
    cp.store_content(1, 100, String::from("Hello World"), 1700000000);
    
    cp.endorse_content(1, 200, String::from("Signature1"));
    cp.endorse_content(1, 300, String::from("Signature2"));
    
    let endorsements = cp.get_endorsements(1).unwrap();
    assert_eq!(endorsements.len(), 2);
    assert!(endorsements.contains(&(200, String::from("Signature1"))));
    assert!(endorsements.contains(&(300, String::from("Signature2"))));
    assert_eq!(cp.get_endorsements(2), None);
}

#[test]
fn test_large_content() {
    let cp = ContentProvenance::new();
    let large_content = "A".repeat(1_000_000);
    
    assert!(cp.store_content(1, 100, large_content.clone(), 1700000000));
    assert!(cp.verify_content(1, large_content));
}

#[test]
fn test_multiple_endorsements_same_user() {
    let cp = ContentProvenance::new();
    cp.store_content(1, 100, String::from("Hello World"), 1700000000);
    
    assert!(cp.endorse_content(1, 200, String::from("Signature1")));
    assert!(cp.endorse_content(1, 200, String::from("Signature2")));
    
    let endorsements = cp.get_endorsements(1).unwrap();
    assert_eq!(endorsements.len(), 2);
}

#[test]
fn test_concurrent_operations() {
    use std::sync::Arc;
    use std::thread;
    
    let cp = Arc::new(ContentProvenance::new());
    let mut handles = vec![];
    
    // Store content
    cp.store_content(1, 100, String::from("Hello World"), 1700000000);
    
    // Spawn multiple threads to perform concurrent operations
    for i in 0..10 {
        let cp_clone = Arc::clone(&cp);
        let handle = thread::spawn(move || {
            assert!(cp_clone.endorse_content(1, 200 + i, format!("Signature{}", i)));
            assert!(cp_clone.verify_content(1, String::from("Hello World")));
            assert_eq!(cp_clone.get_author(1), Some(100));
        });
        handles.push(handle);
    }
    
    // Wait for all threads to complete
    for handle in handles {
        handle.join().unwrap();
    }
    
    let endorsements = cp.get_endorsements(1).unwrap();
    assert_eq!(endorsements.len(), 10);
}

#[test]
fn test_empty_content() {
    let cp = ContentProvenance::new();
    assert!(cp.store_content(1, 100, String::from(""), 1700000000));
    assert!(cp.verify_content(1, String::from("")));
}

#[test]
fn test_special_characters() {
    let cp = ContentProvenance::new();
    let content = String::from("Hello 世界! 🌍 #$%^&*");
    assert!(cp.store_content(1, 100, content.clone(), 1700000000));
    assert!(cp.verify_content(1, content));
}

#[test]
fn test_timestamp_storage() {
    let cp = ContentProvenance::new();
    let timestamp = 1700000000;
    cp.store_content(1, 100, String::from("Hello World"), timestamp);
    
    assert!(cp.verify_content(1, String::from("Hello World")));
}