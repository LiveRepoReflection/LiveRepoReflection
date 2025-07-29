package transaction_coordinator

import (
	"errors"
	"sync"
	"testing"
	"time"
)

// mockService is used to simulate the behavior of a Service in tests.
type mockService struct {
	name           string
	prepareErr     error
	commitErrs     []error
	rollbackErr    error
	commitCallCount int

	mux        sync.Mutex
	prepared   bool
	committed  bool
	rolledBack bool
}

func (ms *mockService) Prepare(transactionID string) error {
	ms.mux.Lock()
	defer ms.mux.Unlock()
	ms.prepared = true
	return ms.prepareErr
}

func (ms *mockService) Commit(transactionID string) error {
	ms.mux.Lock()
	defer ms.mux.Unlock()
	var err error
	if ms.commitCallCount < len(ms.commitErrs) {
		err = ms.commitErrs[ms.commitCallCount]
		ms.commitCallCount++
	} else {
		err = nil
		ms.commitCallCount++
	}
	if err == nil {
		ms.committed = true
	}
	return err
}

func (ms *mockService) Rollback(transactionID string) error {
	ms.mux.Lock()
	defer ms.mux.Unlock()
	if ms.rollbackErr == nil {
		ms.rolledBack = true
		return nil
	}
	ms.rolledBack = true
	return ms.rollbackErr
}

// TestTransactionCommitSuccess tests a transaction that should commit successfully.
func TestTransactionCommitSuccess(t *testing.T) {
	// Create two services that always succeed.
	svc1 := &mockService{name: "svc1"}
	svc2 := &mockService{name: "svc2"}
	services := []Service{svc1, svc2}

	// Create a coordinator with reasonable timeouts and commitRetries.
	tc := NewTransactionCoordinator(100*time.Millisecond, 100*time.Millisecond, 100*time.Millisecond, 3)
	txID, err := tc.BeginTransaction(services)
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = tc.EndTransaction(txID)
	if err != nil {
		t.Fatalf("EndTransaction failed: %v", err)
	}
	// Verify that both services were prepared and committed.
	if !svc1.prepared || !svc2.prepared {
		t.Error("Not all services were prepared")
	}
	if !svc1.committed || !svc2.committed {
		t.Error("Not all services committed")
	}
}

// TestTransactionPrepareFailure tests a transaction where one service fails in the prepare phase.
func TestTransactionPrepareFailure(t *testing.T) {
	// svc2 fails during Prepare.
	svc1 := &mockService{name: "svc1"}
	svc2 := &mockService{name: "svc2", prepareErr: errors.New("prepare failure")}
	services := []Service{svc1, svc2}

	tc := NewTransactionCoordinator(100*time.Millisecond, 100*time.Millisecond, 100*time.Millisecond, 3)
	txID, err := tc.BeginTransaction(services)
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = tc.EndTransaction(txID)
	if err == nil {
		t.Error("Expected EndTransaction to fail due to prepare error")
	}
	// In prepare failure, rollback should be called.
	if !svc1.rolledBack {
		t.Error("svc1 was not rolled back on prepare failure")
	}
	if !svc2.rolledBack {
		t.Error("svc2 was not rolled back on prepare failure")
	}
}

// TestTransactionCommitWithRetries tests a transaction which experiences transient commit failures
// that are eventually resolved using the commit retry mechanism.
func TestTransactionCommitWithRetries(t *testing.T) {
	// svc1 will fail commit twice, then succeed.
	svc1 := &mockService{
		name:       "svc1",
		commitErrs: []error{errors.New("commit error 1"), errors.New("commit error 2"), nil},
	}
	svc2 := &mockService{name: "svc2"}
	services := []Service{svc1, svc2}

	// Set commitRetries to 3 so that svc1 eventually succeeds.
	tc := NewTransactionCoordinator(100*time.Millisecond, 100*time.Millisecond, 100*time.Millisecond, 3)
	txID, err := tc.BeginTransaction(services)
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = tc.EndTransaction(txID)
	if err != nil {
		t.Fatalf("EndTransaction failed despite commit retries: %v", err)
	}

	// Verify that commit was attempted the required number of times.
	if svc1.commitCallCount != 3 {
		t.Errorf("Expected 3 commit attempts for svc1, got %d", svc1.commitCallCount)
	}
	if !svc1.committed || !svc2.committed {
		t.Error("Not all services committed successfully after retries")
	}
}

// TestTransactionCommitFailureThenRollback tests a transaction where commit fails even after retries,
// and the coordinator proceeds to rollback.
func TestTransactionCommitFailureThenRollback(t *testing.T) {
	// svc1 will fail commit always.
	svc1 := &mockService{
		name:       "svc1",
		commitErrs: []error{errors.New("commit error"), errors.New("commit error"), errors.New("commit error")},
	}
	// svc2 succeeds commit normally.
	svc2 := &mockService{name: "svc2"}
	services := []Service{svc1, svc2}

	tc := NewTransactionCoordinator(100*time.Millisecond, 100*time.Millisecond, 100*time.Millisecond, 3)
	txID, err := tc.BeginTransaction(services)
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = tc.EndTransaction(txID)
	if err == nil {
		t.Error("Expected EndTransaction to fail due to persistent commit errors")
	}

	// Both services should have been rolled back.
	if !svc1.rolledBack {
		t.Error("svc1 was not rolled back after commit failure")
	}
	if !svc2.rolledBack {
		t.Error("svc2 was not rolled back after commit failure")
	}
}

// TestTransactionRollbackFailure tests a scenario where rollback fails on one of the services.
func TestTransactionRollbackFailure(t *testing.T) {
	// svc1 fails during commit causing rollback phase.
	svc1 := &mockService{
		name:       "svc1",
		commitErrs: []error{errors.New("commit error"), errors.New("commit error")},
		rollbackErr: errors.New("rollback failure"),
	}
	svc2 := &mockService{name: "svc2"}
	services := []Service{svc1, svc2}

	tc := NewTransactionCoordinator(100*time.Millisecond, 100*time.Millisecond, 100*time.Millisecond, 2)
	txID, err := tc.BeginTransaction(services)
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = tc.EndTransaction(txID)
	if err == nil {
		t.Error("Expected EndTransaction to fail due to rollback failure")
	}

	// Check that rollback was attempted on both and svc1 experienced a rollback error.
	if !svc1.rolledBack {
		t.Error("svc1 rollback was not attempted")
	}
	if !svc2.rolledBack {
		t.Error("svc2 rollback was not attempted")
	}
}

// TestConcurrentTransactions tests that the coordinator can handle multiple concurrent transactions.
func TestConcurrentTransactions(t *testing.T) {
	tc := NewTransactionCoordinator(100*time.Millisecond, 100*time.Millisecond, 100*time.Millisecond, 3)
	numTransactions := 10
	var wg sync.WaitGroup
	errCh := make(chan error, numTransactions)
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func(txNum int) {
			defer wg.Done()
			// Each transaction uses two services that succeed.
			svc1 := &mockService{name: "svc1"}
			svc2 := &mockService{name: "svc2"}
			services := []Service{svc1, svc2}
			txID, err := tc.BeginTransaction(services)
			if err != nil {
				errCh <- err
				return
			}
			err = tc.EndTransaction(txID)
			if err != nil {
				errCh <- err
			}
		}(i)
	}
	wg.Wait()
	close(errCh)
	for err := range errCh {
		t.Errorf("Concurrent transaction error: %v", err)
	}
}