package txnkvstore

import (
	"sync"
	"sync/atomic"
)

// Coordinator manages transactions and coordinates operations across multiple nodes
type Coordinator struct {
	nodes        []*Node       // Array of nodes in the system
	lastTxnID    int64         // Last transaction ID assigned
	activeTxns   sync.Map      // Map of active transactions: txnID -> *Transaction
	mu           sync.Mutex    // Mutex to protect coordinator state
}

// NewCoordinator creates a new coordinator with n nodes, each with m memory capacity
func NewCoordinator(n int, m int) *Coordinator {
	coordinator := &Coordinator{
		nodes:      make([]*Node, n),
		lastTxnID:  0,
		activeTxns: sync.Map{},
		mu:         sync.Mutex{},
	}

	// Initialize nodes
	for i := 0; i < n; i++ {
		coordinator.nodes[i] = NewNode(i, m)
	}

	return coordinator
}

// Begin starts a new transaction
func (c *Coordinator) Begin() *Transaction {
	c.mu.Lock()
	defer c.mu.Unlock()

	// Generate a new transaction ID
	txnID := atomic.AddInt64(&c.lastTxnID, 1)

	// Create a new transaction
	txn := &Transaction{
		txnID:         txnID,
		coordinator:   c,
		affectedNodes: make(map[int]bool),
		status:        StatusActive,
		mu:            sync.Mutex{},
	}

	// Store the transaction in the active transactions map
	c.activeTxns.Store(txnID, txn)

	return txn
}

// getNode returns the node with the specified ID
func (c *Coordinator) getNode(nodeID int) (*Node, error) {
	if nodeID < 0 || nodeID >= len(c.nodes) {
		return nil, ErrInvalidNodeID
	}

	return c.nodes[nodeID], nil
}