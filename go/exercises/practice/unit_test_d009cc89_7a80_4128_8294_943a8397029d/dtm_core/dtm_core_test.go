package dtm_core_test

import (
	"encoding/json"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"

	"dtm_core"
)

type serviceHandler struct {
	prepareResponse  string
	commitResponse   string
	rollbackResponse string
	delay            time.Duration
}

func (s *serviceHandler) ServeHTTP(w http.ResponseWriter, r *http.Request) {
	if s.delay > 0 {
		time.Sleep(s.delay)
	}
	var resp map[string]string
	switch r.URL.Path {
	case "/prepare":
		resp = map[string]string{"status": s.prepareResponse}
	case "/commit":
		resp = map[string]string{"status": s.commitResponse}
	case "/rollback":
		resp = map[string]string{"status": s.rollbackResponse}
	default:
		http.NotFound(w, r)
		return
	}
	w.Header().Set("Content-Type", "application/json")
	json.NewEncoder(w).Encode(resp)
}

func TestSuccessfulTransaction(t *testing.T) {
	// All services return commit in the prepare phase.
	handler := &serviceHandler{
		prepareResponse:  "commit",
		commitResponse:   "commit",
		rollbackResponse: "rollback",
	}
	s1 := httptest.NewServer(handler)
	defer s1.Close()
	s2 := httptest.NewServer(handler)
	defer s2.Close()
	s3 := httptest.NewServer(handler)
	defer s3.Close()

	services := []string{s1.URL, s2.URL, s3.URL}
	err := dtm_core.ExecuteTransaction(services, 2*time.Second)
	if err != nil {
		t.Errorf("Expected successful transaction, got error: %v", err)
	}
}

func TestFailedTransaction(t *testing.T) {
	// One service votes rollback during prepare phase.
	handlerCommit := &serviceHandler{
		prepareResponse:  "commit",
		commitResponse:   "commit",
		rollbackResponse: "rollback",
	}
	handlerRollback := &serviceHandler{
		prepareResponse:  "rollback",
		commitResponse:   "commit",
		rollbackResponse: "rollback",
	}
	s1 := httptest.NewServer(handlerCommit)
	defer s1.Close()
	s2 := httptest.NewServer(handlerRollback)
	defer s2.Close()
	s3 := httptest.NewServer(handlerCommit)
	defer s3.Close()

	services := []string{s1.URL, s2.URL, s3.URL}
	err := dtm_core.ExecuteTransaction(services, 2*time.Second)
	if err == nil {
		t.Errorf("Expected transaction failure due to a rollback vote, but got success")
	}
}

func TestTimeoutTransaction(t *testing.T) {
	// One service delays its response beyond the timeout threshold.
	handlerFast := &serviceHandler{
		prepareResponse:  "commit",
		commitResponse:   "commit",
		rollbackResponse: "rollback",
		delay:            0,
	}
	handlerSlow := &serviceHandler{
		prepareResponse:  "commit",
		commitResponse:   "commit",
		rollbackResponse: "rollback",
		delay:            3 * time.Second,
	}
	s1 := httptest.NewServer(handlerFast)
	defer s1.Close()
	s2 := httptest.NewServer(handlerSlow)
	defer s2.Close()

	services := []string{s1.URL, s2.URL}
	err := dtm_core.ExecuteTransaction(services, 1*time.Second)
	if err == nil {
		t.Errorf("Expected timeout error due to slow response, but got success")
	}
}

func TestConcurrentTransactions(t *testing.T) {
	// Execute multiple transactions concurrently.
	handler := &serviceHandler{
		prepareResponse:  "commit",
		commitResponse:   "commit",
		rollbackResponse: "rollback",
	}
	s1 := httptest.NewServer(handler)
	defer s1.Close()
	s2 := httptest.NewServer(handler)
	defer s2.Close()
	s3 := httptest.NewServer(handler)
	defer s3.Close()

	services := []string{s1.URL, s2.URL, s3.URL}
	var wg sync.WaitGroup
	txnCount := 10

	for i := 0; i < txnCount; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			err := dtm_core.ExecuteTransaction(services, 2*time.Second)
			if err != nil {
				t.Errorf("Concurrent transaction failed: %v", err)
			}
		}()
	}
	wg.Wait()
}

func TestIdempotency(t *testing.T) {
	// Execute the same transaction multiple times to verify idempotency.
	handler := &serviceHandler{
		prepareResponse:  "commit",
		commitResponse:   "commit",
		rollbackResponse: "rollback",
	}
	s1 := httptest.NewServer(handler)
	defer s1.Close()
	s2 := httptest.NewServer(handler)
	defer s2.Close()

	services := []string{s1.URL, s2.URL}

	// First execution
	err1 := dtm_core.ExecuteTransaction(services, 2*time.Second)
	// Second execution, simulating the repeated processing of the same transaction.
	err2 := dtm_core.ExecuteTransaction(services, 2*time.Second)

	if err1 != nil || err2 != nil {
		t.Errorf("Expected idempotent transactions to succeed, got errors: err1=%v, err2=%v", err1, err2)
	}
}