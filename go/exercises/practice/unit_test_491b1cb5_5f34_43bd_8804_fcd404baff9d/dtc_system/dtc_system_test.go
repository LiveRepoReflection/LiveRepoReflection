package dtc_system

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

// newFakeService returns an httptest.Server simulating a service with configurable behavior.
// All endpoints (/prepare, /commit, /rollback) will respond with the specified HTTP status code.
// If delay is non-zero, the response is delayed by the given duration.
func newFakeService(prepareStatus, commitStatus, rollbackStatus int, delay time.Duration) *httptest.Server {
	mux := http.NewServeMux()
	mux.HandleFunc("/prepare", func(w http.ResponseWriter, r *http.Request) {
		if delay > 0 {
			time.Sleep(delay)
		}
		w.WriteHeader(prepareStatus)
	})
	mux.HandleFunc("/commit", func(w http.ResponseWriter, r *http.Request) {
		if delay > 0 {
			time.Sleep(delay)
		}
		w.WriteHeader(commitStatus)
	})
	mux.HandleFunc("/rollback", func(w http.ResponseWriter, r *http.Request) {
		if delay > 0 {
			time.Sleep(delay)
		}
		w.WriteHeader(rollbackStatus)
	})
	return httptest.NewServer(mux)
}

// TestSuccessfulTransaction tests that a transaction commits successfully when all services respond with success.
func TestSuccessfulTransaction(t *testing.T) {
	// Create three fake services that always succeed (HTTP 200) with no delay.
	service1 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service1.Close()
	service2 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service2.Close()
	service3 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service3.Close()

	// Create a coordinator with a reasonable timeout.
	coordinator := NewCoordinator(500 * time.Millisecond)

	// Register services with coordinator.
	services := map[string]string{
		"inventory": service1.URL,
		"payment":   service2.URL,
		"shipping":  service3.URL,
	}
	for name, url := range services {
		if err := coordinator.RegisterService(name, url); err != nil {
			t.Fatalf("failed to register service %s: %v", name, err)
		}
	}

	// Begin a transaction with all registered services.
	txID := "tx_success"
	serviceNames := []string{"inventory", "payment", "shipping"}
	if err := coordinator.BeginTransaction(txID, serviceNames); err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	// Allow some time for the transaction to complete.
	status := coordinator.GetTransactionStatus(txID)
	if status != "COMMITTED" {
		t.Fatalf("expected transaction status COMMITTED, got %s", status)
	}
}

// TestFailedPrepare tests that a transaction rolls back if one of the services fails during the prepare phase.
func TestFailedPrepare(t *testing.T) {
	// Create two good services and one service that fails prepare.
	service1 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service1.Close()
	service2 := newFakeService(http.StatusInternalServerError, http.StatusOK, http.StatusOK, 0)
	defer service2.Close()
	service3 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service3.Close()

	coordinator := NewCoordinator(500 * time.Millisecond)
	services := map[string]string{
		"inventory": service1.URL,
		"payment":   service2.URL,
		"shipping":  service3.URL,
	}
	for name, url := range services {
		if err := coordinator.RegisterService(name, url); err != nil {
			t.Fatalf("failed to register service %s: %v", name, err)
		}
	}

	txID := "tx_failed_prepare"
	serviceNames := []string{"inventory", "payment", "shipping"}
	if err := coordinator.BeginTransaction(txID, serviceNames); err == nil {
		t.Fatalf("expected BeginTransaction to fail due to prepare error, but it succeeded")
	}

	status := coordinator.GetTransactionStatus(txID)
	if status != "ROLLEDBACK" {
		t.Fatalf("expected transaction status ROLLEDBACK, got %s", status)
	}
}

// TestTimeout tests that a transaction is rolled back if a service does not respond within the timeout period.
func TestTimeout(t *testing.T) {
	// Create one service that delays beyond the coordinator timeout.
	service1 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service1.Close()
	// Service with delay: using 1 second delay will exceed our coordinator timeout.
	service2 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 1*time.Second)
	defer service2.Close()
	service3 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service3.Close()

	// Set coordinator timeout to 300 milliseconds.
	coordinator := NewCoordinator(300 * time.Millisecond)
	services := map[string]string{
		"inventory": service1.URL,
		"payment":   service2.URL,
		"shipping":  service3.URL,
	}
	for name, url := range services {
		if err := coordinator.RegisterService(name, url); err != nil {
			t.Fatalf("failed to register service %s: %v", name, err)
		}
	}

	txID := "tx_timeout"
	serviceNames := []string{"inventory", "payment", "shipping"}
	if err := coordinator.BeginTransaction(txID, serviceNames); err == nil {
		t.Fatalf("expected BeginTransaction to fail due to timeout, but it succeeded")
	}

	status := coordinator.GetTransactionStatus(txID)
	if status != "ROLLEDBACK" {
		t.Fatalf("expected transaction status ROLLEDBACK because of timeout, got %s", status)
	}
}

// TestCommitFailure tests that a transaction is rolled back if one of the services fails during the commit phase.
func TestCommitFailure(t *testing.T) {
	// All services succeed in prepare, but one fails in commit.
	service1 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service1.Close()
	service2 := newFakeService(http.StatusOK, http.StatusInternalServerError, http.StatusOK, 0)
	defer service2.Close()
	service3 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service3.Close()

	coordinator := NewCoordinator(500 * time.Millisecond)
	services := map[string]string{
		"inventory": service1.URL,
		"payment":   service2.URL,
		"shipping":  service3.URL,
	}
	for name, url := range services {
		if err := coordinator.RegisterService(name, url); err != nil {
			t.Fatalf("failed to register service %s: %v", name, err)
		}
	}

	txID := "tx_failed_commit"
	serviceNames := []string{"inventory", "payment", "shipping"}
	if err := coordinator.BeginTransaction(txID, serviceNames); err == nil {
		t.Fatalf("expected BeginTransaction to fail due to commit error, but it succeeded")
	}

	status := coordinator.GetTransactionStatus(txID)
	if status != "ROLLEDBACK" {
		t.Fatalf("expected transaction status ROLLEDBACK due to commit failure, got %s", status)
	}
}

// TestConcurrentTransactions tests multiple transactions concurrently to ensure concurrency safety.
func TestConcurrentTransactions(t *testing.T) {
	coordinator := NewCoordinator(500 * time.Millisecond)

	// Create a common set of good services.
	service1 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service1.Close()
	service2 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service2.Close()
	service3 := newFakeService(http.StatusOK, http.StatusOK, http.StatusOK, 0)
	defer service3.Close()

	services := map[string]string{
		"inventory": service1.URL,
		"payment":   service2.URL,
		"shipping":  service3.URL,
	}
	for name, url := range services {
		if err := coordinator.RegisterService(name, url); err != nil {
			t.Fatalf("failed to register service %s: %v", name, err)
		}
	}

	// Launch multiple transactions concurrently.
	var wg sync.WaitGroup
	txCount := 10
	for i := 0; i < txCount; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			txID := fmt.Sprintf("tx_concurrent_%d", i)
			serviceNames := []string{"inventory", "payment", "shipping"}
			err := coordinator.BeginTransaction(txID, serviceNames)
			// For concurrent tests, any error indicates a failed transaction.
			// We then check that the status is consistently ROLLEDBACK.
			status := coordinator.GetTransactionStatus(txID)
			if err != nil && status != "ROLLEDBACK" {
				t.Errorf("transaction %s expected to be ROLLEDBACK, got %s", txID, status)
			}
			if err == nil && status != "COMMITTED" {
				t.Errorf("transaction %s expected to be COMMITTED, got %s", txID, status)
			}
		}(i)
	}
	wg.Wait()
}