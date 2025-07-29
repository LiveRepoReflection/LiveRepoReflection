use dao_simulator::{DAO, ProposalStatus};

#[test]
fn test_add_member() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    assert_eq!(dao.get_member_count(), 2);

    // Adding the same member twice shouldn't increase the count
    dao.add_member("alice".to_string());
    assert_eq!(dao.get_member_count(), 2);
}

#[test]
fn test_submit_proposal() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "charlie".to_string(),
        100,
        "Give Charlie some tokens".to_string()
    );
    
    assert_eq!(dao.get_proposal_status(proposal_id), ProposalStatus::Pending);
    
    // Non-member can't submit a proposal
    let proposal_id2 = dao.submit_proposal(
        "eve".to_string(),
        "dave".to_string(),
        50,
        "Give Dave some tokens".to_string()
    );
    
    assert_eq!(proposal_id2, 0); // Assuming 0 is an invalid proposal ID
}

#[test]
fn test_voting_and_execution() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    dao.add_member("charlie".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "dave".to_string(),
        200,
        "Give Dave some tokens".to_string()
    );
    
    // Non-member can't vote
    assert!(!dao.vote(proposal_id, "eve".to_string(), true));
    
    // Members can vote
    assert!(dao.vote(proposal_id, "alice".to_string(), true));
    assert!(dao.vote(proposal_id, "bob".to_string(), true));
    
    // Member can't vote twice
    assert!(!dao.vote(proposal_id, "alice".to_string(), false));
    
    // Execute proposal (should pass with 2/3 yes votes)
    assert!(dao.execute_proposal(proposal_id));
    
    // Check proposal status
    assert_eq!(dao.get_proposal_status(proposal_id), ProposalStatus::Executed);
    
    // Check treasury balance
    assert_eq!(dao.get_treasury_balance(), 800);
}

#[test]
fn test_failed_proposal() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    dao.add_member("charlie".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "dave".to_string(),
        200,
        "Give Dave some tokens".to_string()
    );
    
    // 1 yes, 2 no
    assert!(dao.vote(proposal_id, "alice".to_string(), true));
    assert!(dao.vote(proposal_id, "bob".to_string(), false));
    assert!(dao.vote(proposal_id, "charlie".to_string(), false));
    
    // Execute proposal (should fail with 1/3 yes votes)
    assert!(!dao.execute_proposal(proposal_id));
    
    // Check proposal status
    assert_eq!(dao.get_proposal_status(proposal_id), ProposalStatus::Failed);
    
    // Treasury balance should remain unchanged
    assert_eq!(dao.get_treasury_balance(), 1000);
}

#[test]
fn test_insufficient_quorum() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    dao.add_member("charlie".to_string());
    dao.add_member("dave".to_string());
    dao.add_member("eve".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "frank".to_string(),
        200,
        "Give Frank some tokens".to_string()
    );
    
    // Only 2/5 members vote (40%), threshold is 60%
    assert!(dao.vote(proposal_id, "alice".to_string(), true));
    assert!(dao.vote(proposal_id, "bob".to_string(), true));
    
    // Execute proposal (should fail due to insufficient quorum)
    assert!(!dao.execute_proposal(proposal_id));
    
    // Check proposal status
    assert_eq!(dao.get_proposal_status(proposal_id), ProposalStatus::Failed);
}

#[test]
fn test_treasury_limits() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "charlie".to_string(),
        1500, // More than available
        "Give Charlie too many tokens".to_string()
    );
    
    assert!(dao.vote(proposal_id, "alice".to_string(), true));
    assert!(dao.vote(proposal_id, "bob".to_string(), true));
    
    // Execute proposal (should fail due to insufficient funds)
    assert!(!dao.execute_proposal(proposal_id));
    
    // Treasury balance should remain unchanged
    assert_eq!(dao.get_treasury_balance(), 1000);
}

#[test]
fn test_concurrent_proposals() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    
    let proposal_id1 = dao.submit_proposal(
        "alice".to_string(),
        "charlie".to_string(),
        300,
        "Give Charlie some tokens".to_string()
    );
    
    let proposal_id2 = dao.submit_proposal(
        "bob".to_string(),
        "dave".to_string(),
        400,
        "Give Dave some tokens".to_string()
    );
    
    // Vote for both proposals
    assert!(dao.vote(proposal_id1, "alice".to_string(), true));
    assert!(dao.vote(proposal_id1, "bob".to_string(), true));
    
    assert!(dao.vote(proposal_id2, "alice".to_string(), true));
    assert!(dao.vote(proposal_id2, "bob".to_string(), true));
    
    // Execute both proposals
    assert!(dao.execute_proposal(proposal_id1));
    assert!(dao.execute_proposal(proposal_id2));
    
    // Treasury should reflect both transfers
    assert_eq!(dao.get_treasury_balance(), 300);
}

#[test]
fn test_invalid_proposal_execution() {
    let mut dao = DAO::new(1000, 60, 50);
    
    // Try to execute a non-existent proposal
    assert!(!dao.execute_proposal(9999));
}

#[test]
fn test_voting_on_invalid_proposal() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    
    // Try to vote on a non-existent proposal
    assert!(!dao.vote(9999, "alice".to_string(), true));
}

#[test]
fn test_executed_proposal_revote() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "charlie".to_string(),
        200,
        "Give Charlie some tokens".to_string()
    );
    
    assert!(dao.vote(proposal_id, "alice".to_string(), true));
    assert!(dao.vote(proposal_id, "bob".to_string(), true));
    
    // Execute the proposal
    assert!(dao.execute_proposal(proposal_id));
    
    // Try to vote again after execution
    assert!(!dao.vote(proposal_id, "alice".to_string(), false));
    
    // Try to execute again
    assert!(!dao.execute_proposal(proposal_id));
}

#[test]
fn test_overflow_scenarios() {
    // Test with a very large treasury amount
    let mut dao = DAO::new(u64::MAX, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "charlie".to_string(),
        100,
        "Give Charlie some tokens".to_string()
    );
    
    assert!(dao.vote(proposal_id, "alice".to_string(), true));
    assert!(dao.vote(proposal_id, "bob".to_string(), true));
    
    assert!(dao.execute_proposal(proposal_id));
    assert_eq!(dao.get_treasury_balance(), u64::MAX - 100);
}

#[test]
fn test_edge_case_quorum_and_threshold() {
    // Test with 100% quorum and threshold requirements
    let mut dao = DAO::new(1000, 100, 100);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    dao.add_member("charlie".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "dave".to_string(),
        200,
        "Give Dave some tokens".to_string()
    );
    
    // All members vote yes
    assert!(dao.vote(proposal_id, "alice".to_string(), true));
    assert!(dao.vote(proposal_id, "bob".to_string(), true));
    assert!(dao.vote(proposal_id, "charlie".to_string(), true));
    
    assert!(dao.execute_proposal(proposal_id));
    assert_eq!(dao.get_treasury_balance(), 800);
    
    // Now a proposal where not everyone votes yes
    let proposal_id2 = dao.submit_proposal(
        "bob".to_string(),
        "eve".to_string(),
        100,
        "Give Eve some tokens".to_string()
    );
    
    assert!(dao.vote(proposal_id2, "alice".to_string(), true));
    assert!(dao.vote(proposal_id2, "bob".to_string(), true));
    assert!(dao.vote(proposal_id2, "charlie".to_string(), false));
    
    // Should fail since not 100% yes votes
    assert!(!dao.execute_proposal(proposal_id2));
    assert_eq!(dao.get_treasury_balance(), 800);
}

#[test]
fn test_zero_amount_proposal() {
    let mut dao = DAO::new(1000, 60, 50);
    dao.add_member("alice".to_string());
    dao.add_member("bob".to_string());
    
    let proposal_id = dao.submit_proposal(
        "alice".to_string(),
        "charlie".to_string(),
        0, // Zero amount
        "Give Charlie zero tokens".to_string()
    );
    
    assert!(dao.vote(proposal_id, "alice".to_string(), true));
    assert!(dao.vote(proposal_id, "bob".to_string(), true));
    
    assert!(dao.execute_proposal(proposal_id));
    
    // Treasury should remain unchanged
    assert_eq!(dao.get_treasury_balance(), 1000);
    assert_eq!(dao.get_proposal_status(proposal_id), ProposalStatus::Executed);
}