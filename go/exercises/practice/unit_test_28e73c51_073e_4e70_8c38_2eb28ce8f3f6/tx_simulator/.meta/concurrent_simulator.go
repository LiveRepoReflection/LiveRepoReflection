package tx_simulator

import (
	"sync"
)

// ConcurrentSimulateTransactions is an advanced version of the transaction simulator
// that uses goroutines to simulate concurrently processing transactions.
// This implementation is more efficient for a large number of transactions.
func ConcurrentSimulateTransactions(n int, transactions []Transaction, nodeBehaviors map[int][]string) map[string]bool {
	results := make(map[string]bool)
	resultsMutex := sync.Mutex{}
	
	// Create a wait group to wait for all transaction processing to complete
	var wg sync.WaitGroup
	wg.Add(len(transactions))
	
	// Process each transaction concurrently
	for _, tx := range transactions {
		go func(transaction Transaction) {
			defer wg.Done()
			
			// Always commit if there are no involved nodes
			if len(transaction.InvolvedNodes) == 0 {
				resultsMutex.Lock()
				results[transaction.ID] = true
				resultsMutex.Unlock()
				return
			}
			
			// Step 1: Prepare phase
			prepareSuccess := processTransaction(n, transaction, nodeBehaviors)
			
			// Step 2: Record result
			resultsMutex.Lock()
			results[transaction.ID] = prepareSuccess
			resultsMutex.Unlock()
		}(tx)
	}
	
	// Wait for all transaction processing to complete
	wg.Wait()
	
	return results
}

// processTransaction handles the prepare phase for a single transaction
// and determines if it should be committed or rolled back
func processTransaction(n int, tx Transaction, nodeBehaviors map[int][]string) bool {
	// Create a channel to collect responses from nodes
	type nodeResponse struct {
		nodeID int
		ack    bool
	}
	
	// If there are duplicate node IDs, we'll deduplicate them
	uniqueNodes := make(map[int]bool)
	for _, nodeID := range tx.InvolvedNodes {
		if nodeID >= 0 && nodeID < n {
			uniqueNodes[nodeID] = true
		}
	}
	
	// Check each involved node in the transaction
	for nodeID := range uniqueNodes {
		// Check if this node would NACK for this operation
		behaviors, exists := nodeBehaviors[nodeID]
		if exists {
			for _, behavior := range behaviors {
				if behavior == tx.Operation {
					// If any node NACKs, the transaction fails
					return false
				}
			}
		}
	}
	
	// All nodes ACKed, so the transaction succeeds
	return true
}