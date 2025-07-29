package dist_tx_kv

// This test file defines the test cases for the distributed transactional key-value store

import (
	"errors"
	"sync"
	"time"
)

// Operation types
const (
	OperationRead   = "read"
	OperationWrite  = "write"
	OperationCommit = "commit"
	OperationAbort  = "abort"
)

// Operation represents a single operation within a transaction
type Operation struct {
	Type  string
	Key   string
	Value string
}

// TransactionTestCase represents a test case for a transaction
type TransactionTestCase struct {
	Description string
	Operations  []Operation
	Expected    []interface{}
}

// SystemTestCase represents a test case for the entire system
type SystemTestCase struct {
	Description      string
	NodeCount        int
	Transactions     [][]Operation
	ExpectedResults  [][]interface{}
	ExpectedKeyState map[string]string
}

// ConcurrencyTestCase represents a test case for concurrent transactions
type ConcurrencyTestCase struct {
	Description      string
	NodeCount        int
	TransactionSets  [][]Operation
	Concurrency      int
	Duration         time.Duration
	MinSuccessRate   float64
	ExpectedKeyState map[string]string
}

// FailureTestCase represents a test case with node failures
type FailureTestCase struct {
	Description      string
	NodeCount        int
	Transactions     [][]Operation
	FailureScenarios []FailureScenario
	ExpectedResults  [][]interface{}
	ExpectedKeyState map[string]string
}

// FailureScenario describes a node failure event
type FailureScenario struct {
	NodeID         int
	FailureTime    time.Duration
	RecoveryTime   time.Duration
	FailureType    string // "crash", "network_partition", etc.
	AffectedNodes  []int  // Used for network partition scenarios
	PartitionGroup int    // Used to group nodes into partitions
}

// MockNode implements the Node interface for testing
type MockNode struct {
	ID       int
	Store    map[string]string
	Available bool
	mu       sync.RWMutex
}

func NewMockNode(id int) *MockNode {
	return &MockNode{
		ID:        id,
		Store:     make(map[string]string),
		Available: true,
	}
}

func (n *MockNode) Get(key string) (string, error) {
	n.mu.RLock()
	defer n.mu.RUnlock()
	
	if !n.Available {
		return "", errors.New("node is not available")
	}
	
	value, exists := n.Store[key]
	if !exists {
		return "", nil
	}
	return value, nil
}

func (n *MockNode) Put(key, value string) error {
	n.mu.Lock()
	defer n.mu.Unlock()
	
	if !n.Available {
		return errors.New("node is not available")
	}
	
	n.Store[key] = value
	return nil
}

func (n *MockNode) Delete(key string) error {
	n.mu.Lock()
	defer n.mu.Unlock()
	
	if !n.Available {
		return errors.New("node is not available")
	}
	
	delete(n.Store, key)
	return nil
}

func (n *MockNode) Fail() {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.Available = false
}

func (n *MockNode) Recover() {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.Available = true
}

// Basic transaction test cases
var basicTransactionTestCases = []TransactionTestCase{
	{
		Description: "Simple read-write-commit transaction",
		Operations: []Operation{
			{Type: OperationRead, Key: "key1"},
			{Type: OperationWrite, Key: "key1", Value: "value1"},
			{Type: OperationCommit},
		},
		Expected: []interface{}{
			nil,     // key1 doesn't exist initially
			nil,     // write operation returns nil
			true,    // commit operation returns true
		},
	},
	{
		Description: "Read after write in same transaction",
		Operations: []Operation{
			{Type: OperationWrite, Key: "key2", Value: "value2"},
			{Type: OperationRead, Key: "key2"},
			{Type: OperationCommit},
		},
		Expected: []interface{}{
			nil,       // write operation returns nil
			"value2",  // read returns the uncommitted value
			true,      // commit operation returns true
		},
	},
	{
		Description: "Multiple writes and reads",
		Operations: []Operation{
			{Type: OperationWrite, Key: "key3", Value: "value3"},
			{Type: OperationWrite, Key: "key4", Value: "value4"},
			{Type: OperationRead, Key: "key3"},
			{Type: OperationRead, Key: "key4"},
			{Type: OperationCommit},
		},
		Expected: []interface{}{
			nil,       // write operation returns nil
			nil,       // write operation returns nil
			"value3",  // read returns the uncommitted value
			"value4",  // read returns the uncommitted value
			true,      // commit operation returns true
		},
	},
	{
		Description: "Aborted transaction",
		Operations: []Operation{
			{Type: OperationWrite, Key: "key5", Value: "value5"},
			{Type: OperationAbort},
		},
		Expected: []interface{}{
			nil,  // write operation returns nil
			true, // abort operation always returns true
		},
	},
}

// System test cases
var systemTestCases = []SystemTestCase{
	{
		Description: "Multiple transactions on different keys",
		NodeCount: 3,
		Transactions: [][]Operation{
			{
				{Type: OperationWrite, Key: "key1", Value: "tx1-value1"},
				{Type: OperationCommit},
			},
			{
				{Type: OperationWrite, Key: "key2", Value: "tx2-value2"},
				{Type: OperationCommit},
			},
			{
				{Type: OperationRead, Key: "key1"},
				{Type: OperationRead, Key: "key2"},
				{Type: OperationCommit},
			},
		},
		ExpectedResults: [][]interface{}{
			{nil, true},
			{nil, true},
			{"tx1-value1", "tx2-value2", true},
		},
		ExpectedKeyState: map[string]string{
			"key1": "tx1-value1",
			"key2": "tx2-value2",
		},
	},
	{
		Description: "Transactions with conflicts",
		NodeCount: 3,
		Transactions: [][]Operation{
			{
				{Type: OperationWrite, Key: "key3", Value: "tx1-value3"},
				{Type: OperationCommit},
			},
			{
				{Type: OperationRead, Key: "key3"},
				{Type: OperationWrite, Key: "key3", Value: "tx2-value3"},
				{Type: OperationCommit},
			},
			{
				{Type: OperationRead, Key: "key3"},
				{Type: OperationCommit},
			},
		},
		ExpectedResults: [][]interface{}{
			{nil, true},
			{"tx1-value3", nil, true},
			{"tx2-value3", true},
		},
		ExpectedKeyState: map[string]string{
			"key3": "tx2-value3",
		},
	},
	{
		Description: "Aborted and committed transactions mix",
		NodeCount: 3,
		Transactions: [][]Operation{
			{
				{Type: OperationWrite, Key: "key4", Value: "tx1-value4"},
				{Type: OperationAbort},
			},
			{
				{Type: OperationRead, Key: "key4"},
				{Type: OperationWrite, Key: "key4", Value: "tx2-value4"},
				{Type: OperationCommit},
			},
			{
				{Type: OperationRead, Key: "key4"},
				{Type: OperationCommit},
			},
		},
		ExpectedResults: [][]interface{}{
			{nil, true},
			{nil, nil, true},
			{"tx2-value4", true},
		},
		ExpectedKeyState: map[string]string{
			"key4": "tx2-value4",
		},
	},
}

// Concurrency test cases
var concurrencyTestCases = []ConcurrencyTestCase{
	{
		Description: "High concurrency on different keys",
		NodeCount: 5,
		TransactionSets: [][]Operation{
			{
				{Type: OperationWrite, Key: "concurrent_key1", Value: "value1"},
				{Type: OperationCommit},
			},
			{
				{Type: OperationWrite, Key: "concurrent_key2", Value: "value2"},
				{Type: OperationCommit},
			},
			{
				{Type: OperationWrite, Key: "concurrent_key3", Value: "value3"},
				{Type: OperationCommit},
			},
		},
		Concurrency: 100,
		Duration: 5 * time.Second,
		MinSuccessRate: 0.95,
		ExpectedKeyState: map[string]string{
			"concurrent_key1": "value1",
			"concurrent_key2": "value2",
			"concurrent_key3": "value3",
		},
	},
	{
		Description: "High contention on same key",
		NodeCount: 5,
		TransactionSets: [][]Operation{
			{
				{Type: OperationRead, Key: "contention_key"},
				{Type: OperationWrite, Key: "contention_key", Value: "value_a"},
				{Type: OperationCommit},
			},
			{
				{Type: OperationRead, Key: "contention_key"},
				{Type: OperationWrite, Key: "contention_key", Value: "value_b"},
				{Type: OperationCommit},
			},
		},
		Concurrency: 50,
		Duration: 5 * time.Second,
		MinSuccessRate: 0.5, // Lower success rate due to conflicts
		ExpectedKeyState: map[string]string{
			// We can't predict the final value, but a value should exist
			"contention_key": "",
		},
	},
}

// Failure test cases
var failureTestCases = []FailureTestCase{
	{
		Description: "Simple node crash and recovery",
		NodeCount: 5,
		Transactions: [][]Operation{
			{
				{Type: OperationWrite, Key: "failure_key1", Value: "before_failure"},
				{Type: OperationCommit},
			},
			// This will be attempted during the failure
			{
				{Type: OperationWrite, Key: "failure_key2", Value: "during_failure"},
				{Type: OperationCommit},
			},
			// This will be after recovery
			{
				{Type: OperationRead, Key: "failure_key1"},
				{Type: OperationRead, Key: "failure_key2"},
				{Type: OperationWrite, Key: "failure_key3", Value: "after_recovery"},
				{Type: OperationCommit},
			},
		},
		FailureScenarios: []FailureScenario{
			{
				NodeID: 0,
				FailureTime: 1 * time.Second,
				RecoveryTime: 3 * time.Second,
				FailureType: "crash",
			},
		},
		ExpectedResults: [][]interface{}{
			{nil, true},
			{nil, true}, // Should still succeed due to replication
			{"before_failure", "during_failure", nil, true},
		},
		ExpectedKeyState: map[string]string{
			"failure_key1": "before_failure",
			"failure_key2": "during_failure",
			"failure_key3": "after_recovery",
		},
	},
	{
		Description: "Network partition",
		NodeCount: 6,
		Transactions: [][]Operation{
			{
				{Type: OperationWrite, Key: "partition_key1", Value: "before_partition"},
				{Type: OperationCommit},
			},
			// During partition, writes to the majority partition should succeed
			{
				{Type: OperationWrite, Key: "partition_key2", Value: "majority_partition"},
				{Type: OperationCommit},
			},
			// After healing
			{
				{Type: OperationRead, Key: "partition_key1"},
				{Type: OperationRead, Key: "partition_key2"},
				{Type: OperationCommit},
			},
		},
		FailureScenarios: []FailureScenario{
			{
				FailureTime: 1 * time.Second,
				RecoveryTime: 3 * time.Second,
				FailureType: "network_partition",
				AffectedNodes: []int{0, 1},
				PartitionGroup: 1,
			},
		},
		ExpectedResults: [][]interface{}{
			{nil, true},
			{nil, true}, // Should succeed in majority partition
			{"before_partition", "majority_partition", true},
		},
		ExpectedKeyState: map[string]string{
			"partition_key1": "before_partition",
			"partition_key2": "majority_partition",
		},
	},
}