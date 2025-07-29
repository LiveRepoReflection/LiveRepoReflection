use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};
use uuid::Uuid;

#[derive(Debug, Clone, PartialEq)]
pub enum Operation {
    Insert {
        after: Option<String>,
        guid: String,
        character: char,
    },
    Delete {
        guid: String,
    },
}

pub struct CrdtEditor {
    sequence: Arc<Mutex<Vec<String>>>,
    characters: Arc<Mutex<HashMap<String, char>>>,
    tombstone: Arc<Mutex<HashSet<String>>>,
}

impl CrdtEditor {
    pub fn new() -> Self {
        CrdtEditor {
            sequence: Arc::new(Mutex::new(Vec::new())),
            characters: Arc::new(Mutex::new(HashMap::new())),
            tombstone: Arc::new(Mutex::new(HashSet::new())),
        }
    }

    pub fn generate_guid() -> String {
        Uuid::new_v4().to_string()
    }

    pub fn apply(&mut self, operation: Operation) {
        match operation {
            Operation::Insert {
                after,
                guid,
                character,
            } => {
                let mut sequence = self.sequence.lock().unwrap();
                let mut characters = self.characters.lock().unwrap();
                let tombstone = self.tombstone.lock().unwrap();

                if characters.contains_key(&guid) || tombstone.contains(&guid) {
                    return;
                }

                characters.insert(guid.clone(), character);

                match after {
                    Some(after_guid) => {
                        if let Some(pos) = sequence.iter().position(|id| id == &after_guid) {
                            sequence.insert(pos + 1, guid);
                        }
                    }
                    None => {
                        sequence.insert(0, guid);
                    }
                }
            }
            Operation::Delete { guid } => {
                let mut tombstone = self.tombstone.lock().unwrap();
                tombstone.insert(guid);
            }
        }
    }

    pub fn to_string(&self) -> String {
        let sequence = self.sequence.lock().unwrap();
        let characters = self.characters.lock().unwrap();
        let tombstone = self.tombstone.lock().unwrap();

        sequence
            .iter()
            .filter(|guid| !tombstone.contains(*guid))
            .filter_map(|guid| characters.get(guid))
            .collect()
    }
}

impl Default for CrdtEditor {
    fn default() -> Self {
        Self::new()
    }
}