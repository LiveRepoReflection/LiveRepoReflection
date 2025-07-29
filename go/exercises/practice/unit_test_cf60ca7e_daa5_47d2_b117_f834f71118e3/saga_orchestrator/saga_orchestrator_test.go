package saga_orchestrator

import (
	"errors"
	"testing"
	"time"
)

func TestSagaOrchestrator_SuccessfulTransaction(t *testing.T) {
	steps := []SagaStep{
		{
			Commit: func() error {
				return nil
			},
			Rollback: func() error {
				return nil
			},
			Timeout: 1 * time.Second,
		},
		{
			Commit: func() error {
				return nil
			},
			Rollback: func() error {
				return nil
			},
			Timeout: 1 * time.Second,
		},
	}

	orchestrator := NewSagaOrchestrator()
	err := orchestrator.Execute(steps)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

func TestSagaOrchestrator_FailedTransactionWithRollback(t *testing.T) {
	rollbackCalled := false
	steps := []SagaStep{
		{
			Commit: func() error {
				return nil
			},
			Rollback: func() error {
				rollbackCalled = true
				return nil
			},
			Timeout: 1 * time.Second,
		},
		{
			Commit: func() error {
				return errors.New("commit failed")
			},
			Rollback: func() error {
				return nil
			},
			Timeout: 1 * time.Second,
		},
	}

	orchestrator := NewSagaOrchestrator()
	err := orchestrator.Execute(steps)
	if err == nil {
		t.Error("Expected error, got nil")
	}
	if !rollbackCalled {
		t.Error("Rollback was not called")
	}
}

func TestSagaOrchestrator_FailedRollbackWithRetry(t *testing.T) {
	rollbackAttempts := 0
	steps := []SagaStep{
		{
			Commit: func() error {
				return nil
			},
			Rollback: func() error {
				rollbackAttempts++
				if rollbackAttempts < 3 {
					return errors.New("temporary rollback failure")
				}
				return nil
			},
			Timeout: 1 * time.Second,
		},
		{
			Commit: func() error {
				return errors.New("commit failed")
			},
			Rollback: func() error {
				return nil
			},
			Timeout: 1 * time.Second,
		},
	}

	orchestrator := NewSagaOrchestrator()
	err := orchestrator.Execute(steps)
	if err == nil {
		t.Error("Expected error, got nil")
	}
	if rollbackAttempts != 3 {
		t.Errorf("Expected 3 rollback attempts, got %d", rollbackAttempts)
	}
}

func TestSagaOrchestrator_Timeout(t *testing.T) {
	steps := []SagaStep{
		{
			Commit: func() error {
				time.Sleep(2 * time.Second)
				return nil
			},
			Rollback: func() error {
				return nil
			},
			Timeout: 1 * time.Second,
		},
	}

	orchestrator := NewSagaOrchestrator()
	err := orchestrator.Execute(steps)
	if err == nil {
		t.Error("Expected timeout error, got nil")
	}
}

func TestSagaOrchestrator_ConcurrentTransactions(t *testing.T) {
	steps := []SagaStep{
		{
			Commit: func() error {
				return nil
			},
			Rollback: func() error {
				return nil
			},
			Timeout: 1 * time.Second,
		},
	}

	orchestrator := NewSagaOrchestrator()

	done := make(chan bool)
	for i := 0; i < 3; i++ {
		go func() {
			err := orchestrator.Execute(steps)
			if err != nil {
				t.Errorf("Unexpected error in concurrent transaction: %v", err)
			}
			done <- true
		}()
	}

	for i := 0; i < 3; i++ {
		<-done
	}
}