package saga_tx

import (
	"errors"
	"os"
	"strconv"
	"sync"
	"testing"
	"time"
)

var (
	compLog   []string
	compMutex sync.Mutex
)

func resetCompLog() {
	compMutex.Lock()
	compLog = []string{}
	compMutex.Unlock()
}

func recordComp(name string) {
	compMutex.Lock()
	compLog = append(compLog, name)
	compMutex.Unlock()
}

func fakeCallService(serviceID string, operation string, data string) error {
	if data == "fail" {
		return errors.New("service error")
	}
	return nil
}

var originalCallService func(serviceID string, operation string, data string) error

func TestMain(m *testing.M) {
	originalCallService = CallService
	CallService = fakeCallService
	code := m.Run()
	CallService = originalCallService
	os.Exit(code)
}

func TestOrchestrateTransactionSuccess(t *testing.T) {
	resetCompLog()
	steps := []TransactionStep{
		{
			ServiceID: "InventoryService",
			Operation: "ReserveItem",
			Data:      "item1",
			Compensation: func(data string) error {
				go func() {
					time.Sleep(10 * time.Millisecond)
					recordComp("InventoryCompensation:" + data)
				}()
				return nil
			},
		},
		{
			ServiceID: "OrderService",
			Operation: "CreateOrder",
			Data:      "order1",
			Compensation: func(data string) error {
				go func() {
					time.Sleep(10 * time.Millisecond)
					recordComp("OrderCompensation:" + data)
				}()
				return nil
			},
		},
		{
			ServiceID: "PaymentService",
			Operation: "ProcessPayment",
			Data:      "payment1",
			Compensation: func(data string) error {
				go func() {
					time.Sleep(10 * time.Millisecond)
					recordComp("PaymentCompensation:" + data)
				}()
				return nil
			},
		},
	}

	err := OrchestrateTransaction(steps)
	if err != nil {
		t.Errorf("Expected success, but got error: %v", err)
	}
	time.Sleep(50 * time.Millisecond)
	compMutex.Lock()
	if len(compLog) != 0 {
		t.Errorf("Expected no compensation calls on success, but got: %v", compLog)
	}
	compMutex.Unlock()
}

func TestOrchestrateTransactionFailure(t *testing.T) {
	resetCompLog()
	steps := []TransactionStep{
		{
			ServiceID: "InventoryService",
			Operation: "ReserveItem",
			Data:      "item1",
			Compensation: func(data string) error {
				go func() {
					time.Sleep(10 * time.Millisecond)
					recordComp("InventoryCompensation:" + data)
				}()
				return nil
			},
		},
		{
			ServiceID: "OrderService",
			Operation: "CreateOrder",
			Data:      "fail",
			Compensation: func(data string) error {
				go func() {
					time.Sleep(10 * time.Millisecond)
					recordComp("OrderCompensation:" + data)
				}()
				return nil
			},
		},
		{
			ServiceID: "PaymentService",
			Operation: "ProcessPayment",
			Data:      "payment1",
			Compensation: func(data string) error {
				go func() {
					time.Sleep(10 * time.Millisecond)
					recordComp("PaymentCompensation:" + data)
				}()
				return nil
			},
		},
	}

	err := OrchestrateTransaction(steps)
	if err == nil {
		t.Errorf("Expected error due to failure in operation, but got success")
	}
	time.Sleep(100 * time.Millisecond)
	compMutex.Lock()
	defer compMutex.Unlock()
	expectedCompensations := []string{
		"InventoryCompensation:item1",
	}
	if len(compLog) != len(expectedCompensations) {
		t.Errorf("Expected compensation calls %v, but got: %v", expectedCompensations, compLog)
	}
	for i, comp := range expectedCompensations {
		if compLog[i] != comp {
			t.Errorf("Expected compensation %s, got %s", comp, compLog[i])
		}
	}
}

func TestOrchestrateTransactionIdempotency(t *testing.T) {
	resetCompLog()
	steps := []TransactionStep{
		{
			ServiceID: "InventoryService",
			Operation: "ReserveItem",
			Data:      "item_idempotent",
			Compensation: func(data string) error {
				go func() {
					time.Sleep(10 * time.Millisecond)
					recordComp("InventoryCompensation:" + data)
				}()
				return nil
			},
		},
	}

	for i := 0; i < 3; i++ {
		err := OrchestrateTransaction(steps)
		if err != nil {
			t.Errorf("Run %d: Expected success, but got error: %v", i, err)
		}
	}
	time.Sleep(50 * time.Millisecond)
	compMutex.Lock()
	if len(compLog) != 0 {
		t.Errorf("Expected no compensation calls in idempotency test, but got: %v", compLog)
	}
	compMutex.Unlock()
}

func TestConcurrentTransactions(t *testing.T) {
	var wg sync.WaitGroup
	transactionCount := 10
	errCh := make(chan error, transactionCount)

	for i := 0; i < transactionCount; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()
			resetCompLog()
			steps := []TransactionStep{
				{
					ServiceID: "InventoryService",
					Operation: "ReserveItem",
					Data:      "item_concurrent_" + strconv.Itoa(idx),
					Compensation: func(data string) error {
						go func() {
							time.Sleep(10 * time.Millisecond)
							recordComp("InventoryCompensation:" + data)
						}()
						return nil
					},
				},
				{
					ServiceID: "OrderService",
					Operation: "CreateOrder",
					Data:      "order_concurrent_" + strconv.Itoa(idx),
					Compensation: func(data string) error {
						go func() {
							time.Sleep(10 * time.Millisecond)
							recordComp("OrderCompensation:" + data)
						}()
						return nil
					},
				},
			}
			if idx%2 == 0 {
				steps[1].Data = "fail"
			}
			err := OrchestrateTransaction(steps)
			errCh <- err
		}(i)
	}
	wg.Wait()
	close(errCh)

	countSuccess := 0
	countFailure := 0
	for err := range errCh {
		if err != nil {
			countFailure++
		} else {
			countSuccess++
		}
	}
	if countSuccess != transactionCount/2 {
		t.Errorf("Expected %d successes, got %d", transactionCount/2, countSuccess)
	}
	if countFailure != transactionCount/2 {
		t.Errorf("Expected %d failures, got %d", transactionCount/2, countFailure)
	}
}