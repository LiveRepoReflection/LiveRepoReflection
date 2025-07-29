package transaction_saga

import (
	"context"
	"errors"
	"testing"
	"time"
)

func TestTransactionOrchestrator_Execute_Success(t *testing.T) {
	orchestrator := NewTransactionOrchestrator()
	ctx := context.Background()

	actions := []Action{
		{
			Name: "CreateOrder",
			Forward: func(ctx context.Context) error {
				return nil
			},
			Compensation: func(ctx context.Context) error {
				return nil
			},
			Timeout: time.Second,
		},
		{
			Name: "ProcessPayment",
			Forward: func(ctx context.Context) error {
				return nil
			},
			Compensation: func(ctx context.Context) error {
				return nil
			},
			Timeout: time.Second,
		},
	}

	err := orchestrator.Execute(ctx, actions)
	if err != nil {
		t.Errorf("Expected no error, got %v", err)
	}
}

func TestTransactionOrchestrator_Execute_FailureWithCompensation(t *testing.T) {
	orchestrator := NewTransactionOrchestrator()
	ctx := context.Background()

	compensationCalled := false

	actions := []Action{
		{
			Name: "CreateOrder",
			Forward: func(ctx context.Context) error {
				return nil
			},
			Compensation: func(ctx context.Context) error {
				compensationCalled = true
				return nil
			},
			Timeout: time.Second,
		},
		{
			Name: "ProcessPayment",
			Forward: func(ctx context.Context) error {
				return errors.New("payment failed")
			},
			Compensation: func(ctx context.Context) error {
				return nil
			},
			Timeout: time.Second,
		},
	}

	err := orchestrator.Execute(ctx, actions)
	if err == nil {
		t.Error("Expected error, got nil")
	}
	if !compensationCalled {
		t.Error("Compensation for first action was not called")
	}
}

func TestTransactionOrchestrator_Execute_Timeout(t *testing.T) {
	orchestrator := NewTransactionOrchestrator()
	ctx := context.Background()

	actions := []Action{
		{
			Name: "SlowOperation",
			Forward: func(ctx context.Context) error {
				select {
				case <-time.After(2 * time.Second):
					return nil
				case <-ctx.Done():
					return ctx.Err()
				}
			},
			Compensation: func(ctx context.Context) error {
				return nil
			},
			Timeout: time.Second,
		},
	}

	err := orchestrator.Execute(ctx, actions)
	if err == nil {
		t.Error("Expected timeout error, got nil")
	}
	if !errors.Is(err, context.DeadlineExceeded) {
		t.Errorf("Expected DeadlineExceeded error, got %v", err)
	}
}

func TestTransactionOrchestrator_Execute_CompensationFailure(t *testing.T) {
	orchestrator := NewTransactionOrchestrator()
	ctx := context.Background()

	actions := []Action{
		{
			Name: "CreateOrder",
			Forward: func(ctx context.Context) error {
				return nil
			},
			Compensation: func(ctx context.Context) error {
				return errors.New("compensation failed")
			},
			Timeout: time.Second,
		},
		{
			Name: "ProcessPayment",
			Forward: func(ctx context.Context) error {
				return errors.New("payment failed")
			},
			Compensation: func(ctx context.Context) error {
				return nil
			},
			Timeout: time.Second,
		},
	}

	err := orchestrator.Execute(ctx, actions)
	if err == nil {
		t.Error("Expected error, got nil")
	}
}

func TestTransactionOrchestrator_ConcurrentExecution(t *testing.T) {
	orchestrator := NewTransactionOrchestrator()
	ctx := context.Background()

	results := make(chan error, 2)

	actions := []Action{
		{
			Name: "CreateOrder",
			Forward: func(ctx context.Context) error {
				return nil
			},
			Compensation: func(ctx context.Context) error {
				return nil
			},
			Timeout: time.Second,
		},
	}

	go func() {
		results <- orchestrator.Execute(ctx, actions)
	}()

	go func() {
		results <- orchestrator.Execute(ctx, actions)
	}()

	err1 := <-results
	err2 := <-results

	if err1 != nil {
		t.Errorf("First execution failed: %v", err1)
	}
	if err2 != nil {
		t.Errorf("Second execution failed: %v", err2)
	}
}