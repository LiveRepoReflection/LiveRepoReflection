package dtm

import (
	"errors"
	"sync"
	"testing"
	"time"
)

// The TransactionManager is assumed to have the following interface:
//   NewTransactionManager(timeout time.Duration) *TransactionManager
//   (tm *TransactionManager) RegisterParticipant(txID string, prepare func() (string, error), commit func(string) error, rollback func() error) error
//   (tm *TransactionManager) CommitTransaction(txID string) error
//   (tm *TransactionManager) RollbackTransaction(txID string) error
//
// This unit test suite verifies various scenarios including successful commits,
// prepare failures, timeouts, explicit rollbacks, and concurrent transactions.

func TestCommitSuccess(t *testing.T) {
	tm := NewTransactionManager(5 * time.Second)
	txID := "tx_success"

	var commitCalls1, commitCalls2 int
	var rollbackCalls1, rollbackCalls2 int
	var mu sync.Mutex

	// Participant 1: Successful prepare, commit and rollback.
	err := tm.RegisterParticipant(txID,
		func() (string, error) {
			return "data1", nil
		},
		func(data string) error {
			mu.Lock()
			commitCalls1++
			mu.Unlock()
			return nil
		},
		func() error {
			mu.Lock()
			rollbackCalls1++
			mu.Unlock()
			return nil
		},
	)
	if err != nil {
		t.Fatalf("RegisterParticipant failed: %v", err)
	}

	// Participant 2: Successful prepare, commit and rollback.
	err = tm.RegisterParticipant(txID,
		func() (string, error) {
			return "data2", nil
		},
		func(data string) error {
			mu.Lock()
			commitCalls2++
			mu.Unlock()
			return nil
		},
		func() error {
			mu.Lock()
			rollbackCalls2++
			mu.Unlock()
			return nil
		},
	)
	if err != nil {
		t.Fatalf("RegisterParticipant failed: %v", err)
	}

	err = tm.CommitTransaction(txID)
	if err != nil {
		t.Fatalf("CommitTransaction failed: %v", err)
	}

	// Allow asynchronous operations to complete.
	time.Sleep(100 * time.Millisecond)

	mu.Lock()
	defer mu.Unlock()
	if commitCalls1 != 1 || commitCalls2 != 1 {
		t.Errorf("Expected one commit call per participant, got %d and %d", commitCalls1, commitCalls2)
	}
	if rollbackCalls1 != 0 || rollbackCalls2 != 0 {
		t.Errorf("Expected no rollback calls, got %d and %d", rollbackCalls1, rollbackCalls2)
	}
}

func TestPrepareFailure(t *testing.T) {
	tm := NewTransactionManager(5 * time.Second)
	txID := "tx_prepare_fail"

	var commitCalls int
	var rollbackCalls int
	var mu sync.Mutex

	// Participant 1 succeeds in prepare.
	err := tm.RegisterParticipant(txID,
		func() (string, error) {
			return "ok", nil
		},
		func(data string) error {
			mu.Lock()
			commitCalls++
			mu.Unlock()
			return nil
		},
		func() error {
			mu.Lock()
			rollbackCalls++
			mu.Unlock()
			return nil
		},
	)
	if err != nil {
		t.Fatalf("RegisterParticipant failed: %v", err)
	}

	// Participant 2 fails in prepare.
	err = tm.RegisterParticipant(txID,
		func() (string, error) {
			return "", errors.New("prepare failed")
		},
		func(data string) error {
			mu.Lock()
			commitCalls++
			mu.Unlock()
			return nil
		},
		func() error {
			mu.Lock()
			rollbackCalls++
			mu.Unlock()
			return nil
		},
	)
	if err != nil {
		t.Fatalf("RegisterParticipant failed: %v", err)
	}

	err = tm.CommitTransaction(txID)
	if err == nil {
		t.Fatalf("CommitTransaction should fail due to prepare failure")
	}

	// Allow asynchronous rollback to complete.
	time.Sleep(100 * time.Millisecond)

	mu.Lock()
	defer mu.Unlock()
	if commitCalls != 0 {
		t.Errorf("No commit should be executed when prepare fails, got %d", commitCalls)
	}
	if rollbackCalls != 2 {
		t.Errorf("Expected rollback to be executed twice, got %d", rollbackCalls)
	}
}

func TestTimeoutRollback(t *testing.T) {
	// Using a short timeout for testing.
	tm := NewTransactionManager(1 * time.Second)
	txID := "tx_timeout"

	var commitCalled bool
	var rollbackCalled bool
	var mu sync.Mutex

	// Participant with a long prepare causing a timeout.
	err := tm.RegisterParticipant(txID,
		func() (string, error) {
			time.Sleep(2 * time.Second)
			return "late", nil
		},
		func(data string) error {
			mu.Lock()
			commitCalled = true
			mu.Unlock()
			return nil
		},
		func() error {
			mu.Lock()
			rollbackCalled = true
			mu.Unlock()
			return nil
		},
	)
	if err != nil {
		t.Fatalf("RegisterParticipant failed: %v", err)
	}

	err = tm.CommitTransaction(txID)
	if err == nil {
		t.Fatalf("CommitTransaction should fail due to prepare timeout")
	}

	// Wait for the asynchronous rollback.
	time.Sleep(1500 * time.Millisecond)

	mu.Lock()
	defer mu.Unlock()
	if commitCalled {
		t.Errorf("Commit should not be invoked when prepare times out")
	}
	if !rollbackCalled {
		t.Errorf("Rollback should be invoked when prepare times out")
	}
}

func TestExplicitRollback(t *testing.T) {
	tm := NewTransactionManager(5 * time.Second)
	txID := "tx_explicit_rollback"

	var commitCalled bool
	var rollbackCount int
	var mu sync.Mutex

	err := tm.RegisterParticipant(txID,
		func() (string, error) {
			return "p1", nil
		},
		func(data string) error {
			mu.Lock()
			commitCalled = true
			mu.Unlock()
			return nil
		},
		func() error {
			mu.Lock()
			rollbackCount++
			mu.Unlock()
			return nil
		},
	)
	if err != nil {
		t.Fatalf("RegisterParticipant failed: %v", err)
	}

	err = tm.RollbackTransaction(txID)
	if err != nil {
		t.Fatalf("RollbackTransaction failed: %v", err)
	}

	// Allow asynchronous rollback to complete.
	time.Sleep(100 * time.Millisecond)

	mu.Lock()
	defer mu.Unlock()
	if commitCalled {
		t.Errorf("Commit should not execute when transaction is explicitly rolled back")
	}
	if rollbackCount != 1 {
		t.Errorf("Expected exactly one rollback call, got %d", rollbackCount)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	tm := NewTransactionManager(5 * time.Second)
	var wg sync.WaitGroup

	nTransactions := 10
	for i := 0; i < nTransactions; i++ {
		wg.Add(1)
		go func(txNum int) {
			defer wg.Done()
			txID := "tx_concurrent_" + string(rune('A'+txNum))
			var commitCount int
			var rollbackCount int
			var mu sync.Mutex

			// First participant always succeeds.
			err := tm.RegisterParticipant(txID,
				func() (string, error) {
					return "data", nil
				},
				func(data string) error {
					mu.Lock()
					commitCount++
					mu.Unlock()
					return nil
				},
				func() error {
					mu.Lock()
					rollbackCount++
					mu.Unlock()
					return nil
				},
			)
			if err != nil {
				t.Errorf("[%s] RegisterParticipant failed: %v", txID, err)
				return
			}

			// Second participant conditionally fails in prepare for odd transactions.
			prepareFunc := func() (string, error) {
				if txNum%2 == 1 {
					return "", errors.New("intentional failure")
				}
				return "data2", nil
			}
			err = tm.RegisterParticipant(txID,
				prepareFunc,
				func(data string) error {
					mu.Lock()
					commitCount++
					mu.Unlock()
					return nil
				},
				func() error {
					mu.Lock()
					rollbackCount++
					mu.Unlock()
					return nil
				},
			)
			if err != nil {
				t.Errorf("[%s] RegisterParticipant failed: %v", txID, err)
				return
			}

			var errTx error
			if txNum%2 == 1 {
				// Expect prepare failure and rollback.
				errTx = tm.CommitTransaction(txID)
				if errTx == nil {
					t.Errorf("[%s] Expected commit failure due to prepare error", txID)
				}
			} else {
				errTx = tm.CommitTransaction(txID)
				if errTx != nil {
					t.Errorf("[%s] Unexpected commit failure: %v", txID, errTx)
				}
			}

			// Allow asynchronous operations to finalize.
			time.Sleep(100 * time.Millisecond)

			mu.Lock()
			defer mu.Unlock()
			if txNum%2 == 1 {
				if commitCount != 0 {
					t.Errorf("[%s] Expected no commit calls on failure, got %d", txID, commitCount)
				}
				if rollbackCount < 2 {
					t.Errorf("[%s] Expected rollback calls for both participants on failure, got %d", txID, rollbackCount)
				}
			} else {
				if commitCount != 2 {
					t.Errorf("[%s] Expected commits for both participants, got %d", txID, commitCount)
				}
				if rollbackCount != 0 {
					t.Errorf("[%s] Expected no rollback calls, got %d", txID, rollbackCount)
				}
			}
		}(i)
	}
	wg.Wait()
}