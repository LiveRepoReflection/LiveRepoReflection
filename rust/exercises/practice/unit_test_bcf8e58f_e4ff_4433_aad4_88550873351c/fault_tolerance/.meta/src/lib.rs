use std::sync::{Arc, Mutex};
use std::thread;
use std::time::Duration;

pub struct Cluster {
    n: usize,
    f: usize,
    alive: Arc<Mutex<Vec<bool>>>,
    leader: Arc<Mutex<Option<usize>>>,
    log: Arc<Mutex<Vec<i32>>>,
    monitor_handle: Option<thread::JoinHandle<()>>,
}

impl Cluster {
    pub fn new(n: usize, f: usize) -> Self {
        // Ensure f < n/2 as required
        assert!(f < n/2, "Fault tolerance f must be less than n/2");
        let alive = Arc::new(Mutex::new(vec![true; n]));
        let leader = Arc::new(Mutex::new(None));
        let log = Arc::new(Mutex::new(Vec::new()));

        Cluster {
            n,
            f,
            alive,
            leader,
            log,
            monitor_handle: None,
        }
    }

    pub fn start(&mut self) {
        let alive = Arc::clone(&self.alive);
        let leader = Arc::clone(&self.leader);
        let n = self.n;
        // Start a background monitoring thread to simulate leader election and heartbeats
        let handle = thread::spawn(move || {
            loop {
                {
                    let alive_guard = alive.lock().unwrap();
                    let mut leader_guard = leader.lock().unwrap();
                    // If current leader is None or not alive, elect a new leader
                    let leader_alive = if let Some(l) = *leader_guard {
                        alive_guard.get(l).copied().unwrap_or(false)
                    } else {
                        false
                    };
                    if !leader_alive {
                        // Election process: Choose the smallest index of alive node
                        let new_leader = alive_guard.iter().enumerate()
                            .find(|&(_idx, &status)| status)
                            .map(|(idx, _)| idx);
                        *leader_guard = new_leader;
                    }
                }
                // Sleep to simulate heartbeat interval and election timeout
                thread::sleep(Duration::from_millis(100));
            }
        });
        self.monitor_handle = Some(handle);
    }

    pub fn get_leader(&self) -> Option<usize> {
        let leader_guard = self.leader.lock().unwrap();
        *leader_guard
    }

    pub fn submit(&self, cmd: i32) -> bool {
        // Only allow submission if a leader exists and that leader is alive.
        let leader_opt = self.get_leader();
        if let Some(leader_idx) = leader_opt {
            let alive_guard = self.alive.lock().unwrap();
            if alive_guard.get(leader_idx).copied().unwrap_or(false) {
                let mut log_guard = self.log.lock().unwrap();
                log_guard.push(cmd);
                return true;
            }
        }
        false
    }

    pub fn get_committed_log(&self) -> Vec<i32> {
        let log_guard = self.log.lock().unwrap();
        log_guard.clone()
    }

    pub fn kill_node(&self, index: usize) {
        let mut alive_guard = self.alive.lock().unwrap();
        if index < alive_guard.len() {
            alive_guard[index] = false;
            // If the killed node is leader, clear leader immediately so new election takes place.
            let mut leader_guard = self.leader.lock().unwrap();
            if let Some(current_leader) = *leader_guard {
                if current_leader == index {
                    *leader_guard = None;
                }
            }
        }
    }
}

#[cfg(test)]
mod tests {
    use super::Cluster;
    use std::thread;
    use std::time::Duration;

    #[test]
    fn test_leader_election() {
        let mut cluster = Cluster::new(5, 1);
        cluster.start();
        // Allow time for leader election
        thread::sleep(Duration::from_millis(500));
        let leader = cluster.get_leader();
        assert!(leader.is_some(), "Leader election failed: no leader elected");
    }

    #[test]
    fn test_log_replication() {
        let mut cluster = Cluster::new(5, 1);
        cluster.start();
        // Allow time for leader election
        thread::sleep(Duration::from_millis(500));
        let leader = cluster.get_leader();
        assert!(leader.is_some(), "No leader elected");

        // Submit a command and verify replication
        let cmd = 42;
        let submit_result = cluster.submit(cmd);
        assert!(submit_result, "Failed to submit command");
        // Allow time for log replication
        thread::sleep(Duration::from_millis(500));
        let committed_log = cluster.get_committed_log();
        assert!(committed_log.contains(&cmd), "Log replication failed: command not found");
    }

    #[test]
    fn test_fault_tolerance() {
        let mut cluster = Cluster::new(5, 1);
        cluster.start();
        // Allow time for leader election
        thread::sleep(Duration::from_millis(500));
        let initial_leader = cluster.get_leader();
        assert!(initial_leader.is_some(), "No leader elected initially");
        let leader_index = initial_leader.unwrap();

        // Submit a command and wait for replication
        let cmd1 = 7;
        assert!(cluster.submit(cmd1), "Failed to submit first command");
        thread::sleep(Duration::from_millis(500));

        // Simulate leader failure
        cluster.kill_node(leader_index);
        // Allow time for new election
        thread::sleep(Duration::from_millis(1000));
        let new_leader = cluster.get_leader();
        assert!(new_leader.is_some(), "No new leader elected after leader failure");
        assert_ne!(new_leader.unwrap(), leader_index, "Leader did not change after failure");

        // Submit a second command and wait for replication
        let cmd2 = 13;
        assert!(cluster.submit(cmd2), "Failed to submit second command");
        thread::sleep(Duration::from_millis(500));

        // Verify both commands are committed and in order
        let committed_log = cluster.get_committed_log();
        assert!(committed_log.len() >= 2, "Not all commands were committed");
        let pos1 = committed_log.iter().position(|&x| x == cmd1);
        let pos2 = committed_log.iter().position(|&x| x == cmd2);
        assert!(pos1.is_some() && pos2.is_some(), "Submitted commands missing in log");
        assert!(pos1.unwrap() < pos2.unwrap(), "Commands were not committed in order");
    }

    #[test]
    fn test_multiple_submissions() {
        let mut cluster = Cluster::new(5, 1);
        cluster.start();
        // Allow time for leader election
        thread::sleep(Duration::from_millis(500));
        
        let commands: Vec<i32> = (1..=10).collect();
        for &cmd in &commands {
            assert!(cluster.submit(cmd), "Failed to submit command {}", cmd);
        }
        // Allow time for all commands to be replicated
        thread::sleep(Duration::from_millis(1000));
        let committed_log = cluster.get_committed_log();
        for &cmd in &commands {
            assert!(committed_log.contains(&cmd), "Command {} missing in committed log", cmd);
        }
        // Ensure commands are committed in order
        let mut last_index = None;
        for &cmd in &commands {
            let pos = committed_log.iter().position(|&x| x == cmd);
            assert!(pos.is_some(), "Command {} missing in log order check", cmd);
            if let Some(last) = last_index {
                assert!(last < pos.unwrap(), "Log order incorrect for command {}", cmd);
            }
            last_index = pos;
        }
    }
}