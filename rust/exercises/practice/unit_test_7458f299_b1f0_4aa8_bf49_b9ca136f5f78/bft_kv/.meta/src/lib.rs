use std::collections::HashMap;
use std::sync::{Mutex};
use std::time::{SystemTime, UNIX_EPOCH};

pub struct BftKvStore {
    replicas: Vec<Replica>,
    n: usize,
    f: usize,
    primary_counter: Mutex<usize>,
    sequence: Mutex<u64>,
}

struct Replica {
    id: usize,
    faulty: bool,
    state: Mutex<HashMap<String, String>>,
}

#[derive(Clone, Copy)]
enum Phase {
    PrePrepare,
    Prepare,
    Commit,
}

impl BftKvStore {
    pub fn new(n: usize, f: usize, faulty_nodes: Vec<usize>) -> Self {
        let mut replicas = Vec::with_capacity(n);
        for i in 0..n {
            let is_faulty = faulty_nodes.contains(&i);
            replicas.push(Replica {
                id: i,
                faulty: is_faulty,
                state: Mutex::new(HashMap::new()),
            });
        }
        BftKvStore {
            replicas,
            n,
            f,
            primary_counter: Mutex::new(0),
            sequence: Mutex::new(0),
        }
    }

    pub fn put(&self, key: String, value: String) {
        let sequence = {
            let mut seq_lock = self.sequence.lock().unwrap();
            let seq = *seq_lock;
            *seq_lock += 1;
            seq
        };

        let primary_id = {
            let mut pc = self.primary_counter.lock().unwrap();
            let pid = *pc % self.n;
            *pc += 1;
            pid
        };

        let correct_message = format!("put:{}:{}:{}", key, value, sequence);

        // Pre-prepare phase
        let preprepare_count = self.broadcast_phase(&correct_message, Phase::PrePrepare);
        if preprepare_count < (2 * self.f + 1) {
            panic!("PrePrepare phase did not reach consensus");
        }

        // Prepare phase
        let prepare_count = self.broadcast_phase(&correct_message, Phase::Prepare);
        if prepare_count < (2 * self.f + 1) {
            panic!("Prepare phase did not reach consensus");
        }

        // Commit phase
        let commit_count = self.broadcast_phase(&correct_message, Phase::Commit);
        if commit_count < (self.f + 1) {
            panic!("Commit phase did not reach consensus");
        }

        // At consensus, update state in all correct replicas
        for replica in &self.replicas {
            if !replica.faulty {
                let mut state = replica.state.lock().unwrap();
                state.insert(key.clone(), value.clone());
            }
        }
    }

    pub fn get(&self, key: String) -> Option<String> {
        let sequence = {
            let mut seq_lock = self.sequence.lock().unwrap();
            let seq = *seq_lock;
            *seq_lock += 1;
            seq
        };

        let primary_id = {
            let mut pc = self.primary_counter.lock().unwrap();
            let pid = *pc % self.n;
            *pc += 1;
            pid
        };

        // For get, read the value from one of the correct replicas as basis.
        let mut current_value = None;
        for replica in &self.replicas {
            if !replica.faulty {
                let state = replica.state.lock().unwrap();
                if let Some(val) = state.get(&key) {
                    current_value = Some(val.clone());
                }
                break;
            }
        }
        let value_for_msg = current_value.clone().unwrap_or_else(|| "".to_string());
        let correct_message = format!("get:{}:{}:{}", key, value_for_msg, sequence);

        // Pre-prepare phase
        let preprepare_count = self.broadcast_phase(&correct_message, Phase::PrePrepare);
        if preprepare_count < (2 * self.f + 1) {
            panic!("PrePrepare phase did not reach consensus in get");
        }

        // Prepare phase
        let prepare_count = self.broadcast_phase(&correct_message, Phase::Prepare);
        if prepare_count < (2 * self.f + 1) {
            panic!("Prepare phase did not reach consensus in get");
        }

        // Commit phase
        let commit_count = self.broadcast_phase(&correct_message, Phase::Commit);
        if commit_count < (self.f + 1) {
            panic!("Commit phase did not reach consensus in get");
        }

        // Gather responses from correct replicas
        let mut counts = HashMap::new();
        for replica in &self.replicas {
            if !replica.faulty {
                let state = replica.state.lock().unwrap();
                let val = state.get(&key).cloned().unwrap_or_else(|| "".to_string());
                *counts.entry(val).or_insert(0) += 1;
            }
        }
        let consensus_value = counts.into_iter().max_by_key(|&(_, count)| count).map(|(v, _)| v);
        if consensus_value == Some("".to_string()) {
            None
        } else {
            consensus_value
        }
    }

    fn broadcast_phase(&self, correct_message: &str, phase: Phase) -> usize {
        let mut count = 0;
        for replica in &self.replicas {
            if let Some(response) = replica.receive_message(correct_message, phase) {
                if response == correct_message {
                    count += 1;
                }
            }
        }
        count
    }
}

impl Replica {
    fn receive_message(&self, correct_message: &str, _phase: Phase) -> Option<String> {
        if self.faulty {
            faulty_behavior(correct_message)
        } else {
            Some(correct_message.to_string())
        }
    }
}

fn faulty_behavior(correct_message: &str) -> Option<String> {
    let nanos = SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .subsec_nanos();
    let val = nanos % 100;
    if val < 50 {
        None
    } else if val < 80 {
        Some("fault".to_string())
    } else {
        Some(correct_message.to_string())
    }
}