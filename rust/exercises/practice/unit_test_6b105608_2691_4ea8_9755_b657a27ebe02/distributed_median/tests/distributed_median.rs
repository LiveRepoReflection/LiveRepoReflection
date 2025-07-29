use distributed_median::DistributedMedianSystem;

#[test]
fn test_empty_system() {
    let system = DistributedMedianSystem::new();
    assert_eq!(system.get_median(), None);
}

#[test]
fn test_single_node_single_batch() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    system.add_data(1, &[1, 2, 3]);
    assert_eq!(system.get_median(), Some(2.0));
}

#[test]
fn test_single_node_multiple_batches() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    system.add_data(1, &[1, 2, 3]);
    system.add_data(1, &[4, 5, 6]);
    assert_eq!(system.get_median(), Some(3.5));
}

#[test]
fn test_multiple_nodes_single_batch() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    assert!(system.register_node(2));
    system.add_data(1, &[1, 3, 5]);
    system.add_data(2, &[2, 4, 6]);
    assert_eq!(system.get_median(), Some(3.5));
}

#[test]
fn test_multiple_nodes_multiple_batches() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    assert!(system.register_node(2));
    system.add_data(1, &[1, 3, 5]);
    system.add_data(2, &[2, 4]);
    system.add_data(1, &[7, 9]);
    system.add_data(2, &[6, 8]);
    assert_eq!(system.get_median(), Some(5.0));
}

#[test]
fn test_duplicate_node_registration() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    assert!(!system.register_node(1));
}

#[test]
fn test_negative_numbers() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    system.add_data(1, &[-5, -3, -1]);
    assert_eq!(system.get_median(), Some(-3.0));
}

#[test]
fn test_mixed_positive_negative() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    assert!(system.register_node(2));
    system.add_data(1, &[-3, -2, -1]);
    system.add_data(2, &[0, 1, 2]);
    assert_eq!(system.get_median(), Some(-0.5));
}

#[test]
fn test_even_number_of_elements() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    system.add_data(1, &[1, 2, 3, 4]);
    assert_eq!(system.get_median(), Some(2.5));
}

#[test]
fn test_odd_number_of_elements() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    system.add_data(1, &[1, 2, 3, 4, 5]);
    assert_eq!(system.get_median(), Some(3.0));
}

#[test]
fn test_duplicate_values() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    system.add_data(1, &[1, 2, 2, 3]);
    assert_eq!(system.get_median(), Some(2.0));
}

#[test]
fn test_large_dataset() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    assert!(system.register_node(2));
    
    // Node 1: 1..=1000 step 2 (odd numbers)
    let node1_data: Vec<i64> = (1..=1000).step_by(2).collect();
    // Node 2: 2..=1000 step 2 (even numbers)
    let node2_data: Vec<i64> = (2..=1000).step_by(2).collect();
    
    system.add_data(1, &node1_data);
    system.add_data(2, &node2_data);
    
    // Median of 1..1000 should be (500 + 501)/2 = 500.5
    assert_eq!(system.get_median(), Some(500.5));
}

#[test]
fn test_unregistered_node() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    system.add_data(2, &[1, 2, 3]); // Should be ignored
    assert_eq!(system.get_median(), None);
}

#[test]
fn test_empty_batch() {
    let system = DistributedMedianSystem::new();
    assert!(system.register_node(1));
    system.add_data(1, &[]); // Should be ignored
    assert_eq!(system.get_median(), None);
    system.add_data(1, &[1, 2, 3]);
    assert_eq!(system.get_median(), Some(2.0));
}