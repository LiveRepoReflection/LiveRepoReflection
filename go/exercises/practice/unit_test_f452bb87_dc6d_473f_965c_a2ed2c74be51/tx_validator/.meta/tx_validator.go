package tx_validator

import (
	"sync"
)

type TransactionRecord struct {
	TransactionID string
	Resources     []string
	Nodes         []string
}

type ResourceStateUpdate struct {
	ResourceID   string
	NodeID       string
	StateVersion int
}

type ValidationResult struct {
	TransactionID string
	IsValid       bool
}

var (
	resourceStates = make(map[string]map[string]int)
	mu             sync.RWMutex
)

// ProcessResourceUpdate updates the state version of a resource on a particular node.
func ProcessResourceUpdate(update ResourceStateUpdate) {
	mu.Lock()
	defer mu.Unlock()
	if _, exists := resourceStates[update.ResourceID]; !exists {
		resourceStates[update.ResourceID] = make(map[string]int)
	}
	resourceStates[update.ResourceID][update.NodeID] = update.StateVersion
}

// ValidateTransaction validates a transaction record by ensuring that for every resource involved,
// the state versions across all specified nodes are identical. If any resource is missing an update
// for any node, or if there is a mismatch in state versions, the transaction is considered invalid.
func ValidateTransaction(tx TransactionRecord) ValidationResult {
	mu.RLock()
	defer mu.RUnlock()

	isValid := true
	for _, resource := range tx.Resources {
		nodeVersions, exists := resourceStates[resource]
		if !exists {
			isValid = false
			break
		}

		var expectedVersion int
		first := true
		for _, node := range tx.Nodes {
			version, nodeExists := nodeVersions[node]
			if !nodeExists {
				isValid = false
				break
			}
			if first {
				expectedVersion = version
				first = false
			} else if version != expectedVersion {
				isValid = false
				break
			}
		}
		if !isValid {
			break
		}
	}

	return ValidationResult{
		TransactionID: tx.TransactionID,
		IsValid:       isValid,
	}
}