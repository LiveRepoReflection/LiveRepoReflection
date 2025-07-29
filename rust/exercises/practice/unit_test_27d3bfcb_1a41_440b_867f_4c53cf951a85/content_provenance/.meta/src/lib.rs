use std::collections::HashMap;
use std::sync::RwLock;
use sha2::{Sha256, Digest};

#[derive(Default)]
struct Content {
    author_id: u64,
    content_hash: String,
    timestamp: u64,
    endorsements: Vec<(u64, String)>,
}

pub struct ContentProvenance {
    contents: RwLock<HashMap<u64, Content>>,
}

impl ContentProvenance {
    pub fn new() -> Self {
        Self {
            contents: RwLock::new(HashMap::new()),
        }
    }

    fn calculate_hash(content: &str) -> String {
        let mut hasher = Sha256::new();
        hasher.update(content.as_bytes());
        format!("{:x}", hasher.finalize())
    }

    pub fn store_content(&self, content_id: u64, author_id: u64, content: String, timestamp: u64) -> bool {
        let mut contents = self.contents.write().unwrap();
        
        if contents.contains_key(&content_id) {
            return false;
        }

        contents.insert(content_id, Content {
            author_id,
            content_hash: Self::calculate_hash(&content),
            timestamp,
            endorsements: Vec::new(),
        });

        true
    }

    pub fn verify_content(&self, content_id: u64, content: String) -> bool {
        let contents = self.contents.read().unwrap();
        
        if let Some(stored_content) = contents.get(&content_id) {
            let calculated_hash = Self::calculate_hash(&content);
            calculated_hash == stored_content.content_hash
        } else {
            false
        }
    }

    pub fn get_author(&self, content_id: u64) -> Option<u64> {
        let contents = self.contents.read().unwrap();
        contents.get(&content_id).map(|content| content.author_id)
    }

    pub fn endorse_content(&self, content_id: u64, endorser_id: u64, signature: String) -> bool {
        let mut contents = self.contents.write().unwrap();
        
        if let Some(content) = contents.get_mut(&content_id) {
            content.endorsements.push((endorser_id, signature));
            true
        } else {
            false
        }
    }

    pub fn get_endorsements(&self, content_id: u64) -> Option<Vec<(u64, String)>> {
        let contents = self.contents.read().unwrap();
        
        contents.get(&content_id)
            .map(|content| content.endorsements.clone())
            .filter(|endorsements| !endorsements.is_empty())
    }
}

impl Default for ContentProvenance {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_functionality() {
        let cp = ContentProvenance::new();
        
        // Test storing content
        assert!(cp.store_content(1, 100, "Hello".to_string(), 1700000000));
        
        // Test verification
        assert!(cp.verify_content(1, "Hello".to_string()));
        assert!(!cp.verify_content(1, "Modified".to_string()));
        
        // Test author retrieval
        assert_eq!(cp.get_author(1), Some(100));
        
        // Test endorsements
        assert!(cp.endorse_content(1, 200, "Sig1".to_string()));
        let endorsements = cp.get_endorsements(1).unwrap();
        assert_eq!(endorsements.len(), 1);
        assert_eq!(endorsements[0], (200, "Sig1".to_string()));
    }

    #[test]
    fn test_non_existent_content() {
        let cp = ContentProvenance::new();
        
        assert!(!cp.verify_content(999, "Test".to_string()));
        assert_eq!(cp.get_author(999), None);
        assert!(!cp.endorse_content(999, 100, "Sig".to_string()));
        assert_eq!(cp.get_endorsements(999), None);
    }

    #[test]
    fn test_duplicate_content_id() {
        let cp = ContentProvenance::new();
        
        assert!(cp.store_content(1, 100, "First".to_string(), 1700000000));
        assert!(!cp.store_content(1, 200, "Second".to_string(), 1700000000));
    }
}