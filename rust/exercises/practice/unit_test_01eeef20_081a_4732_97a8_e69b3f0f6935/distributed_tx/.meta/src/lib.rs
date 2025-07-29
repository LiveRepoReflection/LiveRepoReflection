use std::sync::Mutex;
use std::thread;
use std::time::Duration;

#[derive(Debug, PartialEq, Eq, Clone)]
pub enum Outcome {
    Commit,
    Abort,
}

pub struct TransactionCoordinator {
    log: Mutex<Vec<(String, Outcome)>>,
}

impl TransactionCoordinator {
    pub fn new() -> Self {
        TransactionCoordinator {
            log: Mutex::new(Vec::new()),
        }
    }

    pub fn execute_transaction(&self, tx_id: String, participants: Vec<String>) -> Outcome {
        let mut votes = Vec::new();
        for participant in &participants {
            let vote = Self::simulate_vote(participant);
            votes.push(vote);
        }
        let outcome = if votes.contains(&Outcome::Abort) {
            Outcome::Abort
        } else {
            Outcome::Commit
        };
        {
            let mut log = self.log.lock().unwrap();
            log.push((tx_id, outcome.clone()));
        }
        outcome
    }

    pub fn simulate_crash_and_recover(&self, tx_id: String, participants: Vec<String>) -> Outcome {
        // Phase 1: Voting Phase (simulated)
        let mut votes = Vec::new();
        for participant in &participants {
            let vote = Self::simulate_vote(participant);
            votes.push(vote);
        }
        let outcome = if votes.contains(&Outcome::Abort) {
            Outcome::Abort
        } else {
            Outcome::Commit
        };
        // Simulate crash by not sending final decision immediately.
        // "Recover" by reading the persistent log (in our simulation, we simply log the outcome)
        {
            let mut log = self.log.lock().unwrap();
            log.push((tx_id, outcome.clone()));
        }
        outcome
    }

    fn simulate_vote(participant: &String) -> Outcome {
        if participant.starts_with("fail") {
            Outcome::Abort
        } else if participant.starts_with("delay") {
            thread::sleep(Duration::from_millis(50));
            Outcome::Commit
        } else {
            Outcome::Commit
        }
    }
}