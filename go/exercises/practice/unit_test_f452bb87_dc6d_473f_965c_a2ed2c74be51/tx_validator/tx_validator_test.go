package tx_validator

import (
	"strconv"
	"sync"
	"testing"
	"time"
)

func TestValidTransaction(t *testing.T) {
	// Create resource state updates for a valid transaction scenario.
	updates := []ResourceStateUpdate{
		{ResourceID: "res1", NodeID: "node1", StateVersion: 5},
		{ResourceID: "res1", NodeID: "node2", StateVersion: 5},
		{ResourceID: "res2", NodeID: "node1", StateVersion: 3},
		{ResourceID: "res2", NodeID: "node2", StateVersion: 3},
	}

	for _, update := range updates {
		ProcessResourceUpdate(update)
	}

	tx := TransactionRecord{
		TransactionID: "tx_valid_1",
		Resources:     []string{"res1", "res2"},
		Nodes:         []string{"node1", "node2"},
	}

	result := ValidateTransaction(tx)
	if !result.IsValid {
		t.Errorf("Expected transaction to be valid, but got invalid for %v", tx)
	}
}

func TestInvalidTransaction(t *testing.T) {
	// Mismatched state versions among resources.
	updates := []ResourceStateUpdate{
		{ResourceID: "res1", NodeID: "node1", StateVersion: 7},
		{ResourceID: "res1", NodeID: "node2", StateVersion: 7},
		{ResourceID: "res2", NodeID: "node1", StateVersion: 4},
		{ResourceID: "res2", NodeID: "node2", StateVersion: 5}, // mismatch
	}

	for _, update := range updates {
		ProcessResourceUpdate(update)
	}

	tx := TransactionRecord{
		TransactionID: "tx_invalid_1",
		Resources:     []string{"res1", "res2"},
		Nodes:         []string{"node1", "node2"},
	}

	result := ValidateTransaction(tx)
	if result.IsValid {
		t.Errorf("Expected transaction to be invalid due to state mismatch, but got valid for %v", tx)
	}
}

func TestMissingResourceUpdates(t *testing.T) {
	// One resource is missing an update on one of the nodes.
	updates := []ResourceStateUpdate{
		{ResourceID: "res1", NodeID: "node1", StateVersion: 2},
		// Missing update for res1 on node2
		{ResourceID: "res2", NodeID: "node1", StateVersion: 2},
		{ResourceID: "res2", NodeID: "node2", StateVersion: 2},
	}

	for _, update := range updates {
		ProcessResourceUpdate(update)
	}

	tx := TransactionRecord{
		TransactionID: "tx_missing_update",
		Resources:     []string{"res1", "res2"},
		Nodes:         []string{"node1", "node2"},
	}

	result := ValidateTransaction(tx)
	if result.IsValid {
		t.Errorf("Expected transaction to be invalid due to missing update for a resource, but got valid for %v", tx)
	}
}

func TestEventualConsistency(t *testing.T) {
	// Initially invalid, then update to eventually become valid.
	initialUpdates := []ResourceStateUpdate{
		{ResourceID: "res1", NodeID: "node1", StateVersion: 10},
		{ResourceID: "res1", NodeID: "node2", StateVersion: 9}, // mismatch initially
	}

	for _, update := range initialUpdates {
		ProcessResourceUpdate(update)
	}

	tx := TransactionRecord{
		TransactionID: "tx_eventual_consistency",
		Resources:     []string{"res1"},
		Nodes:         []string{"node1", "node2"},
	}

	result := ValidateTransaction(tx)
	if result.IsValid {
		t.Errorf("Expected transaction to be invalid initially due to mismatch, but got valid for %v", tx)
	}

	// Wait to simulate delay before eventual consistency update.
	time.Sleep(50 * time.Millisecond)

	// Correct the mismatch.
	ProcessResourceUpdate(ResourceStateUpdate{ResourceID: "res1", NodeID: "node2", StateVersion: 10})

	// Allow time for the update to propagate.
	time.Sleep(50 * time.Millisecond)

	result = ValidateTransaction(tx)
	if !result.IsValid {
		t.Errorf("Expected transaction to be eventually valid after correcting update, but got invalid for %v", tx)
	}
}

func TestConcurrentProcessing(t *testing.T) {
	var wg sync.WaitGroup
	numGoroutines := 50

	// Pre-populate updates for a consistent state.
	// We start with version 0 for the resource across nodes.
	ProcessResourceUpdate(ResourceStateUpdate{ResourceID: "res_concurrent", NodeID: "node1", StateVersion: 0})
	ProcessResourceUpdate(ResourceStateUpdate{ResourceID: "res_concurrent", NodeID: "node2", StateVersion: 0})

	// Perform concurrent updates and validations.
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(version int) {
			defer wg.Done()
			// Update resource versions concurrently.
			ProcessResourceUpdate(ResourceStateUpdate{ResourceID: "res_concurrent", NodeID: "node1", StateVersion: version})
			ProcessResourceUpdate(ResourceStateUpdate{ResourceID: "res_concurrent", NodeID: "node2", StateVersion: version})

			tx := TransactionRecord{
				TransactionID: "tx_concurrent_" + strconv.Itoa(version),
				Resources:     []string{"res_concurrent"},
				Nodes:         []string{"node1", "node2"},
			}
			result := ValidateTransaction(tx)
			// Due to concurrency, the result might be transitional.
			// Ensure eventual consistency by revalidating after a short pause.
			time.Sleep(10 * time.Millisecond)
			result = ValidateTransaction(tx)
			if !result.IsValid {
				t.Errorf("Expected transaction to be valid after eventual consistency for version %d, got invalid", version)
			}
		}(i)
	}
	wg.Wait()
}