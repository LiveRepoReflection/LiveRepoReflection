use std::collections::{HashMap, HashSet};
use std::sync::{Arc, Mutex};

#[derive(Debug, Clone, PartialEq, Eq)]
pub enum ProposalStatus {
    Pending,
    Passed,
    Failed,
    Executed,
}

struct Proposal {
    id: u64,
    proposer: String,
    recipient: String,
    amount: u64,
    description: String,
    status: ProposalStatus,
    yes_votes: HashSet<String>,
    no_votes: HashSet<String>,
}

impl Proposal {
    fn new(
        id: u64,
        proposer: String,
        recipient: String,
        amount: u64,
        description: String,
    ) -> Self {
        Proposal {
            id,
            proposer,
            recipient,
            amount,
            description,
            status: ProposalStatus::Pending,
            yes_votes: HashSet::new(),
            no_votes: HashSet::new(),
        }
    }

    fn vote(&mut self, voter: String, vote: bool) -> bool {
        // Prevent double voting
        if self.yes_votes.contains(&voter) || self.no_votes.contains(&voter) {
            return false;
        }

        // Add the vote to the appropriate set
        if vote {
            self.yes_votes.insert(voter);
        } else {
            self.no_votes.insert(voter);
        }

        true
    }

    fn total_votes(&self) -> usize {
        self.yes_votes.len() + self.no_votes.len()
    }

    fn yes_percentage(&self) -> u8 {
        if self.total_votes() == 0 {
            return 0;
        }
        
        ((self.yes_votes.len() as f64 / self.total_votes() as f64) * 100.0) as u8
    }
}

pub struct DAO {
    treasury_balance: u64,
    quorum_percentage: u8,
    threshold_percentage: u8,
    members: HashSet<String>,
    proposals: HashMap<u64, Proposal>,
    next_proposal_id: u64,
    transaction_lock: Arc<Mutex<()>>,
}

impl DAO {
    pub fn new(initial_balance: u64, quorum_percentage: u8, threshold_percentage: u8) -> Self {
        // Validate quorum and threshold percentages
        let quorum = std::cmp::min(quorum_percentage, 100);
        let threshold = std::cmp::min(threshold_percentage, 100);

        DAO {
            treasury_balance: initial_balance,
            quorum_percentage: quorum,
            threshold_percentage: threshold,
            members: HashSet::new(),
            proposals: HashMap::new(),
            next_proposal_id: 1,
            transaction_lock: Arc::new(Mutex::new(())),
        }
    }

    pub fn add_member(&mut self, address: String) {
        self.members.insert(address);
    }

    pub fn get_member_count(&self) -> usize {
        self.members.len()
    }

    pub fn submit_proposal(
        &mut self,
        proposer: String,
        recipient: String,
        amount: u64,
        description: String,
    ) -> u64 {
        // Ensure the proposer is a member
        if !self.members.contains(&proposer) {
            return 0; // Invalid proposal ID
        }

        // Create a new proposal
        let proposal_id = self.next_proposal_id;
        let proposal = Proposal::new(
            proposal_id,
            proposer,
            recipient,
            amount,
            description,
        );

        // Store the proposal
        self.proposals.insert(proposal_id, proposal);
        self.next_proposal_id += 1;

        proposal_id
    }

    pub fn vote(&mut self, proposal_id: u64, voter: String, vote: bool) -> bool {
        // Ensure the voter is a member
        if !self.members.contains(&voter) {
            return false;
        }

        // Find the proposal
        if let Some(proposal) = self.proposals.get_mut(&proposal_id) {
            // Ensure the proposal is still pending
            if proposal.status != ProposalStatus::Pending {
                return false;
            }

            // Register the vote
            proposal.vote(voter, vote)
        } else {
            false
        }
    }

    pub fn execute_proposal(&mut self, proposal_id: u64) -> bool {
        // Acquire lock to ensure atomic transaction
        let _lock = self.transaction_lock.lock().unwrap();

        // Find the proposal
        if let Some(proposal) = self.proposals.get_mut(&proposal_id) {
            // Ensure the proposal is still pending
            if proposal.status != ProposalStatus::Pending {
                return false;
            }

            // Check if the quorum requirement is met
            let quorum_required = (self.members.len() as f64 * (self.quorum_percentage as f64 / 100.0)) as usize;
            if proposal.total_votes() < quorum_required {
                proposal.status = ProposalStatus::Failed;
                return false;
            }

            // Check if the threshold requirement is met
            if proposal.yes_percentage() < self.threshold_percentage {
                proposal.status = ProposalStatus::Failed;
                return false;
            }

            // Check if the treasury has sufficient funds
            if proposal.amount > self.treasury_balance {
                proposal.status = ProposalStatus::Failed;
                return false;
            }

            // Execute the proposal
            if proposal.amount > 0 {
                self.treasury_balance = self.treasury_balance.saturating_sub(proposal.amount);
            }
            proposal.status = ProposalStatus::Executed;
            true
        } else {
            false
        }
    }

    pub fn get_treasury_balance(&self) -> u64 {
        self.treasury_balance
    }

    pub fn get_proposal_status(&self, proposal_id: u64) -> ProposalStatus {
        self.proposals
            .get(&proposal_id)
            .map(|p| p.status.clone())
            .unwrap_or(ProposalStatus::Failed)
    }
}