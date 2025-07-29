use std::collections::{BTreeMap, HashMap};
use std::sync::{Arc, RwLock};

pub struct LogEntry {
    timestamp: u64,
    message: String,
}

struct Machine {
    logs: BTreeMap<u64, Vec<String>>,
}

impl Machine {
    fn new() -> Self {
        Machine {
            logs: BTreeMap::new(),
        }
    }

    fn add_log(&mut self, timestamp: u64, message: String) {
        self.logs
            .entry(timestamp)
            .or_insert_with(Vec::new)
            .push(message);
    }

    fn query(&self, start_time: u64, end_time: u64) -> Vec<String> {
        self.logs
            .range(start_time..=end_time)
            .flat_map(|(_, messages)| messages.clone())
            .collect()
    }
}

pub struct DistributedLogSystem {
    machines: Arc<RwLock<HashMap<usize, Machine>>>,
    machine_count: usize,
}

impl DistributedLogSystem {
    pub fn new(machine_count: usize) -> Self {
        let mut machines = HashMap::new();
        for i in 0..machine_count {
            machines.insert(i, Machine::new());
        }

        DistributedLogSystem {
            machines: Arc::new(RwLock::new(machines)),
            machine_count,
        }
    }

    pub fn add_log(&self, machine_id: usize, timestamp: u64, message: String) {
        if machine_id >= self.machine_count {
            return;
        }

        if message.len() > 256 {
            return;
        }

        if let Ok(mut machines) = self.machines.write() {
            if let Some(machine) = machines.get_mut(&machine_id) {
                machine.add_log(timestamp, message);
            }
        }
    }

    pub fn query(&self, start_time: u64, end_time: u64) -> Vec<String> {
        let mut all_logs = Vec::new();

        if let Ok(machines) = self.machines.read() {
            for machine in machines.values() {
                all_logs.extend(machine.query(start_time, end_time));
            }
        }

        all_logs.sort();
        all_logs
    }
}

impl Clone for DistributedLogSystem {
    fn clone(&self) -> Self {
        DistributedLogSystem {
            machines: self.machines.clone(),
            machine_count: self.machine_count,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn test_basic_functionality() {
        let system = DistributedLogSystem::new(2);
        
        system.add_log(0, 1000, "Test message 1".to_string());
        system.add_log(1, 1001, "Test message 2".to_string());
        
        let logs = system.query(1000, 1001);
        assert_eq!(logs.len(), 2);
        assert_eq!(logs[0], "Test message 1");
        assert_eq!(logs[1], "Test message 2");
    }

    #[test]
    fn test_message_length_limit() {
        let system = DistributedLogSystem::new(1);
        let long_message = "a".repeat(257);
        
        system.add_log(0, 1000, long_message);
        let logs = system.query(1000, 1000);
        assert_eq!(logs.len(), 0);
    }

    #[test]
    fn test_invalid_machine_id() {
        let system = DistributedLogSystem::new(2);
        
        system.add_log(2, 1000, "Should not be added".to_string());
        let logs = system.query(1000, 1000);
        assert_eq!(logs.len(), 0);
    }
}