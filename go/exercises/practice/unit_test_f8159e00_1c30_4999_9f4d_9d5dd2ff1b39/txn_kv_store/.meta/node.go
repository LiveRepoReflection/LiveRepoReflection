package txnkvstore

import (
	"sync"
)

// Node represents a single node in the distributed key-value store
type Node struct {
	id           int
	store        map[string]string    // Main storage for committed key-value pairs
	memoryUsage  int                  // Current memory usage in bytes
	maxMemory    int                  // Maximum memory capacity in bytes
	pendingWrites map[string]map[int64]string // Transaction ID -> key -> value mapping for pending writes
	mu           sync.RWMutex         // Mutex to protect the node's state
}

// NewNode creates a new node with the specified ID and memory capacity
func NewNode(id int, maxMemory int) *Node {
	return &Node{
		id:           id,
		store:        make(map[string]string),
		memoryUsage:  0,
		maxMemory:    maxMemory,
		pendingWrites: make(map[string]map[int64]string),
		mu:           sync.RWMutex{},
	}
}

// Read retrieves the value for the specified key from the node's store
// If the key is not found, returns an empty string
func (n *Node) Read(key string, txnID int64) (string, error) {
	if key == "" {
		return "", ErrEmptyKey
	}

	n.mu.RLock()
	defer n.mu.RUnlock()

	// Check if there's a pending write for this transaction
	if n.pendingWrites[key] != nil && n.pendingWrites[key][txnID] != "" {
		return n.pendingWrites[key][txnID], nil
	}

	// Otherwise, read from the committed store
	if value, exists := n.store[key]; exists {
		return value, nil
	}

	return "", nil
}

// calculateMemorySize returns the memory size of a key-value pair in bytes
func calculateMemorySize(key string, value string) int {
	return len(key) + len(value)
}

// Write stores the key-value pair in the node's pending writes for the transaction
// Returns error if there's insufficient memory
func (n *Node) Write(key string, value string, txnID int64) error {
	if key == "" {
		return ErrEmptyKey
	}

	n.mu.Lock()
	defer n.mu.Unlock()

	// Calculate memory required for this key-value pair
	memoryRequired := calculateMemorySize(key, value)
	
	// Check if this key already exists in the store to account for memory difference
	var existingSize int
	if oldVal, exists := n.store[key]; exists {
		existingSize = calculateMemorySize(key, oldVal)
	}

	// Calculate net memory impact
	netMemoryImpact := memoryRequired - existingSize
	
	// Check if there's enough memory
	if n.memoryUsage+netMemoryImpact > n.maxMemory {
		return ErrInsufficientMemory
	}

	// Initialize the pending writes map for this key if not exists
	if n.pendingWrites[key] == nil {
		n.pendingWrites[key] = make(map[int64]string)
	}

	// Store the pending write
	n.pendingWrites[key][txnID] = value

	return nil
}

// Prepare checks if the node can commit all pending writes for the transaction
// Part of the two-phase commit protocol
func (n *Node) Prepare(txnID int64) error {
	n.mu.Lock()
	defer n.mu.Unlock()

	// Calculate total memory impact of all pending writes
	totalMemoryImpact := 0
	for key, txnWrites := range n.pendingWrites {
		if value, exists := txnWrites[txnID]; exists {
			memoryRequired := calculateMemorySize(key, value)
			
			// Check if this key already exists in the store to account for memory difference
			var existingSize int
			if oldVal, exists := n.store[key]; exists {
				existingSize = calculateMemorySize(key, oldVal)
			}

			// Add net memory impact
			totalMemoryImpact += memoryRequired - existingSize
		}
	}

	// Check if there's enough memory for all pending writes
	if n.memoryUsage+totalMemoryImpact > n.maxMemory {
		return ErrInsufficientMemory
	}

	return nil
}

// Commit applies all pending writes for the transaction to the node's store
func (n *Node) Commit(txnID int64) error {
	n.mu.Lock()
	defer n.mu.Unlock()

	// Apply all pending writes for this transaction
	for key, txnWrites := range n.pendingWrites {
		if value, exists := txnWrites[txnID]; exists {
			// Update memory usage
			newSize := calculateMemorySize(key, value)
			oldSize := 0
			if oldVal, exists := n.store[key]; exists {
				oldSize = calculateMemorySize(key, oldVal)
			}
			
			// Update the store
			n.store[key] = value
			
			// Update memory usage
			n.memoryUsage += (newSize - oldSize)
			
			// Remove the pending write
			delete(txnWrites, txnID)
			
			// Clean up if no more pending writes for this key
			if len(txnWrites) == 0 {
				delete(n.pendingWrites, key)
			}
		}
	}

	return nil
}

// Abort removes all pending writes for the transaction
func (n *Node) Abort(txnID int64) {
	n.mu.Lock()
	defer n.mu.Unlock()

	// Remove all pending writes for this transaction
	for key, txnWrites := range n.pendingWrites {
		if _, exists := txnWrites[txnID]; exists {
			delete(txnWrites, txnID)
			
			// Clean up if no more pending writes for this key
			if len(txnWrites) == 0 {
				delete(n.pendingWrites, key)
			}
		}
	}
}