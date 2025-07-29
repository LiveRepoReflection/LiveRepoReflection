package dist_tx_orchestrator

import (
	"context"
	"errors"
	"testing"
	"time"
)

type mockService struct {
	name           string
	shouldFail     bool
	shouldTimeout  bool
	compensateFail bool
}

func (m *mockService) Prepare(ctx context.Context, txID string) error {
	if m.shouldTimeout {
		select {
		case <-ctx.Done():
			return ctx.Err()
		case <-time.After(2 * time.Second):
			return nil
		}
	}
	if m.shouldFail {
		return errors.New("prepare failed")
	}
	return nil
}

func (m *mockService) Commit(ctx context.Context, txID string) error {
	if m.shouldFail {
		return errors.New("commit failed")
	}
	return nil
}

func (m *mockService) Rollback(ctx context.Context, txID string) error {
	if m.compensateFail {
		return errors.New("compensate failed")
	}
	return nil
}

func TestOrchestrator_SuccessfulTransaction(t *testing.T) {
	services := []Service{
		&mockService{name: "inventory"},
		&mockService{name: "payment"},
		&mockService{name: "shipping"},
		&mockService{name: "notification"},
	}

	orch := NewOrchestrator(services)
	ctx := context.Background()
	txID := "test-tx-1"

	err := orch.ExecuteTransaction(ctx, txID)
	if err != nil {
		t.Errorf("Expected successful transaction, got error: %v", err)
	}
}

func TestOrchestrator_PrepareFailure(t *testing.T) {
	services := []Service{
		&mockService{name: "inventory"},
		&mockService{name: "payment", shouldFail: true},
		&mockService{name: "shipping"},
		&mockService{name: "notification"},
	}

	orch := NewOrchestrator(services)
	ctx := context.Background()
	txID := "test-tx-2"

	err := orch.ExecuteTransaction(ctx, txID)
	if err == nil {
		t.Error("Expected transaction to fail during prepare phase")
	}
}

func TestOrchestrator_CommitFailure(t *testing.T) {
	services := []Service{
		&mockService{name: "inventory"},
		&mockService{name: "payment"},
		&mockService{name: "shipping", shouldFail: true},
		&mockService{name: "notification"},
	}

	orch := NewOrchestrator(services)
	ctx := context.Background()
	txID := "test-tx-3"

	err := orch.ExecuteTransaction(ctx, txID)
	if err == nil {
		t.Error("Expected transaction to fail during commit phase")
	}
}

func TestOrchestrator_CompensateFailure(t *testing.T) {
	services := []Service{
		&mockService{name: "inventory"},
		&mockService{name: "payment", shouldFail: true},
		&mockService{name: "shipping", compensateFail: true},
		&mockService{name: "notification"},
	}

	orch := NewOrchestrator(services)
	ctx := context.Background()
	txID := "test-tx-4"

	err := orch.ExecuteTransaction(ctx, txID)
	if err == nil {
		t.Error("Expected transaction to fail during compensate phase")
	}
}

func TestOrchestrator_Timeout(t *testing.T) {
	services := []Service{
		&mockService{name: "inventory"},
		&mockService{name: "payment", shouldTimeout: true},
		&mockService{name: "shipping"},
		&mockService{name: "notification"},
	}

	orch := NewOrchestrator(services)
	ctx, cancel := context.WithTimeout(context.Background(), 100*time.Millisecond)
	defer cancel()
	txID := "test-tx-5"

	err := orch.ExecuteTransaction(ctx, txID)
	if err == nil {
		t.Error("Expected transaction to timeout")
	}
}

func TestOrchestrator_EmptyServices(t *testing.T) {
	orch := NewOrchestrator([]Service{})
	ctx := context.Background()
	txID := "test-tx-6"

	err := orch.ExecuteTransaction(ctx, txID)
	if err != nil {
		t.Errorf("Expected successful transaction with empty services, got error: %v", err)
	}
}