package tx_key_value

import (
	"errors"
	"fmt"
	"sync"
	"time"
)

type valueEntry struct {
	value string
	ts    int64
}

type Node struct {
	address string
	data    map[string]valueEntry
	mu      sync.Mutex
}

func NewNode(address string) *Node {
	return &Node{
		address: address,
		data:    make(map[string]valueEntry),
	}
}

type Transaction struct {
	id     string
	writes map[string]valueEntry
}

type DistributedKVStore struct {
	nodes        []*Node
	transactions map[string]*Transaction
	mu           sync.Mutex
	txCounter    int64
}

func NewDistributedKVStore(addresses []string) (*DistributedKVStore, error) {
	if len(addresses) < 3 {
		return nil, errors.New("need at least 3 nodes for replication")
	}
	nodes := make([]*Node, 0, len(addresses))
	for _, addr := range addresses {
		nodes = append(nodes, NewNode(addr))
	}
	store := &DistributedKVStore{
		nodes:        nodes,
		transactions: make(map[string]*Transaction),
		txCounter:    0,
	}
	return store, nil
}

// Simulated Agree function that returns the same data.
func Agree(data interface{}) interface{} {
	// In a real system, a consensus algorithm would ensure agreement.
	return data
}

func (store *DistributedKVStore) generateTxID() string {
	store.txCounter++
	return fmt.Sprintf("tx_%d", store.txCounter)
}

func (store *DistributedKVStore) BeginTransaction() (string, error) {
	store.mu.Lock()
	defer store.mu.Unlock()
	txID := store.generateTxID()
	tx := &Transaction{
		id:     txID,
		writes: make(map[string]valueEntry),
	}
	store.transactions[txID] = tx
	return txID, nil
}

func (store *DistributedKVStore) getTransaction(txID string) (*Transaction, error) {
	store.mu.Lock()
	defer store.mu.Unlock()
	tx, ok := store.transactions[txID]
	if !ok {
		return nil, errors.New("invalid transaction id")
	}
	return tx, nil
}

func (store *DistributedKVStore) Read(txID string, key string) (string, error) {
	tx, err := store.getTransaction(txID)
	if err != nil {
		return "", err
	}
	// Check for a pending write in the transaction.
	if ve, ok := tx.writes[key]; ok {
		return ve.value, nil
	}
	// Read from the first node (simulate consistent read from a replicated store).
	node := store.nodes[0]
	node.mu.Lock()
	defer node.mu.Unlock()
	if entry, ok := node.data[key]; ok {
		return entry.value, nil
	}
	// Return empty string if key does not exist.
	return "", nil
}

func (store *DistributedKVStore) Write(txID string, key string, value string) error {
	tx, err := store.getTransaction(txID)
	if err != nil {
		return err
	}
	// Generate a logical timestamp.
	ts := time.Now().UnixNano()
	tx.writes[key] = valueEntry{
		value: value,
		ts:    ts,
	}
	return nil
}

func (store *DistributedKVStore) Commit(txID string) error {
	store.mu.Lock()
	tx, ok := store.transactions[txID]
	if !ok {
		store.mu.Unlock()
		return errors.New("invalid transaction id")
	}
	// Simulate reaching consensus on the transaction's writes.
	agreedWrites, ok := Agree(tx.writes).(map[string]valueEntry)
	if !ok {
		store.mu.Unlock()
		return errors.New("consensus agreement failed")
	}
	// Commit the writes to all nodes with Last-Writer-Wins conflict resolution.
	for _, node := range store.nodes {
		node.mu.Lock()
		for key, newEntry := range agreedWrites {
			current, exists := node.data[key]
			if !exists || newEntry.ts > current.ts {
				node.data[key] = newEntry
			}
		}
		node.mu.Unlock()
	}
	// Remove the transaction.
	delete(store.transactions, txID)
	store.mu.Unlock()
	return nil
}