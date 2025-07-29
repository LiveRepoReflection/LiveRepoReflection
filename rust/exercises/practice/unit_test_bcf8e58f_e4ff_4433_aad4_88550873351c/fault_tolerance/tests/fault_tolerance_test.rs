use std::thread;
use std::time::Duration;
use fault_tolerance::Cluster;

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