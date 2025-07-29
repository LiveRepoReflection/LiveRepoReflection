use network_orchestrator::*;
use std::collections::HashMap;

fn setup_basic_test() -> (HashMap<NodeId, Node>, HashMap<TaskId, Task>, HashMap<(NodeId, NodeId), i32>) {
    let mut nodes = HashMap::new();
    let mut tasks = HashMap::new();
    let mut network = HashMap::new();

    // Create nodes
    nodes.insert(1, Node {
        id: 1,
        capabilities: vec!["compute".to_string()],
        cpu_cores: 4,
        memory_mb: 8192,
        available_cpu: 4,
        available_memory: 8192,
    });

    nodes.insert(2, Node {
        id: 2,
        capabilities: vec!["storage".to_string()],
        cpu_cores: 8,
        memory_mb: 16384,
        available_cpu: 8,
        available_memory: 16384,
    });

    // Create tasks
    tasks.insert(1, Task {
        id: 1,
        required_capability: "compute".to_string(),
        cpu_cores: 2,
        memory_mb: 4096,
    });

    // Create network connections
    network.insert((1, 2), 10);
    network.insert((2, 1), 10);

    (nodes, tasks, network)
}

#[test]
fn test_empty_input() {
    let nodes = HashMap::new();
    let tasks = HashMap::new();
    let network = HashMap::new();
    
    let result = assign_tasks(nodes, tasks, network, 1);
    assert!(result.is_ok());
    assert_eq!(result.unwrap().len(), 0);
}

#[test]
fn test_basic_assignment() {
    let (nodes, tasks, network) = setup_basic_test();
    let result = assign_tasks(nodes, tasks, network, 1);
    
    assert!(result.is_ok());
    let assignments = result.unwrap();
    assert_eq!(assignments.get(&1), Some(&1));
}

#[test]
fn test_insufficient_resources() {
    let (mut nodes, mut tasks, network) = setup_basic_test();
    
    // Create a task that requires more resources than available
    tasks.insert(2, Task {
        id: 2,
        required_capability: "compute".to_string(),
        cpu_cores: 10,
        memory_mb: 32768,
    });

    let result = assign_tasks(nodes, tasks, network, 1);
    assert!(result.is_ok());
    let assignments = result.unwrap();
    assert_eq!(assignments.len(), 1); // Only one task should be assigned
}

#[test]
fn test_capability_mismatch() {
    let (nodes, mut tasks, network) = setup_basic_test();
    
    // Create a task that requires a non-existent capability
    tasks.insert(2, Task {
        id: 2,
        required_capability: "network".to_string(),
        cpu_cores: 2,
        memory_mb: 4096,
    });

    let result = assign_tasks(nodes, tasks, network, 1);
    assert!(result.is_ok());
    let assignments = result.unwrap();
    assert_eq!(assignments.len(), 1); // Only one task should be assigned
}

#[test]
fn test_disconnected_nodes() {
    let mut nodes = HashMap::new();
    let mut tasks = HashMap::new();
    let network = HashMap::new(); // Empty network = disconnected nodes

    nodes.insert(1, Node {
        id: 1,
        capabilities: vec!["compute".to_string()],
        cpu_cores: 4,
        memory_mb: 8192,
        available_cpu: 4,
        available_memory: 8192,
    });

    nodes.insert(2, Node {
        id: 2,
        capabilities: vec!["compute".to_string()],
        cpu_cores: 4,
        memory_mb: 8192,
        available_cpu: 4,
        available_memory: 8192,
    });

    tasks.insert(1, Task {
        id: 1,
        required_capability: "compute".to_string(),
        cpu_cores: 2,
        memory_mb: 4096,
    });

    let result = assign_tasks(nodes, tasks, network, 1);
    assert!(result.is_ok());
}

#[test]
fn test_multiple_tasks_assignment() {
    let (mut nodes, mut tasks, mut network) = setup_basic_test();
    
    // Add more nodes and tasks
    nodes.insert(3, Node {
        id: 3,
        capabilities: vec!["compute".to_string(), "storage".to_string()],
        cpu_cores: 8,
        memory_mb: 16384,
        available_cpu: 8,
        available_memory: 16384,
    });

    tasks.insert(2, Task {
        id: 2,
        required_capability: "storage".to_string(),
        cpu_cores: 4,
        memory_mb: 8192,
    });

    tasks.insert(3, Task {
        id: 3,
        required_capability: "compute".to_string(),
        cpu_cores: 2,
        memory_mb: 4096,
    });

    network.insert((1, 3), 5);
    network.insert((3, 1), 5);
    network.insert((2, 3), 15);
    network.insert((3, 2), 15);

    let result = assign_tasks(nodes, tasks, network, 1);
    assert!(result.is_ok());
    let assignments = result.unwrap();
    assert_eq!(assignments.len(), 3); // All tasks should be assigned
}

#[test]
fn test_resource_exhaustion() {
    let (mut nodes, mut tasks, network) = setup_basic_test();
    
    // Add multiple tasks that together exceed node capacity
    for i in 2..5 {
        tasks.insert(i, Task {
            id: i,
            required_capability: "compute".to_string(),
            cpu_cores: 2,
            memory_mb: 4096,
        });
    }

    let result = assign_tasks(nodes, tasks, network, 1);
    assert!(result.is_ok());
    let assignments = result.unwrap();
    assert!(assignments.len() < 4); // Not all tasks should be assigned
}

#[test]
fn test_optimal_assignment() {
    let mut nodes = HashMap::new();
    let mut tasks = HashMap::new();
    let mut network = HashMap::new();

    // Create three nodes with different latencies
    nodes.insert(1, Node {
        id: 1,
        capabilities: vec!["compute".to_string()],
        cpu_cores: 4,
        memory_mb: 8192,
        available_cpu: 4,
        available_memory: 8192,
    });

    nodes.insert(2, Node {
        id: 2,
        capabilities: vec!["compute".to_string()],
        cpu_cores: 4,
        memory_mb: 8192,
        available_cpu: 4,
        available_memory: 8192,
    });

    nodes.insert(3, Node {
        id: 3,
        capabilities: vec!["compute".to_string()],
        cpu_cores: 4,
        memory_mb: 8192,
        available_cpu: 4,
        available_memory: 8192,
    });

    // Create network with different latencies
    network.insert((1, 2), 5);
    network.insert((2, 1), 5);
    network.insert((1, 3), 20);
    network.insert((3, 1), 20);
    network.insert((2, 3), 15);
    network.insert((3, 2), 15);

    // Add a task
    tasks.insert(1, Task {
        id: 1,
        required_capability: "compute".to_string(),
        cpu_cores: 2,
        memory_mb: 4096,
    });

    let result = assign_tasks(nodes, tasks, network, 1);
    assert!(result.is_ok());
    let assignments = result.unwrap();
    
    // Task should be assigned to node 1 or 2 (closest nodes)
    assert!(assignments.get(&1) == Some(&1) || assignments.get(&1) == Some(&2));
}