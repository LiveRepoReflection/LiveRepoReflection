package dist_tx_saga_test

import (
	"errors"
	"strconv"
	"sync"
	"testing"
	"time"

	"dist_tx_saga"
)

func TestSuccessfulTransaction(t *testing.T) {
	orch := dist_tx_saga.NewOrchestrator()

	// Set up mocks that always succeed.
	orch.SetInventoryFunc(func(txID string) error {
		return nil
	})
	orch.SetPaymentFunc(func(txID string) error {
		return nil
	})
	orch.SetShippingFunc(func(txID string) error {
		return nil
	})

	// Set compensating functions (even though they should not be called on success).
	orch.SetCompensateInventoryFunc(func(txID string) error {
		return nil
	})
	orch.SetCompensatePaymentFunc(func(txID string) error {
		return nil
	})
	orch.SetCompensateShippingFunc(func(txID string) error {
		return nil
	})

	txID := "txn_success"
	err := orch.ExecuteTransaction(txID)
	if err != nil {
		t.Fatalf("Expected successful transaction, got error: %v", err)
	}

	status, err := orch.GetTransactionStatus(txID)
	if err != nil {
		t.Fatalf("Failed to get transaction status: %v", err)
	}
	if status != dist_tx_saga.Committed {
		t.Fatalf("Expected transaction committed, got %v", status)
	}
}

func TestTransactionFailureAndCompensation(t *testing.T) {
	orch := dist_tx_saga.NewOrchestrator()

	inventoryCalled := false
	paymentCalled := false
	shippingCalled := false
	compensateInventoryCalled := false
	compensatePaymentCalled := false
	compensateShippingCalled := false

	orch.SetInventoryFunc(func(txID string) error {
		inventoryCalled = true
		return nil
	})
	orch.SetPaymentFunc(func(txID string) error {
		paymentCalled = true
		return errors.New("payment service error")
	})
	orch.SetShippingFunc(func(txID string) error {
		shippingCalled = true
		return nil
	})

	orch.SetCompensateInventoryFunc(func(txID string) error {
		compensateInventoryCalled = true
		return nil
	})
	orch.SetCompensatePaymentFunc(func(txID string) error {
		compensatePaymentCalled = true
		return nil
	})
	orch.SetCompensateShippingFunc(func(txID string) error {
		compensateShippingCalled = true
		return nil
	})

	txID := "txn_failure"
	err := orch.ExecuteTransaction(txID)
	if err == nil {
		t.Fatalf("Expected failure due to payment error, but transaction succeeded")
	}

	if !inventoryCalled {
		t.Fatalf("Expected inventory service to be called")
	}
	if !paymentCalled {
		t.Fatalf("Expected payment service to be called")
	}
	if shippingCalled {
		t.Fatalf("Did not expect shipping service to be called")
	}
	if !compensateInventoryCalled {
		t.Fatalf("Expected inventory compensating function to be called")
	}
	// Payment was not successful so its compensation should not be triggered.
	if compensatePaymentCalled {
		t.Fatalf("Did not expect payment compensating function to be called")
	}
	if compensateShippingCalled {
		t.Fatalf("Did not expect shipping compensating function to be called")
	}

	status, err := orch.GetTransactionStatus(txID)
	if err != nil {
		t.Fatalf("Failed to get transaction status: %v", err)
	}
	if status != dist_tx_saga.Aborted {
		t.Fatalf("Expected transaction aborted, got %v", status)
	}
}

func TestIdempotency(t *testing.T) {
	orch := dist_tx_saga.NewOrchestrator()

	callCount := 0
	orch.SetInventoryFunc(func(txID string) error {
		callCount++
		return nil
	})
	orch.SetPaymentFunc(func(txID string) error {
		return nil
	})
	orch.SetShippingFunc(func(txID string) error {
		return nil
	})
	orch.SetCompensateInventoryFunc(func(txID string) error {
		return nil
	})
	orch.SetCompensatePaymentFunc(func(txID string) error {
		return nil
	})
	orch.SetCompensateShippingFunc(func(txID string) error {
		return nil
	})

	txID := "txn_idempotent"
	var wg sync.WaitGroup
	iterations := 3
	for i := 0; i < iterations; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			err := orch.ExecuteTransaction(txID)
			if err != nil {
				t.Errorf("Expected idempotent transaction to succeed, got error: %v", err)
			}
		}()
	}
	wg.Wait()

	if callCount > 1 {
		t.Fatalf("Expected inventory function to be called once due to idempotency, got %d calls", callCount)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	orch := dist_tx_saga.NewOrchestrator()

	orch.SetInventoryFunc(func(txID string) error {
		time.Sleep(10 * time.Millisecond)
		return nil
	})
	orch.SetPaymentFunc(func(txID string) error {
		time.Sleep(10 * time.Millisecond)
		return nil
	})
	orch.SetShippingFunc(func(txID string) error {
		time.Sleep(10 * time.Millisecond)
		return nil
	})
	orch.SetCompensateInventoryFunc(func(txID string) error {
		return nil
	})
	orch.SetCompensatePaymentFunc(func(txID string) error {
		return nil
	})
	orch.SetCompensateShippingFunc(func(txID string) error {
		return nil
	})

	numTransactions := 10
	var wg sync.WaitGroup
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func(txNum int) {
			defer wg.Done()
			txID := "txn_concurrent_" + strconv.Itoa(txNum)
			err := orch.ExecuteTransaction(txID)
			if err != nil {
				t.Errorf("Transaction %s failed: %v", txID, err)
			}
		}(i)
	}
	wg.Wait()

	for i := 0; i < numTransactions; i++ {
		txID := "txn_concurrent_" + strconv.Itoa(i)
		status, err := orch.GetTransactionStatus(txID)
		if err != nil {
			t.Errorf("Error fetching status for transaction %s: %v", txID, err)
		}
		if status != dist_tx_saga.Committed {
			t.Errorf("Expected transaction %s to be committed, got %v", txID, status)
		}
	}
}