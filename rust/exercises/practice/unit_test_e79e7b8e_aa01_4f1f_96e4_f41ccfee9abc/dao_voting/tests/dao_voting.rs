use std::sync::Arc;
use std::thread;
use std::time::{Duration, SystemTime, UNIX_EPOCH};
use dao_voting::*;

// Helper function to get current timestamp
fn now() -> u64 {
    SystemTime::now()
        .duration_since(UNIX_EPOCH)
        .unwrap()
        .as_secs()
}

#[test]
fn test_member_management() {
    let mut dao = Dao::new(100, 0.5);
    
    // Test adding members
    assert!(dao.add_member(1, 50).is_ok());
    assert!(dao.add_member(2, 30).is_ok());
    
    // Test duplicate member
    assert!(dao.add_member(1, 40).is_err());
    
    // Test updating voting power
    assert!(dao.update_member_power(1, 60).is_ok());
    assert_eq!(dao.get_member_power(1), Some(60));
    
    // Test removing member
    assert!(dao.remove_member(1).is_ok());
    assert_eq!(dao.get_member_power(1), None);
    
    // Test updating non-existent member
    assert!(dao.update_member_power(999, 50).is_err());
}

#[test]
fn test_proposal_creation() {
    let mut dao = Dao::new(100, 0.5);
    let start = now();
    let end = start + 3600; // 1 hour later
    
    // Test valid proposal creation
    assert!(dao.create_proposal(1, "Test proposal".to_string(), start, end).is_ok());
    
    // Test duplicate proposal ID
    assert!(dao.create_proposal(1, "Another proposal".to_string(), start, end).is_err());
    
    // Test invalid time window
    assert!(dao.create_proposal(2, "Invalid time".to_string(), end, start).is_err());
    
    // Test proposal with past end time
    assert!(dao.create_proposal(3, "Past proposal".to_string(), start - 7200, start - 3600).is_err());
}

#[test]
fn test_voting_basic() {
    let mut dao = Dao::new(100, 0.5);
    let start = now();
    let end = start + 3600;
    
    dao.add_member(1, 50).unwrap();
    dao.add_member(2, 30).unwrap();
    dao.create_proposal(1, "Test proposal".to_string(), start, end).unwrap();
    
    // Test valid votes
    assert!(dao.cast_vote(1, 1, VoteOption::For).is_ok());
    assert!(dao.cast_vote(2, 1, VoteOption::Against).is_ok());
    
    // Test double voting
    assert!(dao.cast_vote(1, 1, VoteOption::Against).is_err());
    
    // Test non-existent member voting
    assert!(dao.cast_vote(999, 1, VoteOption::For).is_err());
    
    // Test voting on non-existent proposal
    assert!(dao.cast_vote(1, 999, VoteOption::For).is_err());
}

#[test]
fn test_vote_counting() {
    let mut dao = Dao::new(100, 0.5);
    let start = now();
    let end = start + 3600;
    
    dao.add_member(1, 50).unwrap();
    dao.add_member(2, 30).unwrap();
    dao.add_member(3, 20).unwrap();
    dao.create_proposal(1, "Test proposal".to_string(), start, end).unwrap();
    
    dao.cast_vote(1, 1, VoteOption::For).unwrap();
    dao.cast_vote(2, 1, VoteOption::Against).unwrap();
    dao.cast_vote(3, 1, VoteOption::Abstain).unwrap();
    
    let results = dao.calculate_voting_results(1).unwrap();
    assert_eq!(results.for_votes, 50);
    assert_eq!(results.against_votes, 30);
    assert_eq!(results.abstain_votes, 20);
}

#[test]
fn test_proposal_outcome() {
    let mut dao = Dao::new(60, 0.6); // 60% quorum, 60% threshold
    let start = now();
    let end = start + 3600;
    
    dao.add_member(1, 40).unwrap();
    dao.add_member(2, 30).unwrap();
    dao.add_member(3, 30).unwrap();
    dao.create_proposal(1, "Test proposal".to_string(), start, end).unwrap();
    
    // Test not meeting quorum
    dao.cast_vote(1, 1, VoteOption::For).unwrap();
    assert!(!dao.determine_outcome(1).unwrap());
    
    // Test meeting quorum but not threshold
    dao.cast_vote(2, 1, VoteOption::Against).unwrap();
    assert!(!dao.determine_outcome(1).unwrap());
    
    // Test meeting both quorum and threshold
    dao.cast_vote(3, 1, VoteOption::For).unwrap();
    assert!(dao.determine_outcome(1).unwrap());
}

#[test]
fn test_concurrent_voting() {
    let dao = Arc::new(Dao::new(100, 0.5));
    let start = now();
    let end = start + 3600;
    
    dao.add_member(1, 50).unwrap();
    dao.add_member(2, 30).unwrap();
    dao.create_proposal(1, "Test proposal".to_string(), start, end).unwrap();
    
    let dao1 = Arc::clone(&dao);
    let handle1 = thread::spawn(move || {
        dao1.cast_vote(1, 1, VoteOption::For)
    });
    
    let dao2 = Arc::clone(&dao);
    let handle2 = thread::spawn(move || {
        dao2.cast_vote(2, 1, VoteOption::Against)
    });
    
    handle1.join().unwrap().unwrap();
    handle2.join().unwrap().unwrap();
    
    let results = dao.calculate_voting_results(1).unwrap();
    assert_eq!(results.for_votes, 50);
    assert_eq!(results.against_votes, 30);
}

#[test]
fn test_time_window_constraints() {
    let mut dao = Dao::new(100, 0.5);
    let start = now() + 3600; // 1 hour from now
    let end = start + 3600;   // 2 hours from now
    
    dao.add_member(1, 50).unwrap();
    dao.create_proposal(1, "Future proposal".to_string(), start, end).unwrap();
    
    // Test voting before start time
    assert!(dao.cast_vote(1, 1, VoteOption::For).is_err());
}

#[test]
fn test_large_scale_voting() {
    let mut dao = Dao::new(1_000_000, 0.5);
    let start = now();
    let end = start + 3600;
    
    // Add 1000 members
    for i in 0..1000 {
        dao.add_member(i, 1000).unwrap();
    }
    
    dao.create_proposal(1, "Large scale test".to_string(), start, end).unwrap();
    
    // Cast 1000 votes
    for i in 0..1000 {
        if i % 2 == 0 {
            dao.cast_vote(i, 1, VoteOption::For).unwrap();
        } else {
            dao.cast_vote(i, 1, VoteOption::Against).unwrap();
        }
    }
    
    let results = dao.calculate_voting_results(1).unwrap();
    assert_eq!(results.for_votes, 500_000);
    assert_eq!(results.against_votes, 500_000);
}

#[test]
fn test_member_power_changes() {
    let mut dao = Dao::new(100, 0.5);
    let start = now();
    let end = start + 3600;
    
    dao.add_member(1, 50).unwrap();
    dao.create_proposal(1, "Test proposal".to_string(), start, end).unwrap();
    
    // Cast vote with initial power
    dao.cast_vote(1, 1, VoteOption::For).unwrap();
    
    // Update member power
    dao.update_member_power(1, 100).unwrap();
    
    // Vote power should reflect the power at the time of voting
    let results = dao.calculate_voting_results(1).unwrap();
    assert_eq!(results.for_votes, 50);
}

#[test]
fn test_edge_cases() {
    let mut dao = Dao::new(0, 0.0); // Edge case: zero quorum and threshold
    let start = now();
    let end = start + 3600;
    
    dao.add_member(1, u64::MAX).unwrap(); // Edge case: maximum voting power
    dao.create_proposal(1, "Edge case test".to_string(), start, end).unwrap();
    
    assert!(dao.cast_vote(1, 1, VoteOption::For).is_ok());
    
    let results = dao.calculate_voting_results(1).unwrap();
    assert_eq!(results.for_votes, u64::MAX);
    assert!(dao.determine_outcome(1).unwrap());
}
