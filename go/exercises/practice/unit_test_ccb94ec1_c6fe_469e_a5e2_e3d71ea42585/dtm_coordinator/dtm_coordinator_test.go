package dtm_coordinator_test

import (
	"errors"
	"sync"
	"testing"
	"time"

	"dtm_coordinator"
)

func TestBeginTransaction(t *testing.T) {
	coord := dtm_coordinator.NewCoordinator()
	tx, err := coord.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}
	if tx.Status != "pending" {
		t.Fatalf("Expected transaction status 'pending', got: %s", tx.Status)
	}
}

func TestRegisterService(t *testing.T) {
	coord := dtm_coordinator.NewCoordinator()
	tx, err := coord.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = coord.RegisterService(tx.ID, "serviceA")
	if err != nil {
		t.Fatalf("RegisterService failed: %v", err)
	}

	status, err := coord.GetTransactionStatus(tx.ID)
	if err != nil {
		t.Fatalf("GetTransactionStatus failed: %v", err)
	}
	if status != "pending" {
		t.Errorf("Expected status 'pending' after registration, got: %s", status)
	}
}

func TestCommitTransaction(t *testing.T) {
	coord := dtm_coordinator.NewCoordinator()
	tx, err := coord.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	services := []string{"serviceA", "serviceB", "serviceC"}
	for _, s := range services {
		err = coord.RegisterService(tx.ID, s)
		if err != nil {
			t.Fatalf("RegisterService for %s failed: %v", s, err)
		}
	}

	// Simulate commit confirmation for all services.
	for _, s := range services {
		coord.SimulateServiceCommit(tx.ID, s)
	}

	err = coord.CommitTransaction(tx.ID)
	if err != nil {
		t.Fatalf("CommitTransaction failed: %v", err)
	}

	status, err := coord.GetTransactionStatus(tx.ID)
	if err != nil {
		t.Fatalf("GetTransactionStatus failed: %v", err)
	}
	if status != "committed" {
		t.Errorf("Expected transaction 'committed', got: %s", status)
	}
}

func TestRollbackTransaction(t *testing.T) {
	coord := dtm_coordinator.NewCoordinator()
	tx, err := coord.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	services := []string{"serviceA", "serviceB"}
	for _, s := range services {
		err = coord.RegisterService(tx.ID, s)
		if err != nil {
			t.Fatalf("RegisterService for %s failed: %v", s, err)
		}
	}

	// Simulate that only serviceA confirms the commit.
	coord.SimulateServiceCommit(tx.ID, "serviceA")
	// Commit should timeout due to missing confirmation from serviceB and trigger a rollback.
	err = coord.CommitTransaction(tx.ID)
	if err == nil {
		t.Errorf("Expected CommitTransaction to fail due to timeout, got nil error")
	}

	status, err := coord.GetTransactionStatus(tx.ID)
	if err != nil {
		t.Fatalf("GetTransactionStatus failed: %v", err)
	}
	if status != "rolledback" {
		t.Errorf("Expected transaction 'rolledback', got: %s", status)
	}
}

func TestIdempotentCommitRollback(t *testing.T) {
	coord := dtm_coordinator.NewCoordinator()
	tx, err := coord.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = coord.RegisterService(tx.ID, "serviceA")
	if err != nil {
		t.Fatalf("RegisterService failed: %v", err)
	}

	coord.SimulateServiceCommit(tx.ID, "serviceA")
	err = coord.CommitTransaction(tx.ID)
	if err != nil {
		t.Fatalf("First CommitTransaction failed: %v", err)
	}

	// Second commit should be idempotent.
	err = coord.CommitTransaction(tx.ID)
	if err != nil {
		t.Fatalf("Second CommitTransaction failed (idempotency): %v", err)
	}

	// Attempt to rollback a committed transaction should either be idempotent or return a graceful error.
	err = coord.RollbackTransaction(tx.ID)
	if err != nil {
		// Accept error if rollback is not allowed once committed.
	}

	status, err := coord.GetTransactionStatus(tx.ID)
	if err != nil {
		t.Fatalf("GetTransactionStatus failed: %v", err)
	}
	if status != "committed" {
		t.Errorf("Expected transaction to remain 'committed', got: %s", status)
	}
}

func TestTimeoutHandling(t *testing.T) {
	coord := dtm_coordinator.NewCoordinator()
	// Set a short timeout for testing purposes.
	coord.SetTimeout(2 * time.Second)

	tx, err := coord.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = coord.RegisterService(tx.ID, "slowService")
	if err != nil {
		t.Fatalf("RegisterService failed: %v", err)
	}

	start := time.Now()
	err = coord.CommitTransaction(tx.ID)
	duration := time.Since(start)

	if err == nil {
		t.Fatalf("Expected CommitTransaction to fail due to timeout, but it succeeded")
	}
	if duration < 2*time.Second {
		t.Errorf("CommitTransaction returned before timeout period: %v", duration)
	}

	status, err := coord.GetTransactionStatus(tx.ID)
	if err != nil {
		t.Fatalf("GetTransactionStatus failed: %v", err)
	}
	if status != "rolledback" {
		t.Errorf("Expected transaction 'rolledback' due to timeout, got: %s", status)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	coord := dtm_coordinator.NewCoordinator()
	var wg sync.WaitGroup
	numTransactions := 10

	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			tx, err := coord.BeginTransaction()
			if err != nil {
				t.Errorf("BeginTransaction failed: %v", err)
				return
			}
			services := []string{"serviceA", "serviceB", "serviceC"}
			for _, s := range services {
				err = coord.RegisterService(tx.ID, s)
				if err != nil {
					t.Errorf("RegisterService for %s failed: %v", s, err)
					return
				}
				coord.SimulateServiceCommit(tx.ID, s)
			}
			err = coord.CommitTransaction(tx.ID)
			if err != nil {
				t.Errorf("CommitTransaction failed: %v", err)
				return
			}
			status, err := coord.GetTransactionStatus(tx.ID)
			if err != nil {
				t.Errorf("GetTransactionStatus failed: %v", err)
				return
			}
			if status != "committed" {
				t.Errorf("Expected 'committed', got %s", status)
			}
		}()
	}

	wg.Wait()
}

func TestServiceFailureDuringCommit(t *testing.T) {
	coord := dtm_coordinator.NewCoordinator()
	tx, err := coord.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	services := []string{"serviceA", "serviceB"}
	for _, s := range services {
		err = coord.RegisterService(tx.ID, s)
		if err != nil {
			t.Fatalf("RegisterService for %s failed: %v", s, err)
		}
	}

	// Simulate commit confirmation for serviceA only.
	coord.SimulateServiceCommit(tx.ID, "serviceA")
	// Simulate a failure for serviceB during commit.
	coord.SimulateServiceFailure(tx.ID, "serviceB", errors.New("commit failure"))

	err = coord.CommitTransaction(tx.ID)
	if err == nil {
		t.Fatalf("Expected CommitTransaction to fail due to service failure, but it succeeded")
	}

	status, err := coord.GetTransactionStatus(tx.ID)
	if err != nil {
		t.Fatalf("GetTransactionStatus failed: %v", err)
	}
	if status != "rolledback" {
		t.Errorf("Expected transaction to be 'rolledback' after service failure, got: %s", status)
	}
}