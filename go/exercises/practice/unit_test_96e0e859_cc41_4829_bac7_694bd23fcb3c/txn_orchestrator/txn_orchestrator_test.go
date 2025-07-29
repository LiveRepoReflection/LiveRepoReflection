package txnorchestrator

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

type testNode struct {
	mu                sync.Mutex
	preparedTxns     map[int]string
	committedTxns    map[int]string
	shouldFailPrepare bool
	prepareDelay     time.Duration
	commitDelay      time.Duration
	prepareCalls     int
	commitCalls      int
}

func newTestNode() *testNode {
	return &testNode{
		preparedTxns:  make(map[int]string),
		committedTxns: make(map[int]string),
	}
}

func (n *testNode) prepare(txnID int, data string) bool {
	n.mu.Lock()
	defer n.mu.Unlock()

	if n.prepareDelay > 0 {
		time.Sleep(n.prepareDelay)
	}

	n.prepareCalls++

	if n.shouldFailPrepare {
		return false
	}

	// If already prepared with same data, return true (idempotency)
	if existingData, exists := n.preparedTxns[txnID]; exists {
		return existingData == data
	}

	n.preparedTxns[txnID] = data
	return true
}

func (n *testNode) commit(txnID int) {
	n.mu.Lock()
	defer n.mu.Unlock()

	if n.commitDelay > 0 {
		time.Sleep(n.commitDelay)
	}

	n.commitCalls++

	// Only commit if transaction was prepared
	if data, exists := n.preparedTxns[txnID]; exists {
		n.committedTxns[txnID] = data
	}
}

func TestSuccessfulTransaction(t *testing.T) {
	nodes := make([]*testNode, 3)
	for i := range nodes {
		nodes[i] = newTestNode()
	}

	prepareFuncs := make([]func(int, string) bool, len(nodes))
	commitFuncs := make([]func(int), len(nodes))

	for i := range nodes {
		node := nodes[i]
		prepareFuncs[i] = node.prepare
		commitFuncs[i] = node.commit
	}

	success := OrchestrateTransaction(
		len(nodes),
		prepareFuncs,
		commitFuncs,
		1,
		"test_data",
	)

	if !success {
		t.Error("Expected transaction to succeed")
	}

	// Verify all nodes committed
	for i, node := range nodes {
		if data, exists := node.committedTxns[1]; !exists || data != "test_data" {
			t.Errorf("Node %d did not commit correctly", i)
		}
	}
}

func TestFailedPreparation(t *testing.T) {
	nodes := make([]*testNode, 3)
	for i := range nodes {
		nodes[i] = newTestNode()
	}

	// Make middle node fail
	nodes[1].shouldFailPrepare = true

	prepareFuncs := make([]func(int, string) bool, len(nodes))
	commitFuncs := make([]func(int), len(nodes))

	for i := range nodes {
		node := nodes[i]
		prepareFuncs[i] = node.prepare
		commitFuncs[i] = node.commit
	}

	success := OrchestrateTransaction(
		len(nodes),
		prepareFuncs,
		commitFuncs,
		1,
		"test_data",
	)

	if success {
		t.Error("Expected transaction to fail")
	}

	// Verify no nodes committed
	for i, node := range nodes {
		if len(node.committedTxns) > 0 {
			t.Errorf("Node %d should not have committed any transactions", i)
		}
	}
}

func TestConcurrentTransactions(t *testing.T) {
	const numNodes = 5
	const numTransactions = 10

	nodes := make([]*testNode, numNodes)
	for i := range nodes {
		nodes[i] = newTestNode()
	}

	prepareFuncs := make([]func(int, string) bool, len(nodes))
	commitFuncs := make([]func(int), len(nodes))

	for i := range nodes {
		node := nodes[i]
		prepareFuncs[i] = node.prepare
		commitFuncs[i] = node.commit
	}

	var wg sync.WaitGroup
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		txnID := i
		go func() {
			defer wg.Done()
			data := fmt.Sprintf("data_%d", txnID)
			success := OrchestrateTransaction(
				len(nodes),
				prepareFuncs,
				commitFuncs,
				txnID,
				data,
			)
			if !success {
				t.Errorf("Transaction %d failed unexpectedly", txnID)
			}
		}()
	}

	wg.Wait()

	// Verify all transactions were committed on all nodes
	for nodeID, node := range nodes {
		if len(node.committedTxns) != numTransactions {
			t.Errorf("Node %d: Expected %d committed transactions, got %d",
				nodeID, numTransactions, len(node.committedTxns))
		}
	}
}

func TestIdempotency(t *testing.T) {
	nodes := make([]*testNode, 3)
	for i := range nodes {
		nodes[i] = newTestNode()
	}

	prepareFuncs := make([]func(int, string) bool, len(nodes))
	commitFuncs := make([]func(int), len(nodes))

	for i := range nodes {
		node := nodes[i]
		prepareFuncs[i] = node.prepare
		commitFuncs[i] = node.commit
	}

	// Call orchestrate multiple times with same transaction ID and data
	for i := 0; i < 3; i++ {
		success := OrchestrateTransaction(
			len(nodes),
			prepareFuncs,
			commitFuncs,
			1,
			"test_data",
		)
		if !success {
			t.Errorf("Expected transaction attempt %d to succeed", i)
		}
	}

	// Verify each node only recorded one commit
	for i, node := range nodes {
		if len(node.committedTxns) != 1 {
			t.Errorf("Node %d: Expected exactly one committed transaction, got %d",
				i, len(node.committedTxns))
		}
	}
}

func TestDelayedNodes(t *testing.T) {
	nodes := make([]*testNode, 3)
	for i := range nodes {
		nodes[i] = newTestNode()
	}

	// Add delay to middle node
	nodes[1].prepareDelay = 100 * time.Millisecond

	prepareFuncs := make([]func(int, string) bool, len(nodes))
	commitFuncs := make([]func(int), len(nodes))

	for i := range nodes {
		node := nodes[i]
		prepareFuncs[i] = node.prepare
		commitFuncs[i] = node.commit
	}

	start := time.Now()
	success := OrchestrateTransaction(
		len(nodes),
		prepareFuncs,
		commitFuncs,
		1,
		"test_data",
	)
	duration := time.Since(start)

	if !success {
		t.Error("Expected transaction to succeed")
	}

	// Verify that the total duration is less than sequential execution would take
	if duration >= 300*time.Millisecond {
		t.Error("Transaction took too long, prepare operations might not be concurrent")
	}
}
