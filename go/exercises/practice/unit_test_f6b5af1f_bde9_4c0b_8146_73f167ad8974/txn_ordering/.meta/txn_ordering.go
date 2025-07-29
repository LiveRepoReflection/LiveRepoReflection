package txn_ordering

import (
	"sort"
	"time"
)

// Transaction represents a transaction in the decentralized system.
type Transaction struct {
	ID        string // Unique transaction ID (UUID)
	Timestamp int64  // Unix timestamp when the transaction was created
	Sender    string // Public key of the sender
	Data      string // Arbitrary transaction data
	Priority  int    // Priority value assigned to the transaction by the sender. Higher value means higher priority.
}

// Node represents a node in the decentralized network.
type Node struct {
	ID string // Unique Node ID (UUID)
	// Additional fields can be added if needed.
}

// OrderTransactions orders transactions based on timestamp (ascending), priority (descending),
// and sender (lexicographical order) to break ties. It filters out duplicates and invalid transactions.
// A transaction is considered invalid if its timestamp is in the future relative to the current system time.
// The function simulates a decentralized consensus mechanism by processing all transactions received
// on the provided channel. All valid, unique transactions are included and returned in a deterministic order.
func OrderTransactions(nodeID string, transactionStream <-chan Transaction, nodeList []string) []Transaction {
	var validTxs []Transaction
	seen := make(map[string]bool)
	now := time.Now().Unix()

	// Process the incoming transaction stream.
	for tx := range transactionStream {
		// Deduplicate transactions based on their unique ID.
		if _, exists := seen[tx.ID]; exists {
			continue
		}
		seen[tx.ID] = true

		// Validate the transaction timestamp.
		// A timestamp that is in the future relative to current system time is considered invalid.
		if tx.Timestamp > now {
			continue
		}

		// Include the valid transaction for later ordering.
		validTxs = append(validTxs, tx)
	}

	// Sort the transactions using the specified ordering rules.
	// Primary order: Timestamp (earlier transactions come first)
	// Secondary order: Priority (transactions with higher priority come first)
	// Tertiary order: Sender (lexicographical order to break ties)
	sort.Slice(validTxs, func(i, j int) bool {
		if validTxs[i].Timestamp != validTxs[j].Timestamp {
			return validTxs[i].Timestamp < validTxs[j].Timestamp
		}
		if validTxs[i].Priority != validTxs[j].Priority {
			return validTxs[i].Priority > validTxs[j].Priority
		}
		return validTxs[i].Sender < validTxs[j].Sender
	})

	return validTxs
}