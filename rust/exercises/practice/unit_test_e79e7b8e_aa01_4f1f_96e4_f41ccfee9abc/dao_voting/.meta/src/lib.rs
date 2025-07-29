use std::collections::HashMap;
use std::sync::{RwLock, Arc};
use std::time::{SystemTime, UNIX_EPOCH};

// Vote options
#[derive(Debug, Clone, Copy, PartialEq)]
pub enum VoteOption {
    For,
    Against,
    Abstain,
}

// Proposal structure
#[derive(Debug)]
struct Proposal {
    id: u64,
    description: String,
    start_time: u64,
    end_time: u64,
    votes: HashMap<u64, (VoteOption, u64)>, // member_id -> (vote, voting_power_at_time)
}

// Voting results structure
#[derive(Debug, PartialEq)]
pub struct VotingResults {
    pub for_votes: u64,
    pub against_votes: u64,
    pub abstain_votes: u64,
}

// Main DAO structure
pub struct Dao {
    members: RwLock<HashMap<u64, u64>>, // member_id -> voting_power
    proposals: RwLock<HashMap<u64, Proposal>>,
    quorum: u64,
    threshold: f64,
}

// Custom error types
#[derive(Debug)]
pub enum DaoError {
    MemberExists,
    MemberNotFound,
    ProposalExists,
    ProposalNotFound,
    InvalidTimeWindow,
    VoteExists,
    VotingClosed,
    VotingNotStarted,
    InvalidThreshold,
}

impl Dao {
    pub fn new(quorum: u64, threshold: f64) -> Self {
        Dao {
            members: RwLock::new(HashMap::new()),
            proposals: RwLock::new(HashMap::new()),
            quorum,
            threshold,
        }
    }

    // Member management functions
    pub fn add_member(&self, member_id: u64, voting_power: u64) -> Result<(), DaoError> {
        let mut members = self.members.write().unwrap();
        if members.contains_key(&member_id) {
            return Err(DaoError::MemberExists);
        }
        members.insert(member_id, voting_power);
        Ok(())
    }

    pub fn remove_member(&self, member_id: u64) -> Result<(), DaoError> {
        let mut members = self.members.write().unwrap();
        if members.remove(&member_id).is_none() {
            return Err(DaoError::MemberNotFound);
        }
        Ok(())
    }

    pub fn update_member_power(&self, member_id: u64, new_power: u64) -> Result<(), DaoError> {
        let mut members = self.members.write().unwrap();
        if let Some(power) = members.get_mut(&member_id) {
            *power = new_power;
            Ok(())
        } else {
            Err(DaoError::MemberNotFound)
        }
    }

    pub fn get_member_power(&self, member_id: u64) -> Option<u64> {
        self.members.read().unwrap().get(&member_id).copied()
    }

    // Proposal management functions
    pub fn create_proposal(
        &self,
        id: u64,
        description: String,
        start_time: u64,
        end_time: u64,
    ) -> Result<(), DaoError> {
        if start_time >= end_time {
            return Err(DaoError::InvalidTimeWindow);
        }

        let current_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        if end_time <= current_time {
            return Err(DaoError::InvalidTimeWindow);
        }

        let mut proposals = self.proposals.write().unwrap();
        if proposals.contains_key(&id) {
            return Err(DaoError::ProposalExists);
        }

        proposals.insert(
            id,
            Proposal {
                id,
                description,
                start_time,
                end_time,
                votes: HashMap::new(),
            },
        );
        Ok(())
    }

    // Voting functions
    pub fn cast_vote(
        &self,
        member_id: u64,
        proposal_id: u64,
        vote: VoteOption,
    ) -> Result<(), DaoError> {
        // Check if member exists and get voting power
        let member_power = {
            let members = self.members.read().unwrap();
            members
                .get(&member_id)
                .copied()
                .ok_or(DaoError::MemberNotFound)?
        };

        let mut proposals = self.proposals.write().unwrap();
        let proposal = proposals
            .get_mut(&proposal_id)
            .ok_or(DaoError::ProposalNotFound)?;

        let current_time = SystemTime::now()
            .duration_since(UNIX_EPOCH)
            .unwrap()
            .as_secs();

        if current_time < proposal.start_time {
            return Err(DaoError::VotingNotStarted);
        }
        if current_time > proposal.end_time {
            return Err(DaoError::VotingClosed);
        }

        // Only insert if not already voted
        if !proposal.votes.contains_key(&member_id) {
            proposal.votes.insert(member_id, (vote, member_power));
            Ok(())
        } else {
            Err(DaoError::VoteExists)
        }
    }

    // Vote counting
    pub fn calculate_voting_results(&self, proposal_id: u64) -> Result<VotingResults, DaoError> {
        let proposals = self.proposals.read().unwrap();
        let proposal = proposals.get(&proposal_id).ok_or(DaoError::ProposalNotFound)?;

        let mut results = VotingResults {
            for_votes: 0,
            against_votes: 0,
            abstain_votes: 0,
        };

        for (_, (vote, power)) in &proposal.votes {
            match vote {
                VoteOption::For => results.for_votes = results.for_votes.saturating_add(*power),
                VoteOption::Against => results.against_votes = results.against_votes.saturating_add(*power),
                VoteOption::Abstain => results.abstain_votes = results.abstain_votes.saturating_add(*power),
            }
        }

        Ok(results)
    }

    // Outcome determination
    pub fn determine_outcome(&self, proposal_id: u64) -> Result<bool, DaoError> {
        let results = self.calculate_voting_results(proposal_id)?;
        let total_votes = results.for_votes
            .saturating_add(results.against_votes)
            .saturating_add(results.abstain_votes);

        // Check quorum
        if total_votes < self.quorum {
            return Ok(false);
        }

        // Calculate approval ratio
        let total_for_against = results.for_votes.saturating_add(results.against_votes);
        if total_for_against == 0 {
            return Ok(false);
        }

        let approval_ratio = results.for_votes as f64 / total_for_against as f64;
        Ok(approval_ratio >= self.threshold)
    }
}

// Implement Send and Sync for thread safety
unsafe impl Send for Dao {}
unsafe impl Sync for Dao {}