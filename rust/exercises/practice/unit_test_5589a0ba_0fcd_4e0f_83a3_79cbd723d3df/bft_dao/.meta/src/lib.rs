use std::collections::HashMap;
use std::fs::File;
use std::io::{BufRead, BufReader, Write};
use std::path::Path;

#[derive(Debug)]
pub enum DAOError {
    MemberExists,
    MemberNotFound,
    ProposalExists,
    ProposalNotFound,
    DuplicateVote,
    ProposalAlreadyExecuted,
    InsufficientYesVotes,
    InsufficientFunds,
    StatePersistenceError(String),
    StateLoadError(String),
    ParseError(String),
}

#[derive(Clone)]
pub struct Member {
    pub stake: u64,
}

#[derive(Clone)]
pub struct Proposal {
    pub proposer: u64,
    pub amount: u64,
    pub description: String,
    pub executed: bool,
    pub votes: HashMap<u64, bool>, // key: member id, value: vote (true for yes, false for no)
}

pub struct DAO {
    fund: u64,
    members: HashMap<u64, Member>,
    proposals: HashMap<u64, Proposal>,
}

impl DAO {
    pub fn new(fund: u64) -> DAO {
        DAO {
            fund,
            members: HashMap::new(),
            proposals: HashMap::new(),
        }
    }

    pub fn add_member(&mut self, member_id: u64, stake: u64) -> Result<(), DAOError> {
        if self.members.contains_key(&member_id) {
            return Err(DAOError::MemberExists);
        }
        self.members.insert(member_id, Member { stake });
        Ok(())
    }

    pub fn remove_member(&mut self, member_id: u64) -> Result<(), DAOError> {
        if self.members.remove(&member_id).is_none() {
            return Err(DAOError::MemberNotFound);
        }
        Ok(())
    }

    pub fn submit_proposal(&mut self, proposal_id: u64, proposer: u64, amount: u64, description: String) -> Result<(), DAOError> {
        if !self.members.contains_key(&proposer) {
            return Err(DAOError::MemberNotFound);
        }
        if self.proposals.contains_key(&proposal_id) {
            return Err(DAOError::ProposalExists);
        }
        let proposal = Proposal {
            proposer,
            amount,
            description,
            executed: false,
            votes: HashMap::new(),
        };
        self.proposals.insert(proposal_id, proposal);
        Ok(())
    }

    pub fn vote(&mut self, proposal_id: u64, member_id: u64, vote: bool) -> Result<(), DAOError> {
        if !self.members.contains_key(&member_id) {
            return Err(DAOError::MemberNotFound);
        }
        let proposal = self.proposals.get_mut(&proposal_id).ok_or(DAOError::ProposalNotFound)?;
        if proposal.votes.contains_key(&member_id) {
            return Err(DAOError::DuplicateVote);
        }
        proposal.votes.insert(member_id, vote);
        Ok(())
    }

    pub fn execute_proposal(&mut self, proposal_id: u64) -> Result<(), DAOError> {
        let proposal = self.proposals.get_mut(&proposal_id).ok_or(DAOError::ProposalNotFound)?;
        if proposal.executed {
            return Err(DAOError::ProposalAlreadyExecuted);
        }
        // Compute total stake of DAO members
        let total_stake: u64 = self.members.values().map(|m| m.stake).sum();
        let mut yes_stake: u64 = 0;
        for (member_id, &vote) in proposal.votes.iter() {
            if vote {
                if let Some(member) = self.members.get(member_id) {
                    yes_stake += member.stake;
                }
            }
        }
        // Check if yes votes exceed 50% of total stake (> total_stake/2)
        if yes_stake <= total_stake / 2 {
            return Err(DAOError::InsufficientYesVotes);
        }
        // Check DAO fund sufficiency
        if self.fund < proposal.amount {
            return Err(DAOError::InsufficientFunds);
        }
        self.fund -= proposal.amount;
        proposal.executed = true;
        Ok(())
    }

    pub fn fund_balance(&self) -> u64 {
        self.fund
    }

    pub fn persist_state(&self, file: &str) -> Result<(), DAOError> {
        let mut f = File::create(file).map_err(|e| DAOError::StatePersistenceError(e.to_string()))?;
        // Write fund
        writeln!(f, "FUND {}", self.fund).map_err(|e| DAOError::StatePersistenceError(e.to_string()))?;
        // Write members
        for (member_id, member) in self.members.iter() {
            writeln!(f, "MEMBER {} {}", member_id, member.stake).map_err(|e| DAOError::StatePersistenceError(e.to_string()))?;
        }
        // Write proposals
        for (proposal_id, proposal) in self.proposals.iter() {
            // Replace newlines in description for safety
            let safe_description = proposal.description.replace("\n", " ");
            writeln!(
                f,
                "PROPOSAL {} {} {} {} {}",
                proposal_id,
                proposal.proposer,
                proposal.amount,
                proposal.executed,
                safe_description
            )
            .map_err(|e| DAOError::StatePersistenceError(e.to_string()))?;
            // Write votes for the proposal
            for (voter, vote) in proposal.votes.iter() {
                writeln!(f, "VOTE {} {} {}", proposal_id, voter, vote).map_err(|e| DAOError::StatePersistenceError(e.to_string()))?;
            }
        }
        Ok(())
    }

    pub fn load_state(file: &str) -> Result<DAO, DAOError> {
        if !Path::new(file).exists() {
            return Err(DAOError::StateLoadError("State file not found".to_string()));
        }
        let f = File::open(file).map_err(|e| DAOError::StateLoadError(e.to_string()))?;
        let reader = BufReader::new(f);
        let mut dao = DAO::new(0);
        // Temporary storage for proposals votes mapping
        let mut proposals_temp: HashMap<u64, Proposal> = HashMap::new();
        for line in reader.lines() {
            let line = line.map_err(|e| DAOError::StateLoadError(e.to_string()))?;
            let parts: Vec<&str> = line.splitn(2, ' ').collect();
            if parts.len() < 2 {
                continue;
            }
            match parts[0] {
                "FUND" => {
                    let rest: Vec<&str> = parts[1].split_whitespace().collect();
                    if let Some(fund_str) = rest.get(0) {
                        dao.fund = fund_str.parse::<u64>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                    }
                }
                "MEMBER" => {
                    let rest: Vec<&str> = parts[1].split_whitespace().collect();
                    if rest.len() >= 2 {
                        let member_id = rest[0].parse::<u64>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                        let stake = rest[1].parse::<u64>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                        dao.members.insert(member_id, Member { stake });
                    }
                }
                "PROPOSAL" => {
                    let rest: Vec<&str> = parts[1].split_whitespace().collect();
                    if rest.len() < 5 {
                        return Err(DAOError::ParseError("Invalid proposal line".to_string()));
                    }
                    let proposal_id = rest[0].parse::<u64>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                    let proposer = rest[1].parse::<u64>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                    let amount = rest[2].parse::<u64>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                    let executed = rest[3].parse::<bool>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                    // The rest is description
                    let description = rest[4..].join(" ");
                    let proposal = Proposal {
                        proposer,
                        amount,
                        description,
                        executed,
                        votes: HashMap::new(),
                    };
                    proposals_temp.insert(proposal_id, proposal);
                }
                "VOTE" => {
                    let rest: Vec<&str> = parts[1].split_whitespace().collect();
                    if rest.len() < 3 {
                        return Err(DAOError::ParseError("Invalid vote line".to_string()));
                    }
                    let proposal_id = rest[0].parse::<u64>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                    let voter = rest[1].parse::<u64>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                    let vote = rest[2].parse::<bool>().map_err(|e| DAOError::ParseError(e.to_string()))?;
                    if let Some(proposal) = proposals_temp.get_mut(&proposal_id) {
                        proposal.votes.insert(voter, vote);
                    }
                }
                _ => {}
            }
        }
        dao.proposals = proposals_temp;
        Ok(dao)
    }
}