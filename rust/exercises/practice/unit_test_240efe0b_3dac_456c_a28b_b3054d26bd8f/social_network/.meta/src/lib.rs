use std::collections::{HashMap, HashSet, VecDeque};
use std::sync::{Arc, RwLock};

/// Represents a user profile in the social network
#[derive(Clone, Debug)]
pub struct UserProfile {
    pub username: String,
    pub bio: String,
    pub online: bool,
}

impl UserProfile {
    fn new(username: String, bio: String) -> Self {
        UserProfile {
            username,
            bio,
            online: true, // Users are online by default
        }
    }
}

/// Main structure for the social network
pub struct SocialNetwork {
    // User profiles: UserID -> UserProfile
    profiles: Arc<RwLock<HashMap<u64, UserProfile>>>,
    // Connections: UserID -> Set of connected UserIDs
    connections: Arc<RwLock<HashMap<u64, HashSet<u64>>>>,
}

impl SocialNetwork {
    /// Creates a new, empty social network
    pub fn new() -> Self {
        SocialNetwork {
            profiles: Arc::new(RwLock::new(HashMap::new())),
            connections: Arc::new(RwLock::new(HashMap::new())),
        }
    }

    /// Adds a new user to the network
    pub fn add_user(&self, user_id: u64, username: String, bio: String) {
        let mut profiles = self.profiles.write().unwrap();
        profiles.insert(user_id, UserProfile::new(username, bio));
        
        // Initialize empty connections for the new user
        let mut connections = self.connections.write().unwrap();
        connections.entry(user_id).or_insert_with(HashSet::new);
    }

    /// Sets a user's online status
    pub fn set_user_status(&self, user_id: u64, online: bool) {
        let mut profiles = self.profiles.write().unwrap();
        if let Some(profile) = profiles.get_mut(&user_id) {
            profile.online = online;
        }
    }

    /// Retrieves a user's profile
    pub fn get_profile(&self, user_id: u64) -> Option<UserProfile> {
        let profiles = self.profiles.read().unwrap();
        profiles.get(&user_id).cloned()
    }

    /// Adds a connection between two users
    /// Returns true if the connection was successfully added, false otherwise
    pub fn add_connection(&self, user_id1: u64, user_id2: u64) -> bool {
        // Check if both users exist
        {
            let profiles = self.profiles.read().unwrap();
            if !profiles.contains_key(&user_id1) || !profiles.contains_key(&user_id2) {
                return false;
            }
        }

        // Don't create self-connections
        if user_id1 == user_id2 {
            return false;
        }

        let mut connections = self.connections.write().unwrap();
        
        // Add bidirectional connection
        connections.entry(user_id1).or_insert_with(HashSet::new).insert(user_id2);
        connections.entry(user_id2).or_insert_with(HashSet::new).insert(user_id1);
        
        true
    }

    /// Removes a connection between two users
    /// Returns true if the connection was successfully removed, false otherwise
    pub fn remove_connection(&self, user_id1: u64, user_id2: u64) -> bool {
        let mut connections = self.connections.write().unwrap();
        
        let mut success = false;
        
        // Remove the connection in both directions
        if let Some(connections1) = connections.get_mut(&user_id1) {
            success = connections1.remove(&user_id2) || success;
        }
        
        if let Some(connections2) = connections.get_mut(&user_id2) {
            success = connections2.remove(&user_id1) || success;
        }
        
        success
    }

    /// Gets all connections for a user
    pub fn get_connections(&self, user_id: u64) -> HashSet<u64> {
        let connections = self.connections.read().unwrap();
        connections.get(&user_id).cloned().unwrap_or_else(HashSet::new)
    }

    /// Finds the shortest path between two users
    /// Returns None if no path exists or if either user doesn't exist
    pub fn find_shortest_path(&self, source_id: u64, destination_id: u64) -> Option<Vec<u64>> {
        // Handle case where source and destination are the same
        if source_id == destination_id {
            // Verify the user exists
            let profiles = self.profiles.read().unwrap();
            if profiles.contains_key(&source_id) {
                return Some(vec![source_id]);
            } else {
                return None;
            }
        }
        
        // Check if both users exist
        {
            let profiles = self.profiles.read().unwrap();
            if !profiles.contains_key(&source_id) || !profiles.contains_key(&destination_id) {
                return None;
            }
        }
        
        // Use BFS to find the shortest path
        let mut queue = VecDeque::new();
        let mut visited = HashSet::new();
        let mut parent = HashMap::new();
        
        queue.push_back(source_id);
        visited.insert(source_id);
        
        // Take a snapshot of the network topology for pathfinding
        let connections = self.connections.read().unwrap();
        let profiles = self.profiles.read().unwrap();
        
        while let Some(current_id) = queue.pop_front() {
            if current_id == destination_id {
                // Reconstruct the path
                let mut path = Vec::new();
                let mut current = current_id;
                
                while current != source_id {
                    path.push(current);
                    current = *parent.get(&current).unwrap();
                }
                path.push(source_id);
                path.reverse();
                
                return Some(path);
            }
            
            // Skip offline users
            if let Some(neighbor_ids) = connections.get(&current_id) {
                for &neighbor_id in neighbor_ids {
                    // Skip offline users
                    if let Some(profile) = profiles.get(&neighbor_id) {
                        if !profile.online {
                            continue;
                        }
                    }
                    
                    if !visited.contains(&neighbor_id) {
                        visited.insert(neighbor_id);
                        parent.insert(neighbor_id, current_id);
                        queue.push_back(neighbor_id);
                    }
                }
            }
        }
        
        // No path found
        None
    }
}

impl Default for SocialNetwork {
    fn default() -> Self {
        Self::new()
    }
}