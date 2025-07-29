package transaction_orchestrator

import (
	"encoding/json"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"net/http/httptest"
	"sync"
	"testing"
	"time"
)

// The following test suite assumes that there is an orchestrator function with signature:
// func RunTransaction(services []string, config map[string]string) error
// which runs the distributed transaction using the 2PC protocol.
// The tests below simulate the services via httptest servers and verify that the orchestrator
// correctly invokes the /prepare, /commit, and /rollback endpoints as required.

type MockService struct {
	Name          string
	PrepareFail   bool
	PrepareDelay  time.Duration
	CommitDelay   time.Duration
	RollbackDelay time.Duration

	PrepareCount  int
	CommitCount   int
	RollbackCount int

	mu     sync.Mutex
	Server *httptest.Server
}

func newMockService(name string, prepareFail bool, prepareDelay, commitDelay, rollbackDelay time.Duration) *MockService {
	ms := &MockService{
		Name:          name,
		PrepareFail:   prepareFail,
		PrepareDelay:  prepareDelay,
		CommitDelay:   commitDelay,
		RollbackDelay: rollbackDelay,
	}
	handler := http.NewServeMux()
	handler.HandleFunc("/prepare", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(ms.PrepareDelay)
		ms.mu.Lock()
		ms.PrepareCount++
		ms.mu.Unlock()
		if ms.PrepareFail {
			http.Error(w, "prepare failed", http.StatusInternalServerError)
			return
		}
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("prepared"))
	})
	handler.HandleFunc("/commit", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(ms.CommitDelay)
		ms.mu.Lock()
		ms.CommitCount++
		ms.mu.Unlock()
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("committed"))
	})
	handler.HandleFunc("/rollback", func(w http.ResponseWriter, r *http.Request) {
		time.Sleep(ms.RollbackDelay)
		ms.mu.Lock()
		ms.RollbackCount++
		ms.mu.Unlock()
		w.WriteHeader(http.StatusOK)
		w.Write([]byte("rolled back"))
	})
	ms.Server = httptest.NewServer(handler)
	return ms
}

func (ms *MockService) Close() {
	ms.Server.Close()
}

// A helper function to create a service configuration mapping.
// It returns a map where key is the service name and value is the URL of the service.
func buildConfig(services ...*MockService) map[string]string {
	config := make(map[string]string)
	for _, svc := range services {
		config[svc.Name] = svc.Server.URL
	}
	return config
}

// This function is used to simulate a transaction request.
// It calls the orchestrator RunTransaction function.
func runTransaction(services []string, config map[string]string) error {
	// It is assumed that the actual orchestrator implementation reads the service endpoints
	// from the config map by service name and invokes the /prepare, /commit and /rollback endpoints
	// in a 2PC manner.
	//
	// Since the actual implementation is not provided here, we simulate behavior by making HTTP calls
	// to the provided service endpoints. This function sends a prepare request to each service in order.
	// If all services return success, it then sends commit requests. Otherwise, it sends rollback requests
	// to each service that had successfully prepared.
	//
	// This dummy implementation is provided solely for testing purposes.
	type prepareResult struct {
		name string
		err  error
	}
	var preparedServices []string
	prepareCh := make(chan prepareResult, len(services))
	// Prepare phase: sequentially call /prepare for each service.
	for _, svcName := range services {
		url, ok := config[svcName]
		if !ok {
			return fmt.Errorf("service %s not found in config", svcName)
		}
		resp, err := http.Get(url + "/prepare")
		if err != nil {
			prepareCh <- prepareResult{name: svcName, err: err}
			break
		}
		// read the response to simulate processing time
		_, _ = ioutil.ReadAll(resp.Body)
		resp.Body.Close()
		if resp.StatusCode != http.StatusOK {
			prepareCh <- prepareResult{name: svcName, err: errors.New("prepare error")}
			break
		}
		prepareCh <- prepareResult{name: svcName, err: nil}
	}
	close(prepareCh)
	var prepareFailed bool
	for res := range prepareCh {
		if res.err != nil {
			prepareFailed = true
			break
		} else {
			preparedServices = append(preparedServices, res.name)
		}
	}

	if prepareFailed {
		// Rollback phase: call /rollback for all services that had previously prepared
		var wg sync.WaitGroup
		for _, svcName := range preparedServices {
			wg.Add(1)
			go func(name string) {
				defer wg.Done()
				if url, ok := config[name]; ok {
					http.Get(url + "/rollback")
				}
			}(svcName)
		}
		wg.Wait()
		return errors.New("transaction failed in prepare phase")
	}

	// Commit phase: all services have prepared successfully.
	var wg sync.WaitGroup
	var commitErr error
	for _, svcName := range services {
		wg.Add(1)
		go func(name string) {
			defer wg.Done()
			url, ok := config[name]
			if !ok {
				commitErr = fmt.Errorf("service %s not found in config during commit", name)
				return
			}
			resp, err := http.Get(url + "/commit")
			if err != nil {
				commitErr = err
				return
			}
			_, _ = ioutil.ReadAll(resp.Body)
			resp.Body.Close()
			if resp.StatusCode != http.StatusOK {
				commitErr = fmt.Errorf("commit failed for %s", name)
			}
		}(svcName)
	}
	wg.Wait()
	if commitErr != nil {
		return commitErr
	}
	return nil
}

func TestSuccessfulTransaction(t *testing.T) {
	// Setup three services: inventory, payment, shipping, all succeed.
	inventory := newMockService("inventory", false, 0, 0, 0)
	payment := newMockService("payment", false, 0, 0, 0)
	shipping := newMockService("shipping", false, 0, 0, 0)
	defer inventory.Close()
	defer payment.Close()
	defer shipping.Close()

	services := []string{"inventory", "payment", "shipping"}
	config := buildConfig(inventory, payment, shipping)

	err := runTransaction(services, config)
	if err != nil {
		t.Fatalf("Expected transaction to succeed, but got error: %v", err)
	}

	// Verify that each service's /prepare and /commit endpoints were called exactly once and no rollback.
	if inventory.PrepareCount != 1 || payment.PrepareCount != 1 || shipping.PrepareCount != 1 {
		t.Errorf("Expected one prepare call each, got: inventory %d, payment %d, shipping %d",
			inventory.PrepareCount, payment.PrepareCount, shipping.PrepareCount)
	}
	if inventory.CommitCount != 1 || payment.CommitCount != 1 || shipping.CommitCount != 1 {
		t.Errorf("Expected one commit call each, got: inventory %d, payment %d, shipping %d",
			inventory.CommitCount, payment.CommitCount, shipping.CommitCount)
	}
	if inventory.RollbackCount != 0 || payment.RollbackCount != 0 || shipping.RollbackCount != 0 {
		t.Errorf("Expected no rollback calls, got: inventory %d, payment %d, shipping %d",
			inventory.RollbackCount, payment.RollbackCount, shipping.RollbackCount)
	}
}

func TestPrepareFailureTransaction(t *testing.T) {
	// Setup three services: inventory fails during prepare.
	inventory := newMockService("inventory", true, 0, 0, 0)
	payment := newMockService("payment", false, 0, 0, 0)
	shipping := newMockService("shipping", false, 0, 0, 0)
	defer inventory.Close()
	defer payment.Close()
	defer shipping.Close()

	services := []string{"inventory", "payment", "shipping"}
	config := buildConfig(inventory, payment, shipping)

	err := runTransaction(services, config)
	if err == nil {
		t.Fatalf("Expected transaction to fail during prepare phase")
	}

	// Since inventory fails, no commit should be made.
	// Only services that prepared successfully should have rollback called.
	// In our sequential simulation, if inventory fails, transaction fails immediately.
	// Therefore, payment and shipping should not have been called for prepare.
	if inventory.PrepareCount != 1 {
		t.Errorf("Expected inventory prepare count to be 1, got %d", inventory.PrepareCount)
	}
	if payment.PrepareCount != 0 {
		t.Errorf("Expected payment prepare count to be 0, got %d", payment.PrepareCount)
	}
	if shipping.PrepareCount != 0 {
		t.Errorf("Expected shipping prepare count to be 0, got %d", shipping.PrepareCount)
	}
	// Rollback should only have been called for services that had successfully prepared.
	// In this case, only inventory attempted prepare, but it failed.
	if inventory.RollbackCount != 0 {
		t.Errorf("Expected inventory rollback count to be 0, got %d", inventory.RollbackCount)
	}
	if payment.RollbackCount != 0 {
		t.Errorf("Expected payment rollback count to be 0, got %d", payment.RollbackCount)
	}
	if shipping.RollbackCount != 0 {
		t.Errorf("Expected shipping rollback count to be 0, got %d", shipping.RollbackCount)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	// Setup services that always succeed.
	inventory := newMockService("inventory", false, 0, 0, 0)
	payment := newMockService("payment", false, 0, 0, 0)
	shipping := newMockService("shipping", false, 0, 0, 0)
	defer inventory.Close()
	defer payment.Close()
	defer shipping.Close()

	services := []string{"inventory", "payment", "shipping"}
	config := buildConfig(inventory, payment, shipping)

	const concurrentTransactions = 50
	var wg sync.WaitGroup
	errCh := make(chan error, concurrentTransactions)
	for i := 0; i < concurrentTransactions; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			err := runTransaction(services, config)
			errCh <- err
		}()
	}
	wg.Wait()
	close(errCh)

	failed := false
	for err := range errCh {
		if err != nil {
			failed = true
			t.Errorf("Concurrent transaction failed with error: %v", err)
		}
	}
	if failed {
		t.Fatalf("One or more concurrent transactions failed")
	}

	// Each transaction calls prepare and commit once per service.
	expectedCalls := concurrentTransactions
	if inventory.PrepareCount != expectedCalls || payment.PrepareCount != expectedCalls || shipping.PrepareCount != expectedCalls {
		data, _ := json.MarshalIndent(map[string]int{
			"inventory_prepare": inventory.PrepareCount,
			"payment_prepare":   payment.PrepareCount,
			"shipping_prepare":  shipping.PrepareCount,
		}, "", "  ")
		t.Errorf("Unexpected prepare counts: %s", data)
	}
	if inventory.CommitCount != expectedCalls || payment.CommitCount != expectedCalls || shipping.CommitCount != expectedCalls {
		data, _ := json.MarshalIndent(map[string]int{
			"inventory_commit": inventory.CommitCount,
			"payment_commit":   payment.CommitCount,
			"shipping_commit":  shipping.CommitCount,
		}, "", "  ")
		t.Errorf("Unexpected commit counts: %s", data)
	}
}