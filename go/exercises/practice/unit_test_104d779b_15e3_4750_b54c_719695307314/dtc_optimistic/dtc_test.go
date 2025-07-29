package dtc

import (
	"sync"
	"testing"
	"time"
)

func TestBeginTransaction(t *testing.T) {
	dtc := NewDTC()
	txID := dtc.BeginTransaction()
	if txID == 0 {
		t.Error("Expected non-zero transaction ID")
	}
}

func TestPrepareTransaction(t *testing.T) {
	dtc := NewDTC()
	txID := dtc.BeginTransaction()
	err := dtc.PrepareTransaction(txID, 1, 0)
	if err != nil {
		t.Errorf("PrepareTransaction failed: %v", err)
	}
}

func TestCommitTransactionSuccess(t *testing.T) {
	dtc := NewDTC()
	txID := dtc.BeginTransaction()
	dtc.PrepareTransaction(txID, 1, 0)
	success := dtc.CommitTransaction(txID)
	if !success {
		t.Error("Expected successful commit")
	}
	state, err := dtc.GetTransactionState(txID)
	if err != nil || state != Committed {
		t.Error("Transaction should be committed")
	}
}

func TestCommitTransactionConflict(t *testing.T) {
	dtc := NewDTC()
	tx1 := dtc.BeginTransaction()
	dtc.PrepareTransaction(tx1, 1, 0)
	
	tx2 := dtc.BeginTransaction()
	dtc.PrepareTransaction(tx2, 1, 0)
	
	// First commit should succeed
	if !dtc.CommitTransaction(tx1) {
		t.Error("First commit should succeed")
	}
	
	// Second commit should fail due to version conflict
	if dtc.CommitTransaction(tx2) {
		t.Error("Second commit should fail due to version conflict")
	}
}

func TestConcurrentCommits(t *testing.T) {
	dtc := NewDTC()
	var wg sync.WaitGroup
	successCount := 0
	const numTransactions = 100

	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			txID := dtc.BeginTransaction()
			dtc.PrepareTransaction(txID, 1, 0)
			if dtc.CommitTransaction(txID) {
				successCount++
			}
		}()
	}

	wg.Wait()
	if successCount != 1 {
		t.Errorf("Expected exactly 1 successful commit, got %d", successCount)
	}
}

func TestInvalidTransactionID(t *testing.T) {
	dtc := NewDTC()
	
	// Test invalid transaction ID for Prepare
	err := dtc.PrepareTransaction(999, 1, 0)
	if err == nil {
		t.Error("Expected error for invalid transaction ID")
	}

	// Test invalid transaction ID for Commit
	if dtc.CommitTransaction(999) {
		t.Error("Expected false for invalid transaction ID commit")
	}

	// Test invalid transaction ID for GetState
	_, err = dtc.GetTransactionState(999)
	if err == nil {
		t.Error("Expected error for invalid transaction ID state check")
	}
}

func TestDuplicateServiceInTransaction(t *testing.T) {
	dtc := NewDTC()
	txID := dtc.BeginTransaction()
	dtc.PrepareTransaction(txID, 1, 0)
	err := dtc.PrepareTransaction(txID, 1, 0)
	if err == nil {
		t.Error("Expected error for duplicate service in transaction")
	}
}

func TestTransactionStateTransitions(t *testing.T) {
	dtc := NewDTC()
	txID := dtc.BeginTransaction()
	
	// Initial state should be Pending
	state, err := dtc.GetTransactionState(txID)
	if err != nil || state != Pending {
		t.Error("Initial state should be Pending")
	}

	// After commit, state should be Committed or Aborted
	dtc.PrepareTransaction(txID, 1, 0)
	dtc.CommitTransaction(txID)
	state, err = dtc.GetTransactionState(txID)
	if err != nil || (state != Committed && state != Aborted) {
		t.Error("Post-commit state should be Committed or Aborted")
	}
}

func TestServiceVersionIncrement(t *testing.T) {
	dtc := NewDTC()
	txID := dtc.BeginTransaction()
	dtc.PrepareTransaction(txID, 1, 0)
	dtc.CommitTransaction(txID)

	// Service version should increment after successful commit
	txID2 := dtc.BeginTransaction()
	err := dtc.PrepareTransaction(txID2, 1, 1)
	if err != nil {
		t.Errorf("Expected to prepare with new version, got error: %v", err)
	}
}

func TestTimeoutHandling(t *testing.T) {
	dtc := NewDTCWithTimeout(100 * time.Millisecond)
	txID := dtc.BeginTransaction()
	dtc.PrepareTransaction(txID, 1, 0)

	// Wait for timeout
	time.Sleep(200 * time.Millisecond)

	// Transaction should be aborted after timeout
	state, err := dtc.GetTransactionState(txID)
	if err != nil || state != Aborted {
		t.Error("Transaction should be aborted after timeout")
	}
}