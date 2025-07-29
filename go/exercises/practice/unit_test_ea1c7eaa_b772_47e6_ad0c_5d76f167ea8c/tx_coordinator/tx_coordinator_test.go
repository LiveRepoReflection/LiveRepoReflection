package tx_coordinator

import (
	"errors"
	"sync"
	"testing"
	"time"
)

func TestExecuteTransaction_AllSuccess(t *testing.T) {
	participants := []string{"A", "B", "C"}
	var mu sync.Mutex
	callOrder := make([]string, 0)

	prepareFunc := func(participant, transactionID string) error {
		mu.Lock()
		callOrder = append(callOrder, "prepare_"+participant)
		mu.Unlock()
		return nil
	}
	commitFunc := func(participant, transactionID string) error {
		mu.Lock()
		callOrder = append(callOrder, "commit_"+participant)
		mu.Unlock()
		return nil
	}
	rollbackFunc := func(participant, transactionID string) error {
		mu.Lock()
		callOrder = append(callOrder, "rollback_"+participant)
		mu.Unlock()
		return nil
	}

	err := ExecuteTransaction("txn1", participants, prepareFunc, commitFunc, rollbackFunc)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
	// Expected calls: all participants prepared and then all committed.
	expectedCalls := []string{"prepare_A", "prepare_B", "prepare_C", "commit_A", "commit_B", "commit_C"}
	for _, call := range expectedCalls {
		found := false
		for _, actualCall := range callOrder {
			if actualCall == call {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("Expected call %s not found in callOrder %v", call, callOrder)
		}
	}
}

func TestExecuteTransaction_PrepareFailure(t *testing.T) {
	participants := []string{"A", "B", "C"}
	var mu sync.Mutex
	prepared := make(map[string]bool)

	prepareFunc := func(participant, transactionID string) error {
		if participant == "B" {
			return errors.New("prepare error")
		}
		mu.Lock()
		prepared[participant] = true
		mu.Unlock()
		return nil
	}
	commitFunc := func(participant, transactionID string) error {
		return nil
	}
	rollbackCalls := make(map[string]bool)
	rollbackFunc := func(participant, transactionID string) error {
		mu.Lock()
		rollbackCalls[participant] = true
		mu.Unlock()
		return nil
	}

	err := ExecuteTransaction("txn2", participants, prepareFunc, commitFunc, rollbackFunc)
	if err == nil {
		t.Errorf("Expected error due to prepare failure, got nil")
	}
	// Only participants A and C should have been prepared and rolled back.
	if !prepared["A"] || !prepared["C"] {
		t.Errorf("Expected participants A and C to be prepared, got %v", prepared)
	}
	if len(rollbackCalls) != 2 || !rollbackCalls["A"] || !rollbackCalls["C"] {
		t.Errorf("Expected rollback to be called for A and C, got %v", rollbackCalls)
	}
}

func TestExecuteTransaction_CommitFailure(t *testing.T) {
	participants := []string{"A", "B", "C"}

	prepareFunc := func(participant, transactionID string) error {
		return nil
	}
	commitFunc := func(participant, transactionID string) error {
		if participant == "B" {
			return errors.New("commit error")
		}
		return nil
	}
	rollbackFunc := func(participant, transactionID string) error {
		return nil
	}

	err := ExecuteTransaction("txn3", participants, prepareFunc, commitFunc, rollbackFunc)
	if err == nil {
		t.Errorf("Expected error due to commit failure, got nil")
	}
}

func TestExecuteTransaction_RollbackFailure(t *testing.T) {
	participants := []string{"A", "B", "C"}

	prepareFunc := func(participant, transactionID string) error {
		if participant == "C" {
			return errors.New("prepare error")
		}
		return nil
	}
	commitFunc := func(participant, transactionID string) error {
		return nil
	}
	rollbackFunc := func(participant, transactionID string) error {
		if participant == "A" {
			return errors.New("rollback error")
		}
		return nil
	}

	err := ExecuteTransaction("txn4", participants, prepareFunc, commitFunc, rollbackFunc)
	if err == nil {
		t.Errorf("Expected error due to rollback failure, got nil")
	}
}

func TestExecuteTransaction_EmptyParticipants(t *testing.T) {
	participants := []string{}

	prepareFunc := func(participant, transactionID string) error {
		return nil
	}
	commitFunc := func(participant, transactionID string) error {
		return nil
	}
	rollbackFunc := func(participant, transactionID string) error {
		return nil
	}

	err := ExecuteTransaction("txn5", participants, prepareFunc, commitFunc, rollbackFunc)
	if err != nil {
		t.Errorf("Expected no error for empty participants, got %v", err)
	}
}

func TestExecuteTransaction_PrepareTimeout(t *testing.T) {
	participants := []string{"A"}

	prepareFunc := func(participant, transactionID string) error {
		// Simulate a delay longer than the expected timeout (5 seconds)
		time.Sleep(6 * time.Second)
		return nil
	}
	commitFunc := func(participant, transactionID string) error {
		return nil
	}
	rollbackFunc := func(participant, transactionID string) error {
		return nil
	}

	start := time.Now()
	err := ExecuteTransaction("txn6", participants, prepareFunc, commitFunc, rollbackFunc)
	duration := time.Since(start)

	if err == nil {
		t.Errorf("Expected error due to prepare timeout, got nil")
	}
	if duration > 7*time.Second {
		t.Errorf("Expected timeout to occur around 5 seconds; took %v", duration)
	}
}

func TestExecuteTransaction_RepeatedTransactionID(t *testing.T) {
	participants := []string{"A", "B"}
	callCount := make(map[string]int)
	var mu sync.Mutex

	prepareFunc := func(participant, transactionID string) error {
		mu.Lock()
		callCount["prepare_"+participant]++
		mu.Unlock()
		return nil
	}
	commitFunc := func(participant, transactionID string) error {
		mu.Lock()
		callCount["commit_"+participant]++
		mu.Unlock()
		return nil
	}
	rollbackFunc := func(participant, transactionID string) error {
		mu.Lock()
		callCount["rollback_"+participant]++
		mu.Unlock()
		return nil
	}

	// First transaction should execute normally.
	err1 := ExecuteTransaction("txn7", participants, prepareFunc, commitFunc, rollbackFunc)
	if err1 != nil {
		t.Errorf("First transaction should succeed, got error: %v", err1)
	}
	// Second transaction with the same transactionID. The coordinator is expected to handle it gracefully.
	err2 := ExecuteTransaction("txn7", participants, prepareFunc, commitFunc, rollbackFunc)
	if err2 == nil {
		t.Errorf("Repeated transactionID should return an error or be handled gracefully, got nil")
	}
}