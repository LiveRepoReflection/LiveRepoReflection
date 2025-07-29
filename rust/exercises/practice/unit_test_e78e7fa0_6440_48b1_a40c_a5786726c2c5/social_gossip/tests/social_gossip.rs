use social_gossip::*;

#[test]
fn test_create_node() {
    let mut network = SocialNetwork::new(10);
    network.create_node(1, 2);
    assert!(network.get_posts_for_node(1).is_empty());
}

#[test]
fn test_connect_nodes() {
    let mut network = SocialNetwork::new(10);
    network.create_node(1, 2);
    network.create_node(2, 2);
    network.connect_nodes(1, 2);
    
    // Test that connections are bidirectional
    let node1_friends = network.get_node_friends(1);
    let node2_friends = network.get_node_friends(2);
    
    assert!(node1_friends.contains(&2));
    assert!(node2_friends.contains(&1));
}

#[test]
fn test_post_creation() {
    let mut network = SocialNetwork::new(10);
    network.create_node(1, 2);
    network.post(1, 101, "Hello, world!".to_string());
    
    let posts = network.get_posts_for_node(1);
    assert_eq!(posts.len(), 1);
    assert_eq!(posts[0].id, 101);
    assert_eq!(posts[0].author_id, 1);
    assert_eq!(posts[0].content, "Hello, world!");
}

#[test]
fn test_post_propagation_degree_1() {
    let mut network = SocialNetwork::new(10);
    
    // Create nodes with degree 1
    network.create_node(1, 1);
    network.create_node(2, 1);
    network.create_node(3, 1);
    
    // Connect nodes: 1 <-> 2, 2 <-> 3
    network.connect_nodes(1, 2);
    network.connect_nodes(2, 3);
    
    // Node 1 creates a post
    network.post(1, 101, "Post from node 1".to_string());
    
    // Node 2 should receive the post (direct friend)
    let node2_posts = network.get_posts_for_node(2);
    assert_eq!(node2_posts.len(), 1);
    assert_eq!(node2_posts[0].id, 101);
    
    // Node 3 should NOT receive the post (friend of friend, beyond degree 1)
    let node3_posts = network.get_posts_for_node(3);
    assert_eq!(node3_posts.len(), 0);
}

#[test]
fn test_post_propagation_degree_2() {
    let mut network = SocialNetwork::new(10);
    
    // Create nodes with degree 2
    network.create_node(1, 2);
    network.create_node(2, 2);
    network.create_node(3, 2);
    network.create_node(4, 2);
    
    // Connect nodes: 1 <-> 2, 2 <-> 3, 3 <-> 4
    network.connect_nodes(1, 2);
    network.connect_nodes(2, 3);
    network.connect_nodes(3, 4);
    
    // Node 1 creates a post
    network.post(1, 101, "Post from node 1".to_string());
    
    // Node 2 should receive the post (direct friend)
    let node2_posts = network.get_posts_for_node(2);
    assert_eq!(node2_posts.len(), 1);
    assert_eq!(node2_posts[0].id, 101);
    
    // Node 3 should receive the post (friend of friend, within degree 2)
    let node3_posts = network.get_posts_for_node(3);
    assert_eq!(node3_posts.len(), 1);
    assert_eq!(node3_posts[0].id, 101);
    
    // Node 4 should NOT receive the post (beyond degree 2)
    let node4_posts = network.get_posts_for_node(4);
    assert_eq!(node4_posts.len(), 0);
}

#[test]
fn test_lru_cache_eviction() {
    let mut network = SocialNetwork::new(2); // Cache size of 2
    
    network.create_node(1, 2);
    network.create_node(2, 2);
    network.connect_nodes(1, 2);
    
    // Node 2 creates 3 posts
    network.post(2, 101, "First post".to_string());
    network.post(2, 102, "Second post".to_string());
    network.post(2, 103, "Third post".to_string());
    
    // Node 1 should only have the 2 most recent posts due to LRU eviction
    let node1_posts = network.get_posts_for_node(1);
    assert_eq!(node1_posts.len(), 2);
    
    // Check that the oldest post was evicted
    let post_ids: Vec<u64> = node1_posts.iter().map(|p| p.id).collect();
    assert!(post_ids.contains(&102));
    assert!(post_ids.contains(&103));
    assert!(!post_ids.contains(&101));
}

#[test]
fn test_complex_network_topology() {
    let mut network = SocialNetwork::new(5);
    
    // Create nodes
    for i in 1..=7 {
        network.create_node(i, 2);
    }
    
    // Create a more complex network topology:
    // 1 -- 2 -- 3
    // |    |    |
    // 4 -- 5 -- 6
    //      |
    //      7
    
    network.connect_nodes(1, 2);
    network.connect_nodes(2, 3);
    network.connect_nodes(1, 4);
    network.connect_nodes(2, 5);
    network.connect_nodes(3, 6);
    network.connect_nodes(4, 5);
    network.connect_nodes(5, 6);
    network.connect_nodes(5, 7);
    
    // Node 1 creates a post
    network.post(1, 101, "Post from node 1".to_string());
    
    // Check post propagation
    // Degree 1: Nodes 2 and 4 should have the post
    assert_eq!(network.get_posts_for_node(2).len(), 1);
    assert_eq!(network.get_posts_for_node(4).len(), 1);
    
    // Degree 2: Nodes 3, 5 should have the post
    assert_eq!(network.get_posts_for_node(3).len(), 1);
    assert_eq!(network.get_posts_for_node(5).len(), 1);
    
    // Degree 3 (beyond limit): Nodes 6 and 7 should NOT have the post
    assert_eq!(network.get_posts_for_node(6).len(), 0);
    assert_eq!(network.get_posts_for_node(7).len(), 0);
    
    // Now node 7 creates a post
    network.post(7, 102, "Post from node 7".to_string());
    
    // Nodes within degree 2 of node 7 should have the post
    assert_eq!(network.get_posts_for_node(5).len(), 2); // Has posts from 1 and 7
    assert_eq!(network.get_posts_for_node(2).len(), 2); // Has posts from 1 and 7
    assert_eq!(network.get_posts_for_node(4).len(), 2); // Has posts from 1 and 7
    assert_eq!(network.get_posts_for_node(6).len(), 1); // Has post from 7 only
}

#[test]
fn test_multiple_posts_ordering() {
    let mut network = SocialNetwork::new(10);
    
    network.create_node(1, 2);
    network.create_node(2, 2);
    network.connect_nodes(1, 2);
    
    // Create multiple posts with different timestamps
    network.post(1, 101, "First post".to_string());
    network.post(1, 102, "Second post".to_string());
    network.post(1, 103, "Third post".to_string());
    network.post(2, 201, "Post from friend".to_string());
    
    // Check that posts are in the correct order (newest first)
    let node1_posts = network.get_posts_for_node(1);
    assert_eq!(node1_posts.len(), 4);
    
    // Posts should be ordered by timestamp (most recent first)
    let post_ids: Vec<u64> = node1_posts.iter().map(|p| p.id).collect();
    assert_eq!(post_ids[0], 201); // Most recent post
    assert_eq!(post_ids[1], 103);
    assert_eq!(post_ids[2], 102);
    assert_eq!(post_ids[3], 101); // Oldest post
}

#[test]
fn test_circular_connections() {
    let mut network = SocialNetwork::new(10);
    
    // Create nodes with degree 2
    network.create_node(1, 2);
    network.create_node(2, 2);
    network.create_node(3, 2);
    
    // Create a circular connection: 1 -> 2 -> 3 -> 1
    network.connect_nodes(1, 2);
    network.connect_nodes(2, 3);
    network.connect_nodes(3, 1);
    
    // Node 1 creates a post
    network.post(1, 101, "Post from node 1".to_string());
    
    // All nodes should receive the post exactly once (no infinite loops)
    assert_eq!(network.get_posts_for_node(1).len(), 1);
    assert_eq!(network.get_posts_for_node(2).len(), 1);
    assert_eq!(network.get_posts_for_node(3).len(), 1);
}

#[test]
#[should_panic(expected = "Node with id 999 not found")]
fn test_nonexistent_node() {
    let mut network = SocialNetwork::new(10);
    network.get_posts_for_node(999); // Should panic
}

#[test]
fn test_disconnected_nodes() {
    let mut network = SocialNetwork::new(10);
    
    network.create_node(1, 2);
    network.create_node(2, 2);
    // Nodes are not connected
    
    network.post(1, 101, "Post from node 1".to_string());
    
    // Node 2 should not receive the post
    assert_eq!(network.get_posts_for_node(2).len(), 0);
}

#[test]
fn test_posts_with_same_content() {
    let mut network = SocialNetwork::new(10);
    
    network.create_node(1, 2);
    network.create_node(2, 2);
    network.connect_nodes(1, 2);
    
    // Create posts with the same content but different IDs
    let content = "Duplicate content".to_string();
    network.post(1, 101, content.clone());
    network.post(1, 102, content.clone());
    
    // Both nodes should have both posts
    assert_eq!(network.get_posts_for_node(1).len(), 2);
    assert_eq!(network.get_posts_for_node(2).len(), 2);
    
    // Posts should be distinct despite having the same content
    let posts = network.get_posts_for_node(1);
    let post_ids: Vec<u64> = posts.iter().map(|p| p.id).collect();
    assert!(post_ids.contains(&101));
    assert!(post_ids.contains(&102));
}