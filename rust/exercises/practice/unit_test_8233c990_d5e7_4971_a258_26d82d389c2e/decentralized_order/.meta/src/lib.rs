use std::cmp::Ordering;

pub const THRESHOLD_MILLISECONDS: u64 = 500;

#[derive(Clone, Debug)]
pub struct Transaction {
    pub id: u64,
    pub timestamp: u64,
}

#[derive(Debug)]
pub struct Node {
    pub id: u32,
    pub transactions: Vec<Transaction>,
    final_order: Option<Vec<u64>>,
}

impl Node {
    pub fn new(id: u32) -> Self {
        Node {
            id,
            transactions: Vec::new(),
            final_order: None,
        }
    }

    pub fn receive_transaction(&mut self, transaction: Transaction) {
        self.transactions.push(transaction);
    }

    pub fn propose_order(&self) -> Vec<u64> {
        let mut txs = self.transactions.clone();
        // Sort transactions using custom rules:
        // If the difference between timestamps is at least THRESHOLD_MILLISECONDS, then the one with the earlier timestamp should come first.
        // If the difference is less than THRESHOLD_MILLISECONDS, use the transaction id to break the tie.
        txs.sort_by(|a, b| {
            let ts_diff = if a.timestamp > b.timestamp {
                a.timestamp - b.timestamp
            } else {
                b.timestamp - a.timestamp
            };

            if ts_diff >= THRESHOLD_MILLISECONDS {
                a.timestamp.cmp(&b.timestamp)
            } else {
                a.id.cmp(&b.id)
            }
        });
        txs.into_iter().map(|t| t.id).collect()
    }

    pub fn receive_proposal(&mut self, _proposal: Vec<u64>, _proposer_id: u32) {
        // In a real system, this method would process the incoming proposal.
        // Here we leave it blank as the consensus mechanism is simplified.
    }

    pub fn accept_proposal(&mut self, proposal: Vec<u64>) {
        self.final_order = Some(proposal);
    }

    pub fn get_final_order(&self) -> Vec<u64> {
        match &self.final_order {
            Some(order) => order.clone(),
            None => self.propose_order(),
        }
    }
}