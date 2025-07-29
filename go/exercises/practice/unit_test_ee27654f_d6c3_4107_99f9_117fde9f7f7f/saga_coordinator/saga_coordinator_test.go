package saga_coordinator

import (
	"errors"
	"sync"
	"testing"
	"time"
)

// Assume these types and functions are defined in the saga_coordinator package:
// 
// type SagaStep struct {
//     Service      string
//     Transaction  string
//     Compensation string
// }
// 
// type SagaConfig struct {
//     SagaName string
//     Steps    []SagaStep
//     Timeout  time.Duration
// }
// 
// type SagaResult struct {
//     SagaName string
//     Status   string            // "Success", "Compensated", "Failed"
//     Details  map[string]string // key: step transaction, value: status ("Executed", "Compensated", "Failed")
// }
//
// // RegisterTransactionHandler registers a handler for a given service and transaction.
// func RegisterTransactionHandler(service, transaction string, handler func() error)
// 
// // RegisterCompensationHandler registers a compensation handler for a given service and compensation.
// func RegisterCompensationHandler(service, compensation string, handler func() error)
// 
// // ExecuteSaga executes the saga as defined in the provided config and returns a SagaResult.
// func ExecuteSaga(config *SagaConfig) (*SagaResult, error)
// 
// // ResetHandlers resets all registered transaction and compensation handlers.
 
// A mutex protected slice to record compensation call order in tests.
var compMu sync.Mutex
var compensationOrder []string

func resetCompensationOrder() {
	compMu.Lock()
	defer compMu.Unlock()
	compensationOrder = []string{}
}

func appendCompensationOrder(step string) {
	compMu.Lock()
	defer compMu.Unlock()
	compensationOrder = append(compensationOrder, step)
}

func TestSagaSuccess(t *testing.T) {
	// Reset all handlers and compensation order.
	ResetHandlers()
	resetCompensationOrder()

	// Register transaction handlers that all succeed.
	RegisterTransactionHandler("OrderService", "createOrder", func() error {
		return nil
	})
	RegisterTransactionHandler("PaymentService", "reserveFunds", func() error {
		return nil
	})
	RegisterTransactionHandler("InventoryService", "reserveInventory", func() error {
		return nil
	})
	RegisterTransactionHandler("NotificationService", "sendConfirmationEmail", func() error {
		return nil
	})
	RegisterTransactionHandler("OrderService", "confirmOrder", func() error {
		return nil
	})

	// Register compensation handlers (should not be used).
	RegisterCompensationHandler("OrderService", "cancelOrder", func() error {
		appendCompensationOrder("cancelOrder")
		return nil
	})
	RegisterCompensationHandler("PaymentService", "releaseFunds", func() error {
		appendCompensationOrder("releaseFunds")
		return nil
	})
	RegisterCompensationHandler("InventoryService", "releaseInventory", func() error {
		appendCompensationOrder("releaseInventory")
		return nil
	})
	RegisterCompensationHandler("NotificationService", "sendCancellationEmail", func() error {
		appendCompensationOrder("sendCancellationEmail")
		return nil
	})

	config := &SagaConfig{
		SagaName: "OrderPlacementSaga",
		Timeout:  2 * time.Second,
		Steps: []SagaStep{
			{Service: "OrderService", Transaction: "createOrder", Compensation: "cancelOrder"},
			{Service: "PaymentService", Transaction: "reserveFunds", Compensation: "releaseFunds"},
			{Service: "InventoryService", Transaction: "reserveInventory", Compensation: "releaseInventory"},
			{Service: "NotificationService", Transaction: "sendConfirmationEmail", Compensation: "sendCancellationEmail"},
			{Service: "OrderService", Transaction: "confirmOrder", Compensation: ""},
		},
	}

	result, err := ExecuteSaga(config)
	if err != nil {
		t.Fatalf("Expected success, but got error: %v", err)
	}
	if result.Status != "Success" {
		t.Fatalf("Expected saga status 'Success', got '%s'", result.Status)
	}
	// Check that no compensation handlers were invoked.
	compMu.Lock()
	if len(compensationOrder) != 0 {
		t.Errorf("Expected no compensations, but got: %v", compensationOrder)
	}
	compMu.Unlock()
}

func TestSagaFailure(t *testing.T) {
	// Reset all handlers and compensation order.
	ResetHandlers()
	resetCompensationOrder()

	// Register transaction handlers.
	RegisterTransactionHandler("OrderService", "createOrder", func() error {
		return nil
	})
	RegisterTransactionHandler("PaymentService", "reserveFunds", func() error {
		return nil
	})
	// Simulate failure in InventoryService.
	RegisterTransactionHandler("InventoryService", "reserveInventory", func() error {
		return errors.New("inventory shortage")
	})
	RegisterTransactionHandler("NotificationService", "sendConfirmationEmail", func() error {
		return nil
	})
	RegisterTransactionHandler("OrderService", "confirmOrder", func() error {
		return nil
	})

	// Register compensation handlers that record their invocation.
	RegisterCompensationHandler("OrderService", "cancelOrder", func() error {
		appendCompensationOrder("cancelOrder")
		return nil
	})
	RegisterCompensationHandler("PaymentService", "releaseFunds", func() error {
		appendCompensationOrder("releaseFunds")
		return nil
	})
	RegisterCompensationHandler("InventoryService", "releaseInventory", func() error {
		appendCompensationOrder("releaseInventory")
		return nil
	})
	RegisterCompensationHandler("NotificationService", "sendCancellationEmail", func() error {
		appendCompensationOrder("sendCancellationEmail")
		return nil
	})

	config := &SagaConfig{
		SagaName: "OrderPlacementSaga",
		Timeout:  2 * time.Second,
		Steps: []SagaStep{
			{Service: "OrderService", Transaction: "createOrder", Compensation: "cancelOrder"},
			{Service: "PaymentService", Transaction: "reserveFunds", Compensation: "releaseFunds"},
			{Service: "InventoryService", Transaction: "reserveInventory", Compensation: "releaseInventory"},
			{Service: "NotificationService", Transaction: "sendConfirmationEmail", Compensation: "sendCancellationEmail"},
			{Service: "OrderService", Transaction: "confirmOrder", Compensation: ""},
		},
	}

	result, err := ExecuteSaga(config)
	// Expecting error due to inventory shortage
	if err == nil {
		t.Fatalf("Expected error due to inventory failure, but saga executed with result: %+v", result)
	}
	// Expect compensations to have been executed for previously successful steps.
	// In our saga, steps 1 and 2 succeeded before failure at step 3.
	expectedCompensationOrder := []string{"releaseFunds", "cancelOrder"}
	compMu.Lock()
	if len(compensationOrder) != len(expectedCompensationOrder) {
		t.Errorf("Expected compensation order %v, got %v", expectedCompensationOrder, compensationOrder)
	} else {
		for i, v := range expectedCompensationOrder {
			if compensationOrder[i] != v {
				t.Errorf("At index %d, expected %s, got %s", i, v, compensationOrder[i])
			}
		}
	}
	compMu.Unlock()
	if result.Status != "Compensated" {
		t.Errorf("Expected saga status 'Compensated', but got '%s'", result.Status)
	}
}

func TestSagaTimeout(t *testing.T) {
	// Reset all handlers and compensation order.
	ResetHandlers()
	resetCompensationOrder()

	// Register transaction handlers.
	RegisterTransactionHandler("OrderService", "createOrder", func() error {
		return nil
	})
	// Simulate a delay that exceeds the timeout.
	RegisterTransactionHandler("PaymentService", "reserveFunds", func() error {
		time.Sleep(3 * time.Second)
		return nil
	})
	RegisterTransactionHandler("InventoryService", "reserveInventory", func() error {
		return nil
	})
	RegisterTransactionHandler("NotificationService", "sendConfirmationEmail", func() error {
		return nil
	})
	RegisterTransactionHandler("OrderService", "confirmOrder", func() error {
		return nil
	})

	// Register compensation handlers that record their invocation.
	RegisterCompensationHandler("OrderService", "cancelOrder", func() error {
		appendCompensationOrder("cancelOrder")
		return nil
	})
	RegisterCompensationHandler("PaymentService", "releaseFunds", func() error {
		appendCompensationOrder("releaseFunds")
		return nil
	})
	RegisterCompensationHandler("InventoryService", "releaseInventory", func() error {
		appendCompensationOrder("releaseInventory")
		return nil
	})
	RegisterCompensationHandler("NotificationService", "sendCancellationEmail", func() error {
		appendCompensationOrder("sendCancellationEmail")
		return nil
	})

	config := &SagaConfig{
		SagaName: "OrderPlacementSaga",
		Timeout:  2 * time.Second, // PaymentService delay exceeds timeout
		Steps: []SagaStep{
			{Service: "OrderService", Transaction: "createOrder", Compensation: "cancelOrder"},
			{Service: "PaymentService", Transaction: "reserveFunds", Compensation: "releaseFunds"},
			{Service: "InventoryService", Transaction: "reserveInventory", Compensation: "releaseInventory"},
			{Service: "NotificationService", Transaction: "sendConfirmationEmail", Compensation: "sendCancellationEmail"},
			{Service: "OrderService", Transaction: "confirmOrder", Compensation: ""},
		},
	}

	result, err := ExecuteSaga(config)
	if err == nil {
		t.Fatalf("Expected timeout error, but saga executed with result: %+v", result)
	}
	// Only the first step should have executed before timeout.
	expectedCompensationOrder := []string{"cancelOrder"}
	compMu.Lock()
	if len(compensationOrder) != len(expectedCompensationOrder) {
		t.Errorf("Expected compensation order %v, got %v", expectedCompensationOrder, compensationOrder)
	} else {
		for i, v := range expectedCompensationOrder {
			if compensationOrder[i] != v {
				t.Errorf("At index %d, expected %s, got %s", i, v, compensationOrder[i])
			}
		}
	}
	compMu.Unlock()
	if result.Status != "Compensated" {
		t.Errorf("Expected saga status 'Compensated' due to timeout, but got '%s'", result.Status)
	}
}

func TestConcurrentSagaExecutions(t *testing.T) {
	// Reset all handlers and compensation order.
	ResetHandlers()
	resetCompensationOrder()

	// Register transaction handlers that all succeed quickly.
	RegisterTransactionHandler("OrderService", "createOrder", func() error {
		return nil
	})
	RegisterTransactionHandler("PaymentService", "reserveFunds", func() error {
		return nil
	})
	RegisterTransactionHandler("InventoryService", "reserveInventory", func() error {
		return nil
	})
	RegisterTransactionHandler("NotificationService", "sendConfirmationEmail", func() error {
		return nil
	})
	RegisterTransactionHandler("OrderService", "confirmOrder", func() error {
		return nil
	})

	// Register compensation handlers.
	RegisterCompensationHandler("OrderService", "cancelOrder", func() error {
		appendCompensationOrder("cancelOrder")
		return nil
	})
	RegisterCompensationHandler("PaymentService", "releaseFunds", func() error {
		appendCompensationOrder("releaseFunds")
		return nil
	})
	RegisterCompensationHandler("InventoryService", "releaseInventory", func() error {
		appendCompensationOrder("releaseInventory")
		return nil
	})
	RegisterCompensationHandler("NotificationService", "sendCancellationEmail", func() error {
		appendCompensationOrder("sendCancellationEmail")
		return nil
	})

	config := &SagaConfig{
		SagaName: "ConcurrentOrderPlacement",
		Timeout:  2 * time.Second,
		Steps: []SagaStep{
			{Service: "OrderService", Transaction: "createOrder", Compensation: "cancelOrder"},
			{Service: "PaymentService", Transaction: "reserveFunds", Compensation: "releaseFunds"},
			{Service: "InventoryService", Transaction: "reserveInventory", Compensation: "releaseInventory"},
			{Service: "NotificationService", Transaction: "sendConfirmationEmail", Compensation: "sendCancellationEmail"},
			{Service: "OrderService", Transaction: "confirmOrder", Compensation: ""},
		},
	}

	var wg sync.WaitGroup
	numSagas := 10
	results := make([]*SagaResult, numSagas)
	errs := make([]error, numSagas)
	for i := 0; i < numSagas; i++ {
		wg.Add(1)
		go func(index int) {
			defer wg.Done()
			res, err := ExecuteSaga(config)
			results[index] = res
			errs[index] = err
		}(i)
	}
	wg.Wait()

	for i := 0; i < numSagas; i++ {
		if errs[i] != nil {
			t.Errorf("Saga %d failed with error: %v", i, errs[i])
		} else if results[i].Status != "Success" {
			t.Errorf("Saga %d expected status 'Success', got '%s'", i, results[i].Status)
		}
	}
}