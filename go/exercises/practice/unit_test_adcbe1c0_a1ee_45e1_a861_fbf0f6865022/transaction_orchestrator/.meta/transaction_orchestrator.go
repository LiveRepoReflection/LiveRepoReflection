package transaction_orchestrator

import (
	"fmt"
	"io/ioutil"
	"net/http"
	"sync"
	"time"
)

// RunTransaction coordinates a distributed transaction using a simplified two-phase commit protocol.
// It takes a slice of service names and a configuration mapping each service to its endpoint URL.
// The function returns an error if the transaction fails in either the prepare or commit phases.
func RunTransaction(services []string, config map[string]string) error {
	var prepared []string

	// Prepare Phase: sequentially invoke the /prepare endpoint for each service.
	for _, svc := range services {
		url, ok := config[svc]
		if !ok {
			return fmt.Errorf("service %s not found in config", svc)
		}
		if err := doRequestWithRetry(url+"/prepare"); err != nil {
			rollback(prepared, config)
			return fmt.Errorf("prepare failed for service %s: %v", svc, err)
		}
		prepared = append(prepared, svc)
	}

	// Commit Phase: concurrently invoke the /commit endpoint for each service.
	var wg sync.WaitGroup
	var commitErr error
	var mu sync.Mutex
	for _, svc := range services {
		wg.Add(1)
		go func(s string) {
			defer wg.Done()
			url := config[s]
			if err := doRequestWithRetry(url+"/commit"); err != nil {
				mu.Lock()
				commitErr = fmt.Errorf("commit failed for service %s: %v", s, err)
				mu.Unlock()
			}
		}(svc)
	}
	wg.Wait()
	if commitErr != nil {
		return commitErr
	}
	return nil
}

// rollback initiates the rollback process concurrently for all services that successfully prepared.
func rollback(prepared []string, config map[string]string) {
	var wg sync.WaitGroup
	for _, svc := range prepared {
		wg.Add(1)
		go func(s string) {
			defer wg.Done()
			if url, ok := config[s]; ok {
				// If rollback fails, we ignore the error since rollback is idempotent.
				_ = doRequestWithRetry(url + "/rollback")
			}
		}(svc)
	}
	wg.Wait()
}

// doRequest sends a GET request to the provided URL and verifies that the response status code is 200 OK.
func doRequest(url string) error {
	client := &http.Client{
		Timeout: 5 * time.Second,
	}
	resp, err := client.Get(url)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("received status code %d", resp.StatusCode)
	}
	_, err = ioutil.ReadAll(resp.Body)
	return err
}

// doRequestWithRetry attempts to send a GET request to the specified URL, retrying on failure
// with an exponential backoff strategy. It retries up to 3 times before returning an error.
func doRequestWithRetry(url string) error {
	maxRetries := 3
	backoff := 100 * time.Millisecond
	var lastErr error
	for i := 0; i < maxRetries; i++ {
		err := doRequest(url)
		if err == nil {
			return nil
		}
		lastErr = err
		time.Sleep(backoff)
		backoff *= 2
	}
	return fmt.Errorf("failed after retries: %v", lastErr)
}