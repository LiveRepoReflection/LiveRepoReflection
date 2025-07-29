use social_network::SocialNetwork;

fn main() {
    // Create a new social network
    let network = SocialNetwork::new();
    
    // Add some users
    network.add_user(1, "Alice".to_string(), "Software engineer".to_string());
    network.add_user(2, "Bob".to_string(), "Data scientist".to_string());
    network.add_user(3, "Charlie".to_string(), "UX designer".to_string());
    network.add_user(4, "Dave".to_string(), "Product manager".to_string());
    network.add_user(5, "Eve".to_string(), "Security expert".to_string());
    
    // Add connections
    network.add_connection(1, 2);
    network.add_connection(2, 3);
    network.add_connection(3, 4);
    network.add_connection(1, 5);
    network.add_connection(5, 4);
    
    // Find shortest path
    if let Some(path) = network.find_shortest_path(1, 4) {
        println!("Shortest path from Alice to Dave: {:?}", path);
    } else {
        println!("No path found");
    }
    
    // Mark Charlie as offline and find path again
    network.set_user_status(3, false);
    
    if let Some(path) = network.find_shortest_path(1, 4) {
        println!("Shortest path after Charlie went offline: {:?}", path);
    } else {
        println!("No path found after Charlie went offline");
    }
    
    // Get profile example
    if let Some(profile) = network.get_profile(1) {
        println!("User profile: {} - {}", profile.username, profile.bio);
    }
}