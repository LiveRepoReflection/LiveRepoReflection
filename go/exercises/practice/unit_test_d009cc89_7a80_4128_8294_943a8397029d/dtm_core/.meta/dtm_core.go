package dtm_core

import (
	"context"
	"encoding/json"
	"errors"
	"net/http"
	"sync"
	"time"
)

type serviceResponse struct {
	Status string `json:"status"`
}

func callEndpoint(service string, endpoint string, timeout time.Duration) (string, error) {
	ctx, cancel := context.WithTimeout(context.Background(), timeout)
	defer cancel()
	url := service + "/" + endpoint
	req, err := http.NewRequestWithContext(ctx, "GET", url, nil)
	if err != nil {
		return "", err
	}
	client := http.Client{}
	resp, err := client.Do(req)
	if err != nil {
		return "", err
	}
	defer resp.Body.Close()

	var res serviceResponse
	if err := json.NewDecoder(resp.Body).Decode(&res); err != nil {
		return "", err
	}
	return res.Status, nil
}

func ExecuteTransaction(services []string, timeout time.Duration) error {
	type vote struct {
		service string
		status  string
		err     error
	}

	voteCh := make(chan vote, len(services))
	var wg sync.WaitGroup

	// Phase 1: Prepare Phase
	for _, service := range services {
		wg.Add(1)
		go func(svc string) {
			defer wg.Done()
			status, err := callEndpoint(svc, "prepare", timeout)
			voteCh <- vote{service: svc, status: status, err: err}
		}(service)
	}
	wg.Wait()
	close(voteCh)

	rollbackRequired := false
	for v := range voteCh {
		if v.err != nil || v.status != "commit" {
			rollbackRequired = true
			break
		}
	}

	// Phase 2: Commit or Rollback Phase based on prepare result
	phase := "commit"
	if rollbackRequired {
		phase = "rollback"
	}

	errCh := make(chan error, len(services))
	for _, service := range services {
		wg.Add(1)
		go func(svc string) {
			defer wg.Done()
			_, err := callEndpoint(svc, phase, timeout)
			errCh <- err
		}(service)
	}
	wg.Wait()
	close(errCh)

	var errorsOccurred []error
	for err := range errCh {
		if err != nil {
			errorsOccurred = append(errorsOccurred, err)
		}
	}

	if rollbackRequired {
		return errors.New("transaction rolled back due to prepare phase failure or timeout")
	}
	if len(errorsOccurred) > 0 {
		return errors.New("transaction commit failed in one or more services")
	}
	return nil
}