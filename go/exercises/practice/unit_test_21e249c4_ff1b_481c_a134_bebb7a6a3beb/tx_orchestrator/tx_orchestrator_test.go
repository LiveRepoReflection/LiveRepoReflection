package tx_orchestrator_test

import (
	"fmt"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"tx_orchestrator"
)

func createTestServer(prepareSuccess bool, delay time.Duration) *httptest.Server {
	handler := http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		// Simulate network latency
		time.Sleep(delay)
		switch r.URL.Path {
		case "/prepare":
			if prepareSuccess {
				w.WriteHeader(http.StatusOK)
				fmt.Fprint(w, "prepare OK")
			} else {
				w.WriteHeader(http.StatusInternalServerError)
				fmt.Fprint(w, "prepare failed")
			}
		case "/commit":
			w.WriteHeader(http.StatusOK)
			fmt.Fprint(w, "commit OK")
		case "/rollback":
			w.WriteHeader(http.StatusOK)
			fmt.Fprint(w, "rollback OK")
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	})
	return httptest.NewServer(handler)
}

func TestOrchestrateTransactionSuccess(t *testing.T) {
	// Test where all services succeed on prepare.
	numServices := 5
	servers := make([]*httptest.Server, numServices)
	endpoints := make([]string, numServices)
	for i := 0; i < numServices; i++ {
		servers[i] = createTestServer(true, 10*time.Millisecond)
		endpoints[i] = servers[i].URL
	}
	defer func() {
		for _, s := range servers {
			s.Close()
		}
	}()

	transactionID := "test-success"
	result := tx_orchestrator.OrchestrateTransaction(transactionID, endpoints)
	if !result {
		t.Errorf("Expected transaction to commit successfully, but got rollback")
	}
}

func TestOrchestrateTransactionFailure(t *testing.T) {
	// Test where one service fails on prepare causing rollback.
	numServices := 5
	servers := make([]*httptest.Server, numServices)
	endpoints := make([]string, numServices)
	for i := 0; i < numServices; i++ {
		// For the 3rd service, simulate failure.
		if i == 2 {
			servers[i] = createTestServer(false, 10*time.Millisecond)
		} else {
			servers[i] = createTestServer(true, 10*time.Millisecond)
		}
		endpoints[i] = servers[i].URL
	}
	defer func() {
		for _, s := range servers {
			s.Close()
		}
	}()

	transactionID := "test-failure"
	result := tx_orchestrator.OrchestrateTransaction(transactionID, endpoints)
	if result {
		t.Errorf("Expected transaction to rollback due to prepare failure, but got commit")
	}
}

func TestOrchestrateTransactionWithDelays(t *testing.T) {
	// Test with variable network latency on each service.
	numServices := 5
	servers := make([]*httptest.Server, numServices)
	endpoints := make([]string, numServices)
	delays := []time.Duration{
		10 * time.Millisecond,
		50 * time.Millisecond,
		100 * time.Millisecond,
		20 * time.Millisecond,
		30 * time.Millisecond,
	}
	for i := 0; i < numServices; i++ {
		servers[i] = createTestServer(true, delays[i])
		endpoints[i] = servers[i].URL
	}
	defer func() {
		for _, s := range servers {
			s.Close()
		}
	}()

	transactionID := "test-delay"
	result := tx_orchestrator.OrchestrateTransaction(transactionID, endpoints)
	if !result {
		t.Errorf("Expected transaction to commit successfully with delays, but got rollback")
	}
}

func TestOrchestrateTransactionRetryLogic(t *testing.T) {
	// Test scenario where initial prepare attempts fail but succeed on retry.
	var mu sync.Mutex
	callCount := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(10 * time.Millisecond)
		mu.Lock()
		callCount++
		currentCall := callCount
		mu.Unlock()
		switch r.URL.Path {
		case "/prepare":
			if currentCall <= 2 {
				w.WriteHeader(http.StatusInternalServerError)
				fmt.Fprint(w, "prepare failed")
			} else {
				w.WriteHeader(http.StatusOK)
				fmt.Fprint(w, "prepare OK")
			}
		case "/commit":
			w.WriteHeader(http.StatusOK)
			fmt.Fprint(w, "commit OK")
		case "/rollback":
			w.WriteHeader(http.StatusOK)
			fmt.Fprint(w, "rollback OK")
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer server.Close()

	endpoints := []string{server.URL}
	transactionID := "test-retry"
	result := tx_orchestrator.OrchestrateTransaction(transactionID, endpoints)
	if !result {
		t.Errorf("Expected transaction to commit successfully after retries, but got rollback")
	}
}

func TestOrchestrateTransactionCommitFailureHandling(t *testing.T) {
	// Test scenario where commit initially fails but recovers after retries.
	var mu sync.Mutex
	commitCallCount := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(10 * time.Millisecond)
		switch r.URL.Path {
		case "/prepare":
			w.WriteHeader(http.StatusOK)
			fmt.Fprint(w, "prepare OK")
		case "/commit":
			mu.Lock()
			commitCallCount++
			current := commitCallCount
			mu.Unlock()
			if current == 1 {
				w.WriteHeader(http.StatusInternalServerError)
				fmt.Fprint(w, "commit failed")
			} else {
				w.WriteHeader(http.StatusOK)
				fmt.Fprint(w, "commit OK")
			}
		case "/rollback":
			w.WriteHeader(http.StatusOK)
			fmt.Fprint(w, "rollback OK")
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer server.Close()

	endpoints := []string{server.URL}
	transactionID := "test-commit-failure"
	result := tx_orchestrator.OrchestrateTransaction(transactionID, endpoints)
	if !result {
		t.Errorf("Expected transaction to eventually commit despite commit failures, but got rollback")
	}
}

func TestOrchestrateTransactionRollbackFailureHandling(t *testing.T) {
	// Test scenario where prepare fails and rollback initially fails but recovers after retries.
	var mu sync.Mutex
	rollbackCallCount := 0
	server := httptest.NewServer(http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(10 * time.Millisecond)
		switch r.URL.Path {
		case "/prepare":
			w.WriteHeader(http.StatusInternalServerError)
			fmt.Fprint(w, "prepare failed")
		case "/commit":
			w.WriteHeader(http.StatusOK)
			fmt.Fprint(w, "commit OK")
		case "/rollback":
			mu.Lock()
			rollbackCallCount++
			current := rollbackCallCount
			mu.Unlock()
			if current == 1 {
				w.WriteHeader(http.StatusInternalServerError)
				fmt.Fprint(w, "rollback failed")
			} else {
				w.WriteHeader(http.StatusOK)
				fmt.Fprint(w, "rollback OK")
			}
		default:
			w.WriteHeader(http.StatusNotFound)
		}
	}))
	defer server.Close()

	endpoints := []string{server.URL}
	transactionID := "test-rollback-failure"
	result := tx_orchestrator.OrchestrateTransaction(transactionID, endpoints)
	if result {
		t.Errorf("Expected transaction to rollback due to prepare failure, but got commit")
	}
}