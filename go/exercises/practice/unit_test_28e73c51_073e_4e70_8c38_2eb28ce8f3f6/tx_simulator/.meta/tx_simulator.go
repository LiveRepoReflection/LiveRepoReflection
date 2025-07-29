package tx_simulator

// Transaction represents a distributed transaction involving multiple nodes
type Transaction struct {
	ID            string
	InvolvedNodes []int
	Operation     string
}

// SimulateTransactions simulates the execution of distributed transactions
// using a two-phase commit protocol and returns a map indicating whether
// each transaction was committed (true) or rolled back (false).
func SimulateTransactions(n int, transactions []Transaction, nodeBehaviors map[int][]string) map[string]bool {
	results := make(map[string]bool)

	// Process each transaction
	for _, tx := range transactions {
		// Always commit if there are no involved nodes
		if len(tx.InvolvedNodes) == 0 {
			results[tx.ID] = true
			continue
		}

		// Step 1: Prepare phase - check if any node would NACK
		prepareSuccess := true
		for _, nodeID := range tx.InvolvedNodes {
			// Skip nodes that are out of range
			if nodeID < 0 || nodeID >= n {
				continue
			}

			// Check if this node would NACK for this operation
			behaviors, exists := nodeBehaviors[nodeID]
			if exists {
				for _, behavior := range behaviors {
					if behavior == tx.Operation {
						prepareSuccess = false
						break
					}
				}
			}

			// If we've already determined the transaction will fail, no need to check more nodes
			if !prepareSuccess {
				break
			}
		}

		// Step 2: Commit or rollback based on prepare phase results
		results[tx.ID] = prepareSuccess
	}

	return results
}