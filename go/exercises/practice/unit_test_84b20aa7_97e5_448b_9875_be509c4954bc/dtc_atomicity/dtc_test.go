package dtc_atomicity

import (
	"context"
	"errors"
	"testing"
	"time"
)

type mockService struct {
	name           string
	prepareFunc    func(ctx context.Context, txID string) error
	commitFunc     func(ctx context.Context, txID string) error
	rollbackFunc   func(ctx context.Context, txID string) error
	prepareDelay   time.Duration
	commitDelay    time.Duration
	rollbackDelay  time.Duration
}

func (m *mockService) Prepare(ctx context.Context, txID string) error {
	if m.prepareDelay > 0 {
		select {
		case <-time.After(m.prepareDelay):
		case <-ctx.Done():
			return ctx.Err()
		}
	}
	if m.prepareFunc != nil {
		return m.prepareFunc(ctx, txID)
	}
	return nil
}

func (m *mockService) Commit(ctx context.Context, txID string) error {
	if m.commitDelay > 0 {
		select {
		case <-time.After(m.commitDelay):
		case <-ctx.Done():
			return ctx.Err()
		}
	}
	if m.commitFunc != nil {
		return m.commitFunc(ctx, txID)
	}
	return nil
}

func (m *mockService) Rollback(ctx context.Context, txID string) error {
	if m.rollbackDelay > 0 {
		select {
		case <-time.After(m.rollbackDelay):
		case <-ctx.Done():
			return ctx.Err()
		}
	}
	if m.rollbackFunc != nil {
		return m.rollbackFunc(ctx, txID)
	}
	return nil
}

func TestDTC_SuccessfulTransaction(t *testing.T) {
	dtc := NewDTC()
	orderService := &mockService{name: "order"}
	inventoryService := &mockService{name: "inventory"}
	paymentService := &mockService{name: "payment"}

	dtc.RegisterService(orderService)
	dtc.RegisterService(inventoryService)
	dtc.RegisterService(paymentService)

	ctx := context.Background()
	err := dtc.ExecuteTransaction(ctx, "tx-123")
	if err != nil {
		t.Fatalf("Expected successful transaction, got error: %v", err)
	}
}

func TestDTC_PrepareFailure(t *testing.T) {
	dtc := NewDTC()
	orderService := &mockService{name: "order"}
	inventoryService := &mockService{
		name: "inventory",
		prepareFunc: func(ctx context.Context, txID string) error {
			return errors.New("inventory unavailable")
		},
	}
	paymentService := &mockService{name: "payment"}

	dtc.RegisterService(orderService)
	dtc.RegisterService(inventoryService)
	dtc.RegisterService(paymentService)

	ctx := context.Background()
	err := dtc.ExecuteTransaction(ctx, "tx-456")
	if err == nil {
		t.Fatal("Expected transaction to fail due to prepare failure")
	}
}

func TestDTC_TimeoutDuringPrepare(t *testing.T) {
	dtc := NewDTCWithOptions(DTCOptions{
		PrepareTimeout:  50 * time.Millisecond,
		CommitTimeout:   1 * time.Second,
		MaxRetries:      3,
		RetryInterval:   100 * time.Millisecond,
	})

	orderService := &mockService{name: "order"}
	inventoryService := &mockService{
		name:         "inventory",
		prepareDelay: 100 * time.Millisecond,
	}
	paymentService := &mockService{name: "payment"}

	dtc.RegisterService(orderService)
	dtc.RegisterService(inventoryService)
	dtc.RegisterService(paymentService)

	ctx := context.Background()
	err := dtc.ExecuteTransaction(ctx, "tx-789")
	if err == nil {
		t.Fatal("Expected transaction to timeout during prepare phase")
	}
}

func TestDTC_CommitFailureWithRetries(t *testing.T) {
	commitAttempts := 0
	dtc := NewDTCWithOptions(DTCOptions{
		PrepareTimeout:  1 * time.Second,
		CommitTimeout:   1 * time.Second,
		MaxRetries:      3,
		RetryInterval:   10 * time.Millisecond,
	})

	orderService := &mockService{name: "order"}
	inventoryService := &mockService{name: "inventory"}
	paymentService := &mockService{
		name: "payment",
		commitFunc: func(ctx context.Context, txID string) error {
			commitAttempts++
			if commitAttempts < 3 {
				return errors.New("payment service temporarily unavailable")
			}
			return nil
		},
	}

	dtc.RegisterService(orderService)
	dtc.RegisterService(inventoryService)
	dtc.RegisterService(paymentService)

	ctx := context.Background()
	err := dtc.ExecuteTransaction(ctx, "tx-abc")
	if err != nil {
		t.Fatalf("Expected transaction to succeed after retries, got error: %v", err)
	}
	if commitAttempts != 3 {
		t.Fatalf("Expected 3 commit attempts, got %d", commitAttempts)
	}
}

func TestDTC_ConcurrentTransactions(t *testing.T) {
	dtc := NewDTCWithOptions(DTCOptions{
		PrepareTimeout:  1 * time.Second,
		CommitTimeout:   1 * time.Second,
		MaxRetries:      3,
		RetryInterval:   10 * time.Millisecond,
	})

	orderService := &mockService{name: "order"}
	inventoryService := &mockService{name: "inventory"}
	paymentService := &mockService{name: "payment"}

	dtc.RegisterService(orderService)
	dtc.RegisterService(inventoryService)
	dtc.RegisterService(paymentService)

	ctx := context.Background()
	const numTransactions = 10
	results := make(chan error, numTransactions)

	for i := 0; i < numTransactions; i++ {
		go func(txNum int) {
			err := dtc.ExecuteTransaction(ctx, string(rune(txNum)))
			results <- err
		}(i)
	}

	for i := 0; i < numTransactions; i++ {
		err := <-results
		if err != nil {
			t.Fatalf("Transaction %d failed: %v", i, err)
		}
	}
}

func TestDTC_ServiceUnavailableAfterPrepare(t *testing.T) {
	dtc := NewDTCWithOptions(DTCOptions{
		PrepareTimeout:  1 * time.Second,
		CommitTimeout:   1 * time.Second,
		MaxRetries:      1,
		RetryInterval:   10 * time.Millisecond,
	})

	orderService := &mockService{name: "order"}
	inventoryService := &mockService{name: "inventory"}
	paymentService := &mockService{
		name: "payment",
		commitFunc: func(ctx context.Context, txID string) error {
			return errors.New("payment service crashed")
		},
	}

	dtc.RegisterService(orderService)
	dtc.RegisterService(inventoryService)
	dtc.RegisterService(paymentService)

	ctx := context.Background()
	err := dtc.ExecuteTransaction(ctx, "tx-crash")
	if err == nil {
		t.Fatal("Expected transaction to fail due to service crash during commit")
	}
}