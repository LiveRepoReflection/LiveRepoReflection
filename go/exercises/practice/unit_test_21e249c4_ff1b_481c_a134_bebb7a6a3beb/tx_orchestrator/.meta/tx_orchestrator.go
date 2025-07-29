package tx_orchestrator

import (
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"net/http"
	"sync"
	"time"
)

const maxRetries = 3
const initialBackoff = 10 * time.Millisecond

// callWithRetry makes a POST request with the given transactionID to endpoint+path.
// It retries the request up to maxRetries times with exponential backoff in case of error or non-200 responses.
func callWithRetry(endpoint, path, transactionID string) error {
	url := endpoint + path
	backoff := initialBackoff

	for attempt := 0; attempt < maxRetries; attempt++ {
		req, err := http.NewRequest("POST", url, bytes.NewBuffer([]byte(transactionID)))
		if err != nil {
			return err
		}
		req.Header.Set("Content-Type", "text/plain")

		client := http.Client{
			Timeout: 200 * time.Millisecond,
		}
		resp, err := client.Do(req)
		if err != nil {
			time.Sleep(backoff)
			backoff *= 2
			continue
		}
		body, _ := ioutil.ReadAll(resp.Body)
		resp.Body.Close()

		if resp.StatusCode == http.StatusOK {
			return nil
		}

		err = fmt.Errorf("unexpected status: %d, body: %s", resp.StatusCode, string(body))
		time.Sleep(backoff)
		backoff *= 2
	}
	return fmt.Errorf("failed after %d retries for %s", maxRetries, url)
}

// orchestratePhase concurrently calls the given path for all endpoints with retries.
// It returns a map from endpoint URL to any error encountered during the call.
func orchestratePhase(endpoints []string, path, transactionID string) map[string]error {
	results := make(map[string]error)
	var mu sync.Mutex
	var wg sync.WaitGroup

	for _, endpoint := range endpoints {
		wg.Add(1)
		go func(ep string) {
			defer wg.Done()
			err := callWithRetry(ep, path, transactionID)
			mu.Lock()
			results[ep] = err
			mu.Unlock()
		}(endpoint)
	}
	wg.Wait()
	return results
}

// OrchestrateTransaction initiates a distributed transaction across the provided service endpoints.
// It follows a two-phase approach: (1) sending /prepare to all services concurrently,
// and if all succeed, (2) sending /commit to all services concurrently.
// In case any prepare fails, it triggers a rollback by calling /rollback on all endpoints concurrently.
// The function returns true if the transaction is committed and false if it is rolled back.
func OrchestrateTransaction(transactionID string, serviceEndpoints []string) bool {
	// Phase 1: Prepare
	prepareResults := orchestratePhase(serviceEndpoints, "/prepare", transactionID)
	prepareFailed := false
	for ep, err := range prepareResults {
		if err != nil {
			log.Printf("Prepare failed for service %s: %v", ep, err)
			prepareFailed = true
		} else {
			log.Printf("Prepare succeeded for service %s", ep)
		}
	}
	if prepareFailed {
		// Rollback phase
		rollbackResults := orchestratePhase(serviceEndpoints, "/rollback", transactionID)
		for ep, err := range rollbackResults {
			if err != nil {
				log.Printf("Rollback failed for service %s: %v", ep, err)
			} else {
				log.Printf("Rollback succeeded for service %s", ep)
			}
		}
		return false
	}

	// Phase 2: Commit
	commitResults := orchestratePhase(serviceEndpoints, "/commit", transactionID)
	for ep, err := range commitResults {
		if err != nil {
			log.Printf("Commit failed for service %s: %v", ep, err)
		} else {
			log.Printf("Commit succeeded for service %s", ep)
		}
	}
	return true
}