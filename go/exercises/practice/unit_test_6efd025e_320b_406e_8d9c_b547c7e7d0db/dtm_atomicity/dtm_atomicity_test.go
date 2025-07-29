package dtm_atomicity

import (
	"errors"
	"sync"
	"testing"
	"time"
)

// Dummy implementations for testing purposes.
// We assume that the DistributedTransactionManager exposes the following API:
//   NewDistributedTransactionManager() *DistributedTransactionManager
//   (dtm *DistributedTransactionManager) BeginTransaction() string
//   (dtm *DistributedTransactionManager) Register(txID string, prepare func(string) error, commit func(string) error, rollback func(string) error)
//   (dtm *DistributedTransactionManager) EndTransaction(txID string) error
//
// For the purpose of these tests, it is assumed that the DTM implementation
// correctly routes the operations you register.

type operationCounters struct {
	prepareCount  int
	commitCount   int
	rollbackCount int
	mu            sync.Mutex
}

func (oc *operationCounters) incPrepare() {
	oc.mu.Lock()
	defer oc.mu.Unlock()
	oc.prepareCount++
}

func (oc *operationCounters) incCommit() {
	oc.mu.Lock()
	defer oc.mu.Unlock()
	oc.commitCount++
}

func (oc *operationCounters) incRollback() {
	oc.mu.Lock()
	defer oc.mu.Unlock()
	oc.rollbackCount++
}

func newCounters() *operationCounters {
	return &operationCounters{}
}

// Dummy service functions for a successful commit.
func successfulPrepare(oc *operationCounters) func(string) error {
	return func(txID string) error {
		oc.incPrepare()
		return nil
	}
}

func successfulCommit(oc *operationCounters) func(string) error {
	return func(txID string) error {
		oc.incCommit()
		return nil
	}
}

func successfulRollback(oc *operationCounters) func(string) error {
	return func(txID string) error {
		oc.incRollback()
		return nil
	}
}

// Dummy service function that fails during the prepare phase.
func failingPrepare(oc *operationCounters) func(string) error {
	return func(txID string) error {
		oc.incPrepare()
		return errors.New("prepare failed")
	}
}

// Dummy service function that simulates a long running prepare operation for testing timeouts.
func slowPrepare(oc *operationCounters, sleepDuration time.Duration) func(string) error {
	return func(txID string) error {
		oc.incPrepare()
		time.Sleep(sleepDuration)
		return nil
	}
}

// TestTransactionCommit tests that when all operations succeed, the commit functions are invoked.
func TestTransactionCommit(t *testing.T) {
	dtm := NewDistributedTransactionManager()
	txID := dtm.BeginTransaction()
	
	counters := newCounters()
	
	// Register two successful services.
	dtm.Register(txID, successfulPrepare(counters), successfulCommit(counters), successfulRollback(counters))
	dtm.Register(txID, successfulPrepare(counters), successfulCommit(counters), successfulRollback(counters))
	
	err := dtm.EndTransaction(txID)
	if err != nil {
		t.Fatalf("Expected transaction commit to succeed, got error: %v", err)
	}
	
	// Expect two prepares and two commits, and no rollbacks.
	if counters.prepareCount != 2 {
		t.Errorf("Expected 2 prepare calls, got %d", counters.prepareCount)
	}
	if counters.commitCount != 2 {
		t.Errorf("Expected 2 commit calls, got %d", counters.commitCount)
	}
	if counters.rollbackCount != 0 {
		t.Errorf("Expected 0 rollback calls, got %d", counters.rollbackCount)
	}
}

// TestTransactionRollback tests that when one service fails during prepare,
// the transaction is rolled back for all registered services.
func TestTransactionRollback(t *testing.T) {
	dtm := NewDistributedTransactionManager()
	txID := dtm.BeginTransaction()

	counters1 := newCounters()
	counters2 := newCounters()
	
	// First service succeeds
	dtm.Register(txID, successfulPrepare(counters1), successfulCommit(counters1), successfulRollback(counters1))
	// Second service fails during prepare
	dtm.Register(txID, failingPrepare(counters2), successfulCommit(counters2), successfulRollback(counters2))
	
	err := dtm.EndTransaction(txID)
	if err == nil {
		t.Fatal("Expected transaction to fail and rollback, but got nil error")
	}
	
	// Even if one fails, both services should have attempted rollback.
	if counters1.rollbackCount != 1 {
		t.Errorf("Expected rollback to be called once for service1, got %d", counters1.rollbackCount)
	}
	if counters2.rollbackCount != 1 {
		t.Errorf("Expected rollback to be called once for service2, got %d", counters2.rollbackCount)
	}
	// Commit should not be called on any service.
	if counters1.commitCount != 0 {
		t.Errorf("Expected commit to not be called for service1, got %d", counters1.commitCount)
	}
	if counters2.commitCount != 0 {
		t.Errorf("Expected commit to not be called for service2, got %d", counters2.commitCount)
	}
}

// TestTransactionTimeout tests that when a prepare function exceeds the allowed timeout,
// the transaction is aborted and rollback is executed.
func TestTransactionTimeout(t *testing.T) {
	// For testing timeouts, we assume that the DTM is configured to have a prepare timeout,
	// for example 50 milliseconds. Adjust the sleep duration accordingly.
	dtm := NewDistributedTransactionManager()
	txID := dtm.BeginTransaction()
	
	counters := newCounters()
	
	// One service will sleep longer than the allowed timeout.
	// Assuming timeout is 50ms, here we sleep for 100ms.
	dtm.Register(txID, slowPrepare(counters, 100*time.Millisecond), successfulCommit(counters), successfulRollback(counters))
	// Another service is quick.
	dtm.Register(txID, successfulPrepare(counters), successfulCommit(counters), successfulRollback(counters))
	
	start := time.Now()
	err := dtm.EndTransaction(txID)
	elapsed := time.Since(start)
	if err == nil {
		t.Fatal("Expected transaction to timeout and rollback, but got nil error")
	}
	// Check if rollback was called for both services.
	if counters.rollbackCount != 2 {
		t.Errorf("Expected rollback to be called for both services, got %d", counters.rollbackCount)
	}
	
	// Ensure that the transaction did not wait indefinitely.
	if elapsed > 500*time.Millisecond {
		t.Errorf("Transaction timeout took too long: %v", elapsed)
	}
}

// TestConcurrentTransactions tests that multiple transactions run concurrently without interfering.
func TestConcurrentTransactions(t *testing.T) {
	dtm := NewDistributedTransactionManager()
	const numTransactions = 50
	
	var wg sync.WaitGroup
	errCh := make(chan error, numTransactions)
	
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			txID := dtm.BeginTransaction()
			counters := newCounters()
			// Register two services; both will commit successfully.
			dtm.Register(txID, successfulPrepare(counters), successfulCommit(counters), successfulRollback(counters))
			dtm.Register(txID, successfulPrepare(counters), successfulCommit(counters), successfulRollback(counters))
			
			err := dtm.EndTransaction(txID)
			if err != nil {
				errCh <- err
			}
			// Optionally, one can add further checks here if the DTM provides results back from operations.
		}()
	}
	wg.Wait()
	close(errCh)
	
	for err := range errCh {
		if err != nil {
			t.Errorf("Concurrent transaction failed with error: %v", err)
		}
	}
}