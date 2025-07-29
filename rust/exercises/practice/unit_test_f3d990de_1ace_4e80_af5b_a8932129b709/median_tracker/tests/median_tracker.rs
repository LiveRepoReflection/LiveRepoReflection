use median_tracker::MedianTracker;

#[test]
fn test_empty_stream() {
    let tracker = MedianTracker::new();
    assert_eq!(tracker.get_median(), None);
}

#[test]
fn test_single_element() {
    let mut tracker = MedianTracker::new();
    tracker.insert(5);
    assert_eq!(tracker.get_median(), Some(5.0));
}

#[test]
fn test_odd_number_of_elements() {
    let mut tracker = MedianTracker::new();
    tracker.insert(1);
    tracker.insert(3);
    tracker.insert(2);
    assert_eq!(tracker.get_median(), Some(2.0));
}

#[test]
fn test_even_number_of_elements() {
    let mut tracker = MedianTracker::new();
    tracker.insert(1);
    tracker.insert(3);
    tracker.insert(2);
    tracker.insert(4);
    assert_eq!(tracker.get_median(), Some(2.5));
}

#[test]
fn test_duplicate_elements() {
    let mut tracker = MedianTracker::new();
    tracker.insert(1);
    tracker.insert(1);
    tracker.insert(1);
    tracker.insert(1);
    tracker.insert(1);
    assert_eq!(tracker.get_median(), Some(1.0));
}

#[test]
fn test_remove_nonexistent() {
    let mut tracker = MedianTracker::new();
    tracker.insert(1);
    tracker.insert(2);
    tracker.remove(3); // Trying to remove non-existent element
    assert_eq!(tracker.get_median(), Some(1.5));
}

#[test]
fn test_remove_existing() {
    let mut tracker = MedianTracker::new();
    tracker.insert(1);
    tracker.insert(2);
    tracker.insert(3);
    tracker.remove(2);
    assert_eq!(tracker.get_median(), Some(2.0));
}

#[test]
fn test_remove_duplicate() {
    let mut tracker = MedianTracker::new();
    tracker.insert(1);
    tracker.insert(1);
    tracker.insert(1);
    tracker.remove(1); // Should remove only one instance
    assert_eq!(tracker.get_median(), Some(1.0));
}

#[test]
fn test_complex_sequence() {
    let mut tracker = MedianTracker::new();
    tracker.insert(5);
    assert_eq!(tracker.get_median(), Some(5.0));
    
    tracker.insert(10);
    assert_eq!(tracker.get_median(), Some(7.5));
    
    tracker.insert(15);
    assert_eq!(tracker.get_median(), Some(10.0));
    
    tracker.remove(10);
    assert_eq!(tracker.get_median(), Some(10.0));
    
    tracker.remove(15);
    assert_eq!(tracker.get_median(), Some(5.0));
    
    tracker.remove(5);
    assert_eq!(tracker.get_median(), None);
}

#[test]
fn test_large_sequence() {
    let mut tracker = MedianTracker::new();
    for i in 0..1000 {
        tracker.insert(i);
    }
    assert_eq!(tracker.get_median(), Some(499.5));
    
    for i in (0..500).rev() {
        tracker.remove(i);
    }
    assert_eq!(tracker.get_median(), Some(749.5));
}

#[test]
fn test_negative_numbers() {
    let mut tracker = MedianTracker::new();
    tracker.insert(-5);
    tracker.insert(-3);
    tracker.insert(-1);
    tracker.insert(2);
    tracker.insert(4);
    assert_eq!(tracker.get_median(), Some(-1.0));
}

#[test]
fn test_boundary_values() {
    let mut tracker = MedianTracker::new();
    tracker.insert(i64::MIN);
    tracker.insert(0);
    tracker.insert(i64::MAX);
    assert_eq!(tracker.get_median(), Some(0.0));
}