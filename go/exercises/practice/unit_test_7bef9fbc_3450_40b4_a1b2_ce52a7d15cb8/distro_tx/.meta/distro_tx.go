package distrotx

import (
	"context"
	"errors"
	"fmt"
	"io"
	"log"
	"net/http"
	"sync"
	"time"
)

const (
	maxParticipants = 10
	maxRetries      = 3
	baseBackoff     = 100 * time.Millisecond
)

var (
	ErrTooManyParticipants = errors.New("exceeded maximum number of participants")
	ErrPrepareFailed       = errors.New("prepare phase failed")
	ErrCommitFailed        = errors.New("commit phase failed")
	ErrRollbackFailed      = errors.New("rollback phase failed")
)

type Participant struct {
	ServiceURL string
	Timeout    int // milliseconds
}

type TransactionCoordinator struct {
	participants []Participant
	mu          sync.RWMutex
	logger      *log.Logger
}

func NewTransactionCoordinator() *TransactionCoordinator {
	return &TransactionCoordinator{
		participants: make([]Participant, 0),
		logger:      log.Default(),
	}
}

func (tc *TransactionCoordinator) RegisterParticipant(p Participant) error {
	tc.mu.Lock()
	defer tc.mu.Unlock()

	if len(tc.participants) >= maxParticipants {
		return ErrTooManyParticipants
	}

	tc.participants = append(tc.participants, p)
	tc.logger.Printf("Registered participant: %s", p.ServiceURL)
	return nil
}

func (tc *TransactionCoordinator) Execute(ctx context.Context) error {
	tc.mu.RLock()
	participants := make([]Participant, len(tc.participants))
	copy(participants, tc.participants)
	tc.mu.RUnlock()

	// Phase 1: Prepare
	prepareResults := tc.prepare(ctx, participants)
	allPrepared := true
	for _, success := range prepareResults {
		if !success {
			allPrepared = false
			break
		}
	}

	// Phase 2: Commit or Rollback
	if allPrepared {
		tc.logger.Println("All participants prepared successfully, proceeding with commit")
		if err := tc.commit(ctx, participants); err != nil {
			tc.logger.Printf("Commit failed: %v", err)
			return ErrCommitFailed
		}
		return nil
	}

	tc.logger.Println("Some participants failed to prepare, initiating rollback")
	if err := tc.rollback(ctx, participants); err != nil {
		tc.logger.Printf("Rollback failed: %v", err)
		return ErrRollbackFailed
	}
	return ErrPrepareFailed
}

func (tc *TransactionCoordinator) prepare(ctx context.Context, participants []Participant) map[string]bool {
	results := make(map[string]bool)
	var wg sync.WaitGroup
	var mu sync.Mutex

	for _, p := range participants {
		wg.Add(1)
		go func(p Participant) {
			defer wg.Done()

			success := tc.executePrepare(ctx, p)
			mu.Lock()
			results[p.ServiceURL] = success
			mu.Unlock()
		}(p)
	}

	wg.Wait()
	return results
}

func (tc *TransactionCoordinator) commit(ctx context.Context, participants []Participant) error {
	var wg sync.WaitGroup
	errChan := make(chan error, len(participants))

	for _, p := range participants {
		wg.Add(1)
		go func(p Participant) {
			defer wg.Done()
			if err := tc.executeWithRetry(ctx, p, "commit"); err != nil {
				errChan <- fmt.Errorf("commit failed for %s: %v", p.ServiceURL, err)
			}
		}(p)
	}

	wg.Wait()
	close(errChan)

	// Collect all errors
	var errors []error
	for err := range errChan {
		errors = append(errors, err)
	}

	if len(errors) > 0 {
		return fmt.Errorf("commit errors: %v", errors)
	}
	return nil
}

func (tc *TransactionCoordinator) rollback(ctx context.Context, participants []Participant) error {
	var wg sync.WaitGroup
	errChan := make(chan error, len(participants))

	for _, p := range participants {
		wg.Add(1)
		go func(p Participant) {
			defer wg.Done()
			if err := tc.executeWithRetry(ctx, p, "rollback"); err != nil {
				errChan <- fmt.Errorf("rollback failed for %s: %v", p.ServiceURL, err)
			}
		}(p)
	}

	wg.Wait()
	close(errChan)

	// Collect all errors
	var errors []error
	for err := range errChan {
		errors = append(errors, err)
	}

	if len(errors) > 0 {
		return fmt.Errorf("rollback errors: %v", errors)
	}
	return nil
}

func (tc *TransactionCoordinator) executePrepare(ctx context.Context, p Participant) bool {
	timeout := time.Duration(p.Timeout) * time.Millisecond
	ctx, cancel := context.WithTimeout(ctx, timeout)
	defer cancel()

	req, err := http.NewRequestWithContext(ctx, "POST", p.ServiceURL+"/prepare", nil)
	if err != nil {
		tc.logger.Printf("Failed to create prepare request for %s: %v", p.ServiceURL, err)
		return false
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		tc.logger.Printf("Prepare request failed for %s: %v", p.ServiceURL, err)
		return false
	}
	defer resp.Body.Close()

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		tc.logger.Printf("Failed to read prepare response from %s: %v", p.ServiceURL, err)
		return false
	}

	return resp.StatusCode == http.StatusOK && string(body) == "ACK"
}

func (tc *TransactionCoordinator) executeWithRetry(ctx context.Context, p Participant, action string) error {
	var lastErr error
	for attempt := 0; attempt < maxRetries; attempt++ {
		if attempt > 0 {
			backoff := baseBackoff * time.Duration(1<<uint(attempt))
			time.Sleep(backoff)
		}

		timeout := time.Duration(p.Timeout) * time.Millisecond
		ctxWithTimeout, cancel := context.WithTimeout(ctx, timeout)
		err := tc.executeAction(ctxWithTimeout, p, action)
		cancel()

		if err == nil {
			return nil
		}
		lastErr = err
		tc.logger.Printf("Attempt %d failed for %s on %s: %v", attempt+1, action, p.ServiceURL, err)
	}
	return lastErr
}

func (tc *TransactionCoordinator) executeAction(ctx context.Context, p Participant, action string) error {
	req, err := http.NewRequestWithContext(ctx, "POST", p.ServiceURL+"/"+action, nil)
	if err != nil {
		return fmt.Errorf("failed to create request: %v", err)
	}

	resp, err := http.DefaultClient.Do(req)
	if err != nil {
		return fmt.Errorf("request failed: %v", err)
	}
	defer resp.Body.Close()

	if resp.StatusCode != http.StatusOK {
		return fmt.Errorf("received non-OK status code: %d", resp.StatusCode)
	}

	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return fmt.Errorf("failed to read response: %v", err)
	}

	if string(body) != "OK" && action != "prepare" {
		return fmt.Errorf("received unexpected response: %s", string(body))
	}

	return nil
}