package txn_manager_test

import (
	"errors"
	"strconv"
	"sync"
	"testing"
	"time"

	"txn_manager"
)

func createMockParticipant(id string, prepareErr, commitErr, rollbackErr error, delay time.Duration, callCounts *sync.Map) txn_manager.Participant {
	return txn_manager.Participant{
		ID: id,
		Prepare: func() error {
			key := id + "_prepare"
			if count, ok := callCounts.Load(key); ok {
				callCounts.Store(key, count.(int)+1)
			} else {
				callCounts.Store(key, 1)
			}
			time.Sleep(delay)
			return prepareErr
		},
		Commit: func() error {
			key := id + "_commit"
			if count, ok := callCounts.Load(key); ok {
				callCounts.Store(key, count.(int)+1)
			} else {
				callCounts.Store(key, 1)
			}
			return commitErr
		},
		Rollback: func() error {
			key := id + "_rollback"
			if count, ok := callCounts.Load(key); ok {
				callCounts.Store(key, count.(int)+1)
			} else {
				callCounts.Store(key, 1)
			}
			return rollbackErr
		},
	}
}

func TestSuccessfulCommit(t *testing.T) {
	dtm := txn_manager.NewDTM()
	callCounts := &sync.Map{}
	participants := []txn_manager.Participant{
		createMockParticipant("p1", nil, nil, nil, 10*time.Millisecond, callCounts),
		createMockParticipant("p2", nil, nil, nil, 15*time.Millisecond, callCounts),
		createMockParticipant("p3", nil, nil, nil, 5*time.Millisecond, callCounts),
	}
	txid := "tx_success_1"
	err := dtm.ProcessTransaction(txid, participants)
	if err != nil {
		t.Fatalf("Expected transaction to commit successfully, got error: %v", err)
	}
	state := dtm.GetTransactionState(txid)
	if state != txn_manager.Committed {
		t.Fatalf("Expected state %v, got %v", txn_manager.Committed, state)
	}

	// Check idempotency: ensure each operation is called only once
	callCounts.Range(func(key, value interface{}) bool {
		if count, ok := value.(int); ok && count > 1 {
			t.Errorf("Operation %s called multiple times: %v", key, count)
		}
		return true
	})
}

func TestPrepareFailureTriggersRollback(t *testing.T) {
	dtm := txn_manager.NewDTM()
	callCounts := &sync.Map{}
	participants := []txn_manager.Participant{
		createMockParticipant("p1", nil, nil, nil, 10*time.Millisecond, callCounts),
		createMockParticipant("p2", errors.New("prepare failure"), nil, nil, 10*time.Millisecond, callCounts),
		createMockParticipant("p3", nil, nil, nil, 5*time.Millisecond, callCounts),
	}
	txid := "tx_fail_prepare"
	err := dtm.ProcessTransaction(txid, participants)
	if err == nil {
		t.Fatalf("Expected transaction to fail due to prepare error")
	}
	state := dtm.GetTransactionState(txid)
	if state != txn_manager.RolledBack {
		t.Fatalf("Expected state %v, got %v", txn_manager.RolledBack, state)
	}

	// Ensure rollback was called for participants that prepared successfully.
	expectedRollbacks := []string{"p1_rollback", "p3_rollback"}
	for _, key := range expectedRollbacks {
		val, ok := callCounts.Load(key)
		if !ok || val.(int) != 1 {
			t.Errorf("Expected rollback for %s to be called once, got: %v", key, val)
		}
	}
}

func TestDuplicateCallsAreIdempotent(t *testing.T) {
	dtm := txn_manager.NewDTM()
	callCounts := &sync.Map{}
	participant := createMockParticipant("p_idempotent", nil, nil, nil, 0, callCounts)
	participants := []txn_manager.Participant{participant}

	txid := "tx_idempotent"
	// Process the same transaction twice to simulate duplicate invocations.
	err1 := dtm.ProcessTransaction(txid, participants)
	err2 := dtm.ProcessTransaction(txid, participants)
	if err1 != nil || err2 != nil {
		t.Fatalf("Expected idempotent transaction processing to succeed, got errors: %v and %v", err1, err2)
	}
	state := dtm.GetTransactionState(txid)
	if state != txn_manager.Committed {
		t.Fatalf("Expected state %v, got %v", txn_manager.Committed, state)
	}
	// Check that each method was executed only once.
	keys := []string{"p_idempotent_prepare", "p_idempotent_commit"}
	for _, key := range keys {
		val, ok := callCounts.Load(key)
		if !ok || val.(int) != 1 {
			t.Errorf("Expected %s to be called once, got: %v", key, val)
		}
	}
}

func TestTimeoutHandling(t *testing.T) {
	dtm := txn_manager.NewDTM()
	callCounts := &sync.Map{}
	// Participant that simulates a long delay in prepare.
	participantTimeout := createMockParticipant("p_timeout", nil, nil, nil, 2*time.Second, callCounts)
	// Set a short prepare timeout.
	dtm.SetPrepareTimeout(50 * time.Millisecond)
	participants := []txn_manager.Participant{
		createMockParticipant("p_normal", nil, nil, nil, 10*time.Millisecond, callCounts),
		participantTimeout,
	}
	txid := "tx_timeout"
	start := time.Now()
	err := dtm.ProcessTransaction(txid, participants)
	duration := time.Since(start)
	if err == nil {
		t.Fatalf("Expected transaction to fail due to timeout")
	}
	state := dtm.GetTransactionState(txid)
	if state != txn_manager.RolledBack {
		t.Fatalf("Expected transaction to be rolled back due to timeout, got state: %v", state)
	}
	if duration > 500*time.Millisecond {
		t.Errorf("Transaction processing took too long: %v", duration)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	dtm := txn_manager.NewDTM()
	var wg sync.WaitGroup
	numTransactions := 10
	results := make([]string, numTransactions)
	mu := sync.Mutex{}
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			txid := "tx_concurrent_" + strconv.Itoa(i)
			participants := []txn_manager.Participant{
				{
					ID: "p_concurrent_1",
					Prepare: func() error { return nil },
					Commit:  func() error { return nil },
					Rollback: func() error { return nil },
				},
				{
					ID: "p_concurrent_2",
					Prepare: func() error { return nil },
					Commit:  func() error { return nil },
					Rollback: func() error { return nil },
				},
			}
			err := dtm.ProcessTransaction(txid, participants)
			mu.Lock()
			if err != nil {
				results[i] = "fail"
			} else {
				if dtm.GetTransactionState(txid) == txn_manager.Committed {
					results[i] = "commit"
				} else {
					results[i] = "rollback"
				}
			}
			mu.Unlock()
		}(i)
	}
	wg.Wait()
	for i, res := range results {
		if res != "commit" {
			t.Errorf("Transaction %d did not commit, got result: %s", i, res)
		}
	}
}

func TestCrashRecovery(t *testing.T) {
	dtm := txn_manager.NewDTM()
	callCounts := &sync.Map{}
	participants := []txn_manager.Participant{
		createMockParticipant("p_recover1", nil, nil, nil, 10*time.Millisecond, callCounts),
		createMockParticipant("p_recover2", nil, nil, nil, 15*time.Millisecond, callCounts),
	}
	txid := "tx_recovery"
	// Start transaction in a goroutine to simulate in-flight processing.
	var wg sync.WaitGroup
	wg.Add(1)
	go func() {
		defer wg.Done()
		_ = dtm.ProcessTransaction(txid, participants)
	}()
	// Simulate a crash before the transaction completes.
	time.Sleep(20 * time.Millisecond)
	dtm.SimulateCrash()
	// Recover using persisted logs.
	recoveredLog := dtm.ExportLog()
	dtmRecovered := txn_manager.NewDTMFromLog(recoveredLog)
	err := dtmRecovered.Recover()
	if err != nil {
		t.Fatalf("Recovery failed: %v", err)
	}
	state := dtmRecovered.GetTransactionState(txid)
	if state != txn_manager.Committed && state != txn_manager.RolledBack {
		t.Fatalf("After recovery, transaction should be finalized, got state: %v", state)
	}
	wg.Wait()
}