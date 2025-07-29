#[test]
fn test_basic_path() {
    let mut network = network_route::Network::new(5);
    network.add_link(0, 1, 10);
    network.add_link(1, 2, 20);
    assert_eq!(network.get_shortest_path(0, 2), 30);
}

#[test]
fn test_no_path() {
    let mut network = network_route::Network::new(5);
    network.add_link(0, 1, 10);
    network.add_link(2, 3, 20);
    assert_eq!(network.get_shortest_path(0, 3), -1);
}

#[test]
fn test_multiple_paths() {
    let mut network = network_route::Network::new(4);
    network.add_link(0, 1, 10);
    network.add_link(1, 2, 20);
    network.add_link(0, 2, 50);
    assert_eq!(network.get_shortest_path(0, 2), 30);
}

#[test]
fn test_remove_link() {
    let mut network = network_route::Network::new(3);
    network.add_link(0, 1, 10);
    network.add_link(1, 2, 20);
    assert_eq!(network.get_shortest_path(0, 2), 30);
    network.remove_link(1, 2);
    assert_eq!(network.get_shortest_path(0, 2), -1);
}

#[test]
fn test_update_link() {
    let mut network = network_route::Network::new(3);
    network.add_link(0, 1, 10);
    network.add_link(1, 2, 20);
    assert_eq!(network.get_shortest_path(0, 2), 30);
    network.add_link(1, 2, 5);  // Update existing link
    assert_eq!(network.get_shortest_path(0, 2), 15);
}

#[test]
fn test_cycle() {
    let mut network = network_route::Network::new(4);
    network.add_link(0, 1, 10);
    network.add_link(1, 2, 20);
    network.add_link(2, 3, 30);
    network.add_link(3, 0, 40);
    assert_eq!(network.get_shortest_path(0, 2), 30);
}

#[test]
fn test_same_node() {
    let mut network = network_route::Network::new(5);
    network.add_link(0, 1, 10);
    assert_eq!(network.get_shortest_path(2, 2), 0);
}

#[test]
fn test_large_network() {
    let mut network = network_route::Network::new(1000);
    for i in 0..999 {
        network.add_link(i, i + 1, 1);
    }
    assert_eq!(network.get_shortest_path(0, 999), 999);
}

#[test]
fn test_multiple_updates() {
    let mut network = network_route::Network::new(4);
    network.add_link(0, 1, 10);
    network.add_link(1, 2, 20);
    network.add_link(2, 3, 30);
    
    assert_eq!(network.get_shortest_path(0, 3), 60);
    
    network.add_link(0, 2, 25);
    assert_eq!(network.get_shortest_path(0, 3), 55);
    
    network.remove_link(0, 2);
    assert_eq!(network.get_shortest_path(0, 3), 60);
}

#[test]
fn test_isolated_nodes() {
    let mut network = network_route::Network::new(6);
    network.add_link(0, 1, 10);
    network.add_link(2, 3, 20);
    network.add_link(4, 5, 30);
    
    assert_eq!(network.get_shortest_path(0, 2), -1);
    assert_eq!(network.get_shortest_path(1, 4), -1);
    assert_eq!(network.get_shortest_path(3, 5), -1);
}