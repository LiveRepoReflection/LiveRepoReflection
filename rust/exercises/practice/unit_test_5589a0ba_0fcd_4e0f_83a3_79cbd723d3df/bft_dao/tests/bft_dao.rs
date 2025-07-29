use std::fs;
use std::path::Path;
use std::sync::{Arc, Mutex};
use std::thread;

use bft_dao::{DAO, DAOError};

#[test]
fn test_member_management() {
    // Create a DAO with initial funds of 10,000.
    let mut dao = DAO::new(10_000);
    // Add members.
    assert!(dao.add_member(1, 100).is_ok());
    assert!(dao.add_member(2, 200).is_ok());
    assert!(dao.add_member(3, 300).is_ok());
    // Attempt to add a duplicate member.
    assert!(dao.add_member(1, 150).is_err());
    // Remove an existing member.
    assert!(dao.remove_member(2).is_ok());
    // Attempt to remove a non-existent member.
    assert!(dao.remove_member(99).is_err());
}

#[test]
fn test_proposal_submission() {
    let mut dao = DAO::new(5_000);
    // Add a valid member.
    assert!(dao.add_member(1, 100).is_ok());
    // Submit a valid proposal.
    assert!(dao.submit_proposal(101, 1, 1_000, "Upgrade infrastructure".to_string()).is_ok());
    // Attempt a proposal submission with an invalid proposer.
    assert!(dao.submit_proposal(102, 99, 500, "Invalid proposer".to_string()).is_err());
}

#[test]
fn test_voting_and_execution() {
    let mut dao = DAO::new(10_000);
    // Add members with varying stakes.
    assert!(dao.add_member(1, 300).is_ok());
    assert!(dao.add_member(2, 200).is_ok());
    assert!(dao.add_member(3, 500).is_ok());
    // Total stake = 1,000. Proposal threshold > 500.
    assert!(dao.submit_proposal(201, 1, 2_000, "New initiative".to_string()).is_ok());

    // Cast votes: members 1 and 3 vote yes; member 2 votes no.
    assert!(dao.vote(201, 1, true).is_ok());
    assert!(dao.vote(201, 2, false).is_ok());
    assert!(dao.vote(201, 3, true).is_ok());
    // Attempt duplicate voting.
    assert!(dao.vote(201, 1, true).is_err());
    // Execute the proposal; should be approved and funds deducted.
    assert!(dao.execute_proposal(201).is_ok());
    // Verify remaining funds.
    assert_eq!(dao.fund_balance(), 8_000);
}

#[test]
fn test_insufficient_funds() {
    let mut dao = DAO::new(1_000);
    assert!(dao.add_member(1, 100).is_ok());
    assert!(dao.add_member(2, 200).is_ok());
    // Submit a proposal that requests more funds than available.
    assert!(dao.submit_proposal(301, 1, 1_500, "Big expansion".to_string()).is_ok());
    // Both members vote yes.
    assert!(dao.vote(301, 1, true).is_ok());
    assert!(dao.vote(301, 2, true).is_ok());
    // Execution should fail due to insufficient funds.
    assert!(dao.execute_proposal(301).is_err());
}

#[test]
fn test_concurrent_votes() {
    let dao = Arc::new(Mutex::new(DAO::new(20_000)));
    {
        let mut dao_lock = dao.lock().unwrap();
        // Add 10 members with equal stakes.
        for member_id in 1..=10 {
            assert!(dao_lock.add_member(member_id, 100).is_ok());
        }
        // Submit a proposal.
        assert!(dao_lock.submit_proposal(401, 1, 5_000, "Concurrent decision".to_string()).is_ok());
    }

    let mut handles = vec![];
    // Spawn threads so that each member casts a vote.
    // For even member IDs, vote yes; for odd, vote no.
    for member_id in 1..=10 {
        let dao_clone = Arc::clone(&dao);
        let handle = thread::spawn(move || {
            let mut dao_lock = dao_clone.lock().unwrap();
            let vote = member_id % 2 == 0;
            dao_lock.vote(401, member_id, vote).unwrap();
        });
        handles.push(handle);
    }
    for handle in handles {
        handle.join().unwrap();
    }

    let mut dao_lock = dao.lock().unwrap();
    // Expected: yes votes from members 2,4,6,8,10 = 500 total out of 1000 stake.
    // Threshold is more than 50% (>500), so proposal should not be approved.
    assert!(dao_lock.execute_proposal(401).is_err());

    // Submit a new proposal with unanimous yes votes.
    assert!(dao_lock.submit_proposal(402, 1, 5_000, "Concurrent proposal 2".to_string()).is_ok());
    for member_id in 1..=10 {
        assert!(dao_lock.vote(402, member_id, true).is_ok());
    }
    // Execution should now succeed.
    assert!(dao_lock.execute_proposal(402).is_ok());
    // Verify that funds are deducted.
    assert_eq!(dao_lock.fund_balance(), 15_000);
}

#[test]
fn test_state_persistence() {
    let state_file = "dao_state_test.dat";
    // Remove any pre-existing state file.
    if Path::new(state_file).exists() {
        assert!(fs::remove_file(state_file).is_ok());
    }
    {
        let mut dao = DAO::new(5_000);
        // Add members and submit a proposal.
        assert!(dao.add_member(1, 100).is_ok());
        assert!(dao.add_member(2, 200).is_ok());
        assert!(dao.submit_proposal(501, 1, 1_000, "Persist state test".to_string()).is_ok());
        // Cast votes ensuring the proposal is approved.
        assert!(dao.vote(501, 1, true).is_ok());
        assert!(dao.vote(501, 2, true).is_ok());
        assert!(dao.execute_proposal(501).is_ok());
        // Persist the DAO state.
        assert!(dao.persist_state(state_file).is_ok());
    }
    // Load the persisted state.
    let loaded_dao = DAO::load_state(state_file);
    assert!(loaded_dao.is_ok());
    let loaded_dao = loaded_dao.unwrap();
    // Fund balance should reflect the execution of the proposal.
    assert_eq!(loaded_dao.fund_balance(), 4_000);
    // Clean up the state file.
    assert!(fs::remove_file(state_file).is_ok());
}

#[test]
fn test_byzantine_fault_simulation() {
    let mut dao = DAO::new(20_000);
    // Add members; some will simulate Byzantine behavior.
    assert!(dao.add_member(1, 500).is_ok());
    assert!(dao.add_member(2, 500).is_ok());
    // Member 3 will be simulated as Byzantine.
    assert!(dao.add_member(3, 500).is_ok());
    assert!(dao.add_member(4, 500).is_ok());
    // Total stake = 2,000; threshold > 1,000.
    // Submit a proposal.
    assert!(dao.submit_proposal(601, 1, 3_000, "Byzantine resilience test".to_string()).is_ok());
    // Honest members vote yes; Byzantine member votes no.
    assert!(dao.vote(601, 1, true).is_ok());   // 500 stake
    assert!(dao.vote(601, 2, true).is_ok());   // 500 stake
    assert!(dao.vote(601, 3, false).is_ok());  // Byzantine vote: 500 stake
    assert!(dao.vote(601, 4, true).is_ok());   // 500 stake
    // Yes votes sum to 1500 which exceeds 50% threshold.
    let exec_result = dao.execute_proposal(601);
    // Funds are sufficient so execution should succeed.
    assert!(exec_result.is_ok());
    // Confirm fund deduction.
    assert_eq!(dao.fund_balance(), 17_000);
}