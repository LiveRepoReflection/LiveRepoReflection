package dtc_atomic

import (
	"errors"
	"sync"
	"testing"
	"time"
)

// Assuming the Coordinator type and Service interface are defined in the dtc_atomic package.
// Service interface is expected to have the following methods:
//   Prepare(timeout time.Duration) error
//   Commit(timeout time.Duration) error
//   Rollback(timeout time.Duration) error
//
// And Coordinator is expected to be created using NewCoordinator(timeout time.Duration)
// and provides a method ExecuteTransaction(services []Service) error.

// MockService simulates a service participating in the distributed transaction.
type MockService struct {
	id            string
	prepareDelay  time.Duration
	commitDelay   time.Duration
	rollbackDelay time.Duration
	prepareOK     bool
	commitOK      bool
	// For tracking the number of calls.
	prepareCalled  int
	commitCalled   int
	rollbackCalled int
}

// Prepare simulates the prepare phase.
func (m *MockService) Prepare(timeout time.Duration) error {
	m.prepareCalled++
	// Simulate delay.
	time.Sleep(m.prepareDelay)
	if m.prepareDelay > timeout {
		return errors.New("prepare timeout")
	}
	if !m.prepareOK {
		return errors.New("prepare failed")
	}
	return nil
}

// Commit simulates the commit phase.
func (m *MockService) Commit(timeout time.Duration) error {
	m.commitCalled++
	time.Sleep(m.commitDelay)
	if m.commitDelay > timeout {
		return errors.New("commit timeout")
	}
	if !m.commitOK {
		return errors.New("commit failed")
	}
	return nil
}

// Rollback simulates the rollback phase.
func (m *MockService) Rollback(timeout time.Duration) error {
	m.rollbackCalled++
	time.Sleep(m.rollbackDelay)
	// Even if the delay causes timeout in coordinator, here we assume rollback always succeed.
	if m.rollbackDelay > timeout {
		return errors.New("rollback timeout")
	}
	return nil
}

// TestSuccessfulTransaction tests that a transaction commits successfully when all services prepare and commit without issues.
func TestSuccessfulTransaction(t *testing.T) {
	coordinatorTimeout := 100 * time.Millisecond
	coord := NewCoordinator(coordinatorTimeout)

	services := []Service{
		&MockService{"Inventory", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
		&MockService{"Payment", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
		&MockService{"Shipping", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
	}

	err := coord.ExecuteTransaction(services)
	if err != nil {
		t.Fatalf("Expected successful transaction but got error: %v", err)
	}

	// Optionally, verify that each service has been called appropriately.
	for _, s := range services {
		ms := s.(*MockService)
		if ms.prepareCalled != 1 {
			t.Errorf("Service %s: expected prepare call count 1, got %d", ms.id, ms.prepareCalled)
		}
		if ms.commitCalled != 1 {
			t.Errorf("Service %s: expected commit call count 1, got %d", ms.id, ms.commitCalled)
		}
		if ms.rollbackCalled != 0 {
			t.Errorf("Service %s: expected rollback call count 0, got %d", ms.id, ms.rollbackCalled)
		}
	}
}

// TestFailedTransaction tests that a transaction is rolled back if one service fails in the prepare phase.
func TestFailedTransaction(t *testing.T) {
	coordinatorTimeout := 100 * time.Millisecond
	coord := NewCoordinator(coordinatorTimeout)

	services := []Service{
		&MockService{"Inventory", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
		&MockService{"Payment", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, false, true, 0, 0, 0}, // This service will fail in prepare.
		&MockService{"Shipping", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
	}

	err := coord.ExecuteTransaction(services)
	if err == nil {
		t.Fatal("Expected transaction failure due to prepare error, but transaction succeeded")
	}

	// Verify that each service attempted prepare and then rollback was performed.
	for _, s := range services {
		ms := s.(*MockService)
		if ms.prepareCalled != 1 {
			t.Errorf("Service %s: expected prepare call count 1, got %d", ms.id, ms.prepareCalled)
		}
		// Commit should not be called if any prepare fails.
		if ms.commitCalled != 0 {
			t.Errorf("Service %s: expected commit call count 0, got %d", ms.id, ms.commitCalled)
		}
		// Rollback should be called for services that did prepare.
		if ms.rollbackCalled != 1 {
			t.Errorf("Service %s: expected rollback call count 1, got %d", ms.id, ms.rollbackCalled)
		}
	}
}

// TestTimeoutTransaction tests that a transaction times out in the prepare phase when a service takes too long.
func TestTimeoutTransaction(t *testing.T) {
	coordinatorTimeout := 50 * time.Millisecond
	coord := NewCoordinator(coordinatorTimeout)

	// One service has a prepare delay longer than the coordinator timeout.
	services := []Service{
		&MockService{"Inventory", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
		&MockService{"Payment", 100 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
		&MockService{"Shipping", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
	}

	err := coord.ExecuteTransaction(services)
	if err == nil {
		t.Fatal("Expected transaction failure due to timeout in prepare phase, but transaction succeeded")
	}

	// Even on timeout, all services that returned from prepare should attempt rollback.
	for _, s := range services {
		ms := s.(*MockService)
		if ms.prepareCalled != 1 {
			t.Errorf("Service %s: expected prepare call count 1, got %d", ms.id, ms.prepareCalled)
		}
		// Commit should not be called.
		if ms.commitCalled != 0 {
			t.Errorf("Service %s: expected commit call count 0, got %d", ms.id, ms.commitCalled)
		}
		// Rollback should be called.
		if ms.rollbackCalled != 1 {
			t.Errorf("Service %s: expected rollback call count 1, got %d", ms.id, ms.rollbackCalled)
		}
	}
}

// TestConcurrentTransactions tests the coordinator's ability to handle multiple transactions concurrently.
func TestConcurrentTransactions(t *testing.T) {
	coordinatorTimeout := 100 * time.Millisecond
	coord := NewCoordinator(coordinatorTimeout)

	transactionCount := 50
	var wg sync.WaitGroup
	errorCount := 0
	mu := sync.Mutex{}

	for i := 0; i < transactionCount; i++ {
		wg.Add(1)
		go func(txID int) {
			defer wg.Done()
			// Alternate between successful and failing transactions.
			var services []Service
			if txID%2 == 0 {
				// Successful transaction.
				services = []Service{
					&MockService{"Inventory", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
					&MockService{"Payment", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
					&MockService{"Shipping", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
				}
			} else {
				// Failing transaction.
				services = []Service{
					&MockService{"Inventory", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
					&MockService{"Payment", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, false, true, 0, 0, 0},
					&MockService{"Shipping", 10 * time.Millisecond, 10 * time.Millisecond, 10 * time.Millisecond, true, true, 0, 0, 0},
				}
			}
			err := coord.ExecuteTransaction(services)
			mu.Lock()
			if err != nil && txID%2 == 0 {
				errorCount++
			}
			if err == nil && txID%2 != 0 {
				errorCount++
			}
			mu.Unlock()
		}(i)
	}
	wg.Wait()
	if errorCount != 0 {
		t.Errorf("Concurrent transaction test encountered %d unexpected outcomes", errorCount)
	}
}