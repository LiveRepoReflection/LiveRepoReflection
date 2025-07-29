package dtc

import (
	"math/rand"
	"reflect"
	"sync"
	"testing"
	"time"
)

func TestBasicTransaction(t *testing.T) {
	coord := NewCoordinator(3, 0, 100, 0.0) // 3 services, range 0-100, no message loss
	
	deltas := []int{10, 20, 30}
	success := coord.InitiateTransaction(deltas)
	if !success {
		t.Error("Expected transaction to succeed")
	}

	expected := []int{10, 20, 30}
	states := coord.GetAllStates()
	if !reflect.DeepEqual(states, expected) {
		t.Errorf("Expected states %v, got %v", expected, states)
	}
}

func TestBoundaryConstraints(t *testing.T) {
	coord := NewCoordinator(2, 0, 50, 0.0)

	// Test upper bound
	deltas := []int{60, 40}
	success := coord.InitiateTransaction(deltas)
	if success {
		t.Error("Transaction should fail due to upper bound violation")
	}

	// Test lower bound
	deltas = []int{-10, -10}
	success = coord.InitiateTransaction(deltas)
	if success {
		t.Error("Transaction should fail due to lower bound violation")
	}
}

func TestConcurrentTransactions(t *testing.T) {
	coord := NewCoordinator(3, 0, 1000, 0.0)
	var wg sync.WaitGroup
	numTransactions := 100

	results := make([]bool, numTransactions)
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			deltas := []int{10, 10, 10}
			results[idx] = coord.InitiateTransaction(deltas)
		}(i)
	}

	wg.Wait()

	successCount := 0
	for _, success := range results {
		if success {
			successCount++
		}
	}

	if successCount == 0 {
		t.Error("Expected some transactions to succeed")
	}
}

func TestMessageLoss(t *testing.T) {
	rand.Seed(time.Now().UnixNano())
	coord := NewCoordinator(3, 0, 100, 0.5) // 50% message loss probability

	numAttempts := 10
	successCount := 0

	for i := 0; i < numAttempts; i++ {
		if coord.InitiateTransaction([]int{5, 5, 5}) {
			successCount++
		}
	}

	if successCount == 0 {
		t.Error("Expected some transactions to succeed despite message loss")
	}
}

func TestTransactionIsolation(t *testing.T) {
	coord := NewCoordinator(2, 0, 100, 0.0)
	
	var wg sync.WaitGroup
	wg.Add(2)

	go func() {
		defer wg.Done()
		coord.InitiateTransaction([]int{10, 20})
	}()

	go func() {
		defer wg.Done()
		coord.InitiateTransaction([]int{30, 40})
	}()

	wg.Wait()

	states := coord.GetAllStates()
	total := states[0] + states[1]
	
	if total != 100 && total != 60 && total != 30 {
		t.Errorf("Unexpected final state: %v", states)
	}
}

func TestRollback(t *testing.T) {
	coord := NewCoordinator(3, 0, 100, 0.0)
	
	// First transaction should succeed
	success := coord.InitiateTransaction([]int{10, 10, 10})
	if !success {
		t.Error("First transaction should succeed")
	}

	// Second transaction should fail and rollback
	success = coord.InitiateTransaction([]int{200, 200, 200})
	if success {
		t.Error("Second transaction should fail")
	}

	expected := []int{10, 10, 10}
	states := coord.GetAllStates()
	if !reflect.DeepEqual(states, expected) {
		t.Errorf("Expected states %v after rollback, got %v", expected, states)
	}
}

func TestTimeouts(t *testing.T) {
	coord := NewCoordinator(2, 0, 100, 0.9) // 90% message loss to force timeouts
	
	start := time.Now()
	success := coord.InitiateTransaction([]int{10, 10})
	duration := time.Since(start)

	if duration < time.Second {
		t.Error("Expected transaction to take at least 1 second due to retries")
	}

	if !success && !coord.IsConsistent() {
		t.Error("System entered inconsistent state after timeout")
	}
}

func TestSystemConsistency(t *testing.T) {
	coord := NewCoordinator(3, 0, 100, 0.3)
	
	transactions := [][]int{
		{10, 20, 30},
		{-5, -10, -15},
		{200, 200, 200}, // Should fail
		{5, 5, 5},
	}

	for _, tx := range transactions {
		coord.InitiateTransaction(tx)
	}

	if !coord.IsConsistent() {
		t.Error("System is in an inconsistent state")
	}
}
