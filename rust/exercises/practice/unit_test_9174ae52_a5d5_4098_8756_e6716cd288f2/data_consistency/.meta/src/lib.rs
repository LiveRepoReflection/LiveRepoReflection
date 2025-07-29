use std::collections::HashMap;
use std::sync::Mutex;

#[derive(Debug)]
enum VCOrdering {
    Greater,
    Less,
    Equal,
    Concurrent,
}

fn compare_vector_clocks(a: &Vec<usize>, b: &Vec<usize>) -> VCOrdering {
    let mut a_better = false;
    let mut b_better = false;
    for i in 0..a.len() {
        if a[i] > b[i] {
            a_better = true;
        } else if a[i] < b[i] {
            b_better = true;
        }
    }
    if !a_better && !b_better {
        VCOrdering::Equal
    } else if a_better && !b_better {
        VCOrdering::Greater
    } else if b_better && !a_better {
        VCOrdering::Less
    } else {
        VCOrdering::Concurrent
    }
}

struct Message {
    key: String,
    value: Vec<u8>,
    vector_clock: Vec<usize>,
}

pub struct Node {
    node_id: usize,
    total_nodes: usize,
    store: Mutex<HashMap<String, Vec<(Vec<u8>, Vec<usize>)>>>,
    message_queue: Mutex<Vec<Message>>,
}

impl Node {
    pub fn new(node_id: usize, total_nodes: usize) -> Self {
        Node {
            node_id,
            total_nodes,
            store: Mutex::new(HashMap::new()),
            message_queue: Mutex::new(Vec::new()),
        }
    }

    pub fn put(&self, key: String, value: Vec<u8>) {
        let mut new_vc = vec![0; self.total_nodes];
        {
            let store = self.store.lock().unwrap();
            if let Some(versions) = store.get(&key) {
                for (_, vc) in versions.iter() {
                    for i in 0..self.total_nodes {
                        if vc[i] > new_vc[i] {
                            new_vc[i] = vc[i];
                        }
                    }
                }
            }
        }
        new_vc[self.node_id] += 1;
        self.merge_update(key.clone(), value.clone(), new_vc.clone());
        let msg = Message {
            key,
            value,
            vector_clock: new_vc,
        };
        let mut queue = self.message_queue.lock().unwrap();
        queue.push(msg);
    }

    pub fn get(&self, key: String) -> Vec<(Vec<u8>, Vec<usize>)> {
        let store = self.store.lock().unwrap();
        store.get(&key).cloned().unwrap_or_else(Vec::new)
    }

    pub fn receive_update(&self, key: String, value: Vec<u8>, vector_clock: Vec<usize>) {
        let msg = Message { key, value, vector_clock };
        let mut queue = self.message_queue.lock().unwrap();
        queue.push(msg);
    }

    pub fn process_messages(&self) {
        let msgs = {
            let mut queue = self.message_queue.lock().unwrap();
            let msgs = queue.drain(..).collect::<Vec<_>>();
            msgs
        };
        for msg in msgs {
            self.merge_update(msg.key, msg.value, msg.vector_clock);
        }
    }

    fn merge_update(&self, key: String, value: Vec<u8>, vector_clock: Vec<usize>) {
        let mut store = self.store.lock().unwrap();
        let entry = store.entry(key).or_insert_with(Vec::new);
        // Check if an identical update already exists.
        for (exist_value, exist_vc) in entry.iter() {
            if *exist_value == value && *exist_vc == vector_clock {
                return;
            }
        }
        let mut new_versions: Vec<(Vec<u8>, Vec<usize>)> = Vec::new();
        let mut to_add = true;
        for (existing_value, existing_vc) in entry.iter() {
            match compare_vector_clocks(existing_vc, &vector_clock) {
                VCOrdering::Less => {
                    // Existing version is outdated; do not keep it.
                },
                VCOrdering::Greater => {
                    // New update is outdated compared to an existing version.
                    to_add = false;
                    new_versions.push((existing_value.clone(), existing_vc.clone()));
                },
                VCOrdering::Equal => {
                    new_versions.push((existing_value.clone(), existing_vc.clone()));
                },
                VCOrdering::Concurrent => {
                    new_versions.push((existing_value.clone(), existing_vc.clone()));
                },
            }
        }
        if to_add {
            new_versions.push((value, vector_clock));
        }
        *entry = new_versions;
    }
}

#[cfg(test)]
mod tests {
    use super::Node;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_node_initialization() {
        let node = Node::new(0, 3);
        let result = node.get("key".to_string());
        assert!(result.is_empty(), "Expected empty result for uninitialized key");
    }

    #[test]
    fn test_single_put_and_get() {
        let node = Node::new(0, 3);
        node.put("key".to_string(), b"value".to_vec());
        node.process_messages();

        let result = node.get("key".to_string());
        assert_eq!(result.len(), 1, "Expected one version after put");
        let (val, vector_clock) = &result[0];
        assert_eq!(val, &b"value".to_vec(), "Value does not match");
        assert_eq!(vector_clock.len(), 3, "Vector clock length mismatch");
        assert_eq!(vector_clock[0], 1, "Vector clock count for node 0 should be 1");
        assert_eq!(vector_clock[1], 0, "Vector clock count for node 1 should be 0");
        assert_eq!(vector_clock[2], 0, "Vector clock count for node 2 should be 0");
    }

    #[test]
    fn test_conflict_resolution_concurrent_updates() {
        let node0 = Node::new(0, 3);
        let node1 = Node::new(1, 3);

        node0.put("key".to_string(), b"value0".to_vec());
        node1.put("key".to_string(), b"value1".to_vec());
        node0.process_messages();
        node1.process_messages();

        let versions_node0 = node0.get("key".to_string());
        let versions_node1 = node1.get("key".to_string());
        assert_eq!(versions_node0.len(), 1, "Node0 should have one version before exchange");
        assert_eq!(versions_node1.len(), 1, "Node1 should have one version before exchange");
        let (val0, vc0) = &versions_node0[0];
        let (val1, vc1) = &versions_node1[0];

        node0.receive_update("key".to_string(), val1.clone(), vc1.clone());
        node1.receive_update("key".to_string(), val0.clone(), vc0.clone());
        node0.process_messages();
        node1.process_messages();

        let res0 = node0.get("key".to_string());
        let res1 = node1.get("key".to_string());
        assert_eq!(res0.len(), 2, "Expected 2 versions on node0 due to conflict");
        assert_eq!(res1.len(), 2, "Expected 2 versions on node1 due to conflict");

        let values_node0: Vec<Vec<u8>> = res0.iter().map(|(v, _)| v.clone()).collect();
        assert!(values_node0.contains(&b"value0".to_vec()), "node0 missing value0");
        assert!(values_node0.contains(&b"value1".to_vec()), "node0 missing value1");
    }

    #[test]
    fn test_update_overwrites_existing_value() {
        let node = Node::new(0, 3);
        node.put("key".to_string(), b"old".to_vec());
        node.process_messages();

        node.put("key".to_string(), b"new".to_vec());
        node.process_messages();

        let res = node.get("key".to_string());
        assert_eq!(res.len(), 1, "Only one version should exist after overwrite");
        let (val, vc) = &res[0];
        assert_eq!(val, &b"new".to_vec(), "Value should be 'new'");
        assert_eq!(vc[0], 2, "Vector clock for node 0 should be 2 after two updates");
    }

    #[test]
    fn test_asynchronous_message_ordering() {
        let node = Node::new(0, 3);
        node.put("key".to_string(), b"first".to_vec());
        node.process_messages();

        let versions = node.get("key".to_string());
        assert_eq!(versions.len(), 1, "Expected one version after first put");
        let (_, vc_first) = &versions[0];

        let mut updated_vc = vc_first.clone();
        updated_vc[0] += 1;
        let early_update = ("key".to_string(), b"second".to_vec(), vc_first.clone());
        let delayed_update = ("key".to_string(), b"third".to_vec(), updated_vc.clone());

        node.receive_update(early_update.0.clone(), early_update.1.clone(), early_update.2.clone());
        node.receive_update(delayed_update.0.clone(), delayed_update.1.clone(), delayed_update.2.clone());
        node.process_messages();

        let res = node.get("key".to_string());
        assert_eq!(res.len(), 1, "Only one version expected after proper ordering");
        let (val, vc) = &res[0];
        assert_eq!(val, &b"third".to_vec(), "Value should be 'third' after asynchronous updates");
        assert_eq!(vc, &updated_vc, "Vector clock should match the delayed update");
    }
}

#[cfg(test)]
mod integration_tests {
    // This module includes integration style tests that utilize multithreading to simulate asynchronous behavior.
    use super::Node;
    use std::sync::Arc;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_concurrent_puts() {
        let node = Arc::new(Node::new(0, 3));
        let node_clone = Arc::clone(&node);

        let handle = thread::spawn(move || {
            for _ in 0..5 {
                node_clone.put("concurrent".to_string(), b"thread1".to_vec());
                thread::sleep(Duration::from_millis(10));
            }
            node_clone.process_messages();
        });

        for _ in 0..5 {
            node.put("concurrent".to_string(), b"main".to_vec());
            thread::sleep(Duration::from_millis(15));
        }
        handle.join().unwrap();
        node.process_messages();

        let versions = node.get("concurrent".to_string());
        // Since updates come from one node, they should eventually merge into one version.
        assert_eq!(versions.len(), 1, "Expected one consolidated version after concurrent puts");
    }
}