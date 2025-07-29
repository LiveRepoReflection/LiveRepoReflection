package txnkvstore

import (
	"fmt"
	"sync"
	"sync/atomic"
)

// Transaction represents a transaction in the distributed key-value store
type Transaction struct {
	txnID         int64         // Unique transaction ID
	coordinator   *Coordinator  // Reference to the coordinator
	affectedNodes map[int]bool  // Set of nodes affected by this transaction
	status        int32         // Transaction status (active, prepared, committed, aborted)
	mu            sync.Mutex    // Mutex to protect the transaction's state
}

// Read retrieves the value for the specified key from the specified node
func (t *Transaction) Read(nodeID int, key string) (string, error) {
	// Check if the transaction is still active
	if atomic.LoadInt32(&t.status) != StatusActive {
		return "", ErrTransactionCompleted
	}

	t.mu.Lock()
	defer t.mu.Unlock()

	// Get the node
	node, err := t.coordinator.getNode(nodeID)
	if err != nil {
		return "", err
	}

	// Read the value from the node
	return node.Read(key, t.txnID)
}

// Write stores the key-value pair in the specified node
func (t *Transaction) Write(nodeID int, key string, value string) error {
	// Check if the transaction is still active
	if atomic.LoadInt32(&t.status) != StatusActive {
		return ErrTransactionCompleted
	}

	t.mu.Lock()
	defer t.mu.Unlock()

	// Get the node
	node, err := t.coordinator.getNode(nodeID)
	if err != nil {
		return err
	}

	// Write the value to the node
	err = node.Write(key, value, t.txnID)
	if err != nil {
		return err
	}

	// Mark the node as affected by this transaction
	t.affectedNodes[nodeID] = true

	return nil
}

// Commit performs a two-phase commit to make all changes permanent
func (t *Transaction) Commit() error {
	// Use compare-and-swap to ensure we only transition from active to prepared
	if !atomic.CompareAndSwapInt32(&t.status, StatusActive, StatusPrepared) {
		return ErrTransactionCompleted
	}

	t.mu.Lock()
	defer t.mu.Unlock()

	// Phase 1: Prepare (ask all nodes if they can commit)
	for nodeID := range t.affectedNodes {
		node, err := t.coordinator.getNode(nodeID)
		if err != nil {
			// If any node fails to prepare, abort the transaction
			t.abortUnlocked()
			return fmt.Errorf("prepare phase failed for node %d: %w", nodeID, err)
		}

		err = node.Prepare(t.txnID)
		if err != nil {
			// If any node fails to prepare, abort the transaction
			t.abortUnlocked()
			return fmt.Errorf("prepare phase failed for node %d: %w", nodeID, err)
		}
	}

	// Phase 2: Commit (tell all nodes to commit)
	for nodeID := range t.affectedNodes {
		node, err := t.coordinator.getNode(nodeID)
		if err != nil {
			// This is a critical failure after prepare phase
			// In a real system, we would need a recovery mechanism here
			// For this assignment, we'll simply return an error
			atomic.StoreInt32(&t.status, StatusCommitted) // Still mark as committed since we can't roll back
			return fmt.Errorf("commit phase failed for node %d: %w", nodeID, err)
		}

		err = node.Commit(t.txnID)
		if err != nil {
			// This is a critical failure after prepare phase
			// In a real system, we would need a recovery mechanism here
			atomic.StoreInt32(&t.status, StatusCommitted) // Still mark as committed since we can't roll back
			return fmt.Errorf("commit phase failed for node %d: %w", nodeID, err)
		}
	}

	atomic.StoreInt32(&t.status, StatusCommitted)
	return nil
}

// Abort aborts the transaction, rolling back all changes
func (t *Transaction) Abort() error {
	// Use compare-and-swap to ensure we only transition from active to aborted
	if !atomic.CompareAndSwapInt32(&t.status, StatusActive, StatusAborted) {
		return ErrTransactionCompleted
	}

	t.mu.Lock()
	defer t.mu.Unlock()

	return t.abortUnlocked()
}

// abortUnlocked implements the abort logic without locking
// Caller must hold the transaction mutex
func (t *Transaction) abortUnlocked() error {
	// Notify all affected nodes to abort
	for nodeID := range t.affectedNodes {
		node, err := t.coordinator.getNode(nodeID)
		if err != nil {
			continue // Best effort: try to abort on all available nodes
		}
		node.Abort(t.txnID)
	}

	atomic.StoreInt32(&t.status, StatusAborted)
	return nil
}