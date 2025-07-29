use std::collections::{HashMap, HashSet, VecDeque};
use std::time::{SystemTime, UNIX_EPOCH};
use std::sync::{Arc, RwLock, Mutex};

/// Represents a post in the social network
#[derive(Clone, Debug)]
pub struct Post {
    pub id: u64,
    pub author_id: u64,
    pub content: String,
    pub timestamp: u64,
}

impl Post {
    fn new(id: u64, author_id: u64, content: String) -> Self {
        let timestamp = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .expect("Time went backwards!")
            .as_secs();
        
        Post {
            id,
            author_id,
            content,
            timestamp,
        }
    }
}

/// A structure to track post propagation to avoid duplicates
#[derive(Debug)]
struct PostTracker {
    seen: HashSet<u64>,
}

impl PostTracker {
    fn new() -> Self {
        PostTracker {
            seen: HashSet::new(),
        }
    }
    
    fn has_seen(&self, post_id: u64) -> bool {
        self.seen.contains(&post_id)
    }
    
    fn mark_as_seen(&mut self, post_id: u64) {
        self.seen.insert(post_id);
    }
}

/// LRU Cache for storing posts with a limited capacity
#[derive(Debug)]
struct LRUCache {
    capacity: usize,
    cache: VecDeque<Post>,
    post_map: HashMap<u64, usize>, // Maps post_id to its index in the VecDeque
}

impl LRUCache {
    fn new(capacity: usize) -> Self {
        LRUCache {
            capacity,
            cache: VecDeque::with_capacity(capacity),
            post_map: HashMap::new(),
        }
    }
    
    fn get(&mut self, post_id: u64) -> Option<Post> {
        if let Some(&index) = self.post_map.get(&post_id) {
            // Remove the post from its current position
            let post = self.cache.remove(index).unwrap();
            
            // Update indices for all posts that were after the removed post
            for (_, idx) in self.post_map.iter_mut() {
                if *idx > index {
                    *idx -= 1;
                }
            }
            
            // Add the post to the front (most recently used)
            self.cache.push_front(post.clone());
            
            // Update indices for all posts
            for (id, idx) in self.post_map.iter_mut() {
                if *id != post_id {
                    *idx += 1;
                }
            }
            
            // Update index for this post
            self.post_map.insert(post_id, 0);
            
            Some(post)
        } else {
            None
        }
    }
    
    fn put(&mut self, post: Post) {
        // If the post already exists, just access it to move it to the front
        if self.get(post.id).is_some() {
            return;
        }
        
        // If cache is at capacity, remove the least recently used item
        if self.cache.len() == self.capacity {
            if let Some(lru_post) = self.cache.pop_back() {
                self.post_map.remove(&lru_post.id);
            }
        }
        
        // Add the new post and update indices
        for (_, idx) in self.post_map.iter_mut() {
            *idx += 1;
        }
        
        self.cache.push_front(post.clone());
        self.post_map.insert(post.id, 0);
    }
    
    fn get_all(&self) -> Vec<Post> {
        self.cache.iter().cloned().collect()
    }
}

/// A node in the decentralized social network
#[derive(Debug)]
pub struct Node {
    id: u64,
    friends: HashSet<u64>,
    post_cache: LRUCache,
    max_degree: u32,
    post_tracker: PostTracker,
}

impl Node {
    fn new(id: u64, max_cache_size: usize, max_degree: u32) -> Self {
        Node {
            id,
            friends: HashSet::new(),
            post_cache: LRUCache::new(max_cache_size),
            max_degree,
            post_tracker: PostTracker::new(),
        }
    }
    
    fn add_friend(&mut self, friend_id: u64) -> bool {
        self.friends.insert(friend_id)
    }
    
    fn get_friends(&self) -> Vec<u64> {
        self.friends.iter().cloned().collect()
    }
    
    fn create_post(&self, post_id: u64, content: String) -> Post {
        Post::new(post_id, self.id, content)
    }
    
    fn receive_post(&mut self, post: Post, sender_id: u64, current_degree: u32) -> Vec<u64> {
        // If we've seen this post already or if we're beyond max degree, don't propagate it further
        if self.post_tracker.has_seen(post.id) || current_degree > self.max_degree {
            return Vec::new();
        }
        
        // Mark post as seen and add to cache
        self.post_tracker.mark_as_seen(post.id);
        self.post_cache.put(post);
        
        // Determine which friends to propagate to (all except the sender)
        self.friends.iter()
            .filter(|&&id| id != sender_id)
            .cloned()
            .collect()
    }
    
    fn get_posts(&self) -> Vec<Post> {
        let mut posts = self.post_cache.get_all();
        // Sort by timestamp (newest first)
        posts.sort_by(|a, b| b.timestamp.cmp(&a.timestamp));
        posts
    }
}

/// The main social network structure that manages all nodes
#[derive(Debug)]
pub struct SocialNetwork {
    nodes: HashMap<u64, Arc<Mutex<Node>>>,
    max_cache_size: usize,
}

impl SocialNetwork {
    pub fn new(max_cache_size_per_node: usize) -> Self {
        SocialNetwork {
            nodes: HashMap::new(),
            max_cache_size: max_cache_size_per_node,
        }
    }
    
    pub fn create_node(&mut self, node_id: u64, degree: u32) {
        let node = Node::new(node_id, self.max_cache_size, degree);
        self.nodes.insert(node_id, Arc::new(Mutex::new(node)));
    }
    
    pub fn connect_nodes(&mut self, node1_id: u64, node2_id: u64) {
        // Bidirectional connection
        if let Some(node1) = self.nodes.get(&node1_id) {
            let mut node1 = node1.lock().unwrap();
            node1.add_friend(node2_id);
        } else {
            panic!("Node with id {} not found", node1_id);
        }
        
        if let Some(node2) = self.nodes.get(&node2_id) {
            let mut node2 = node2.lock().unwrap();
            node2.add_friend(node1_id);
        } else {
            panic!("Node with id {} not found", node2_id);
        }
    }
    
    pub fn post(&mut self, author_id: u64, post_id: u64, content: String) {
        // Create the post
        let post = {
            let author = self.nodes.get(&author_id)
                .expect(&format!("Node with id {} not found", author_id));
            let author_guard = author.lock().unwrap();
            author_guard.create_post(post_id, content)
        };
        
        // Propagate the post starting from the author
        self.propagate_post(post, author_id, 0, HashSet::new());
    }
    
    fn propagate_post(&self, post: Post, source_id: u64, current_degree: u32, mut visited: HashSet<u64>) {
        // Queue for breadth-first traversal
        let mut queue: VecDeque<(u64, u64, u32)> = VecDeque::new();
        queue.push_back((source_id, source_id, current_degree));  // (node_id, sender_id, degree)
        
        while let Some((node_id, sender_id, degree)) = queue.pop_front() {
            // Mark as visited to avoid loops
            if !visited.insert(node_id) {
                continue;  // Skip if already visited
            }
            
            // Get the node and process the post
            if let Some(node_arc) = self.nodes.get(&node_id) {
                let mut node = node_arc.lock().unwrap();
                
                // Have the node receive the post and get propagation targets
                let propagate_to = node.receive_post(post.clone(), sender_id, degree);
                
                // Queue up the next nodes to receive the post if we're still within degree limit
                if degree < node.max_degree {
                    for friend_id in propagate_to {
                        if !visited.contains(&friend_id) {
                            queue.push_back((friend_id, node_id, degree + 1));
                        }
                    }
                }
            }
        }
    }
    
    pub fn get_posts_for_node(&self, node_id: u64) -> Vec<Post> {
        if let Some(node) = self.nodes.get(&node_id) {
            let node = node.lock().unwrap();
            node.get_posts()
        } else {
            panic!("Node with id {} not found", node_id);
        }
    }
    
    pub fn get_node_friends(&self, node_id: u64) -> Vec<u64> {
        if let Some(node) = self.nodes.get(&node_id) {
            let node = node.lock().unwrap();
            node.get_friends()
        } else {
            panic!("Node with id {} not found", node_id);
        }
    }
}