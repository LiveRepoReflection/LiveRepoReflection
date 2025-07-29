package txn_coord

import (
	"errors"
	"strconv"
	"sync"
	"time"
)

// BankService is an interface representing a bank service capable of handling distributed transactions.
type BankService interface {
	Prepare(txnID string) (bool, error)
	Commit(txnID string) error
	Rollback(txnID string) error
}

// CoordinatorConfig holds configuration parameters for timeouts and retry mechanisms.
type CoordinatorConfig struct {
	PrepareTimeout  time.Duration
	CommitTimeout   time.Duration
	RollbackTimeout time.Duration
	RetryCount      int
	BackoffInterval time.Duration
}

// ExecuteTransaction coordinates a distributed transaction across multiple bank services using a two-phase commit.
// It returns nil if the transaction is successfully committed across all services; otherwise, it returns an error.
func ExecuteTransaction(services []BankService, config CoordinatorConfig) error {
	// Generate a unique transaction ID using the current time.
	txnID := strconv.FormatInt(time.Now().UnixNano(), 10)

	// Phase 1: Prepare Phase.
	prepareErrs := make(chan error, len(services))
	var wg sync.WaitGroup

	for _, svc := range services {
		wg.Add(1)
		go func(s BankService) {
			defer wg.Done()
			err := prepareWithTimeout(s, txnID, config.PrepareTimeout)
			prepareErrs <- err
		}(svc)
	}
	wg.Wait()
	close(prepareErrs)

	prepareFailed := false
	for err := range prepareErrs {
		if err != nil {
			prepareFailed = true
			break
		}
	}

	// If any service failed during prepare, roll back the transaction across all services.
	if prepareFailed {
		rollbackErrs := make(chan error, len(services))
		var rbWg sync.WaitGroup
		for _, svc := range services {
			rbWg.Add(1)
			go func(s BankService) {
				defer rbWg.Done()
				err := rollbackWithRetry(s, txnID, config)
				rollbackErrs <- err
			}(svc)
		}
		rbWg.Wait()
		close(rollbackErrs)
		return errors.New("transaction aborted during prepare phase")
	}

	// Phase 2: Commit Phase.
	commitErrs := make(chan error, len(services))
	var commitWg sync.WaitGroup
	for _, svc := range services {
		commitWg.Add(1)
		go func(s BankService) {
			defer commitWg.Done()
			err := commitWithRetry(s, txnID, config)
			commitErrs <- err
		}(svc)
	}
	commitWg.Wait()
	close(commitErrs)
	for err := range commitErrs {
		if err != nil {
			return errors.New("transaction commit failed: " + err.Error())
		}
	}
	return nil
}

// prepareWithTimeout calls the Prepare method of a bank service with a specified timeout.
func prepareWithTimeout(s BankService, txnID string, timeout time.Duration) error {
	done := make(chan error, 1)
	go func() {
		ack, err := s.Prepare(txnID)
		if err != nil || !ack {
			done <- errors.New("prepare failed")
		} else {
			done <- nil
		}
	}()
	select {
	case err := <-done:
		return err
	case <-time.After(timeout):
		return errors.New("prepare timeout")
	}
}

// commitWithRetry calls the Commit method of a bank service with a retry mechanism and timeout for each attempt.
func commitWithRetry(s BankService, txnID string, config CoordinatorConfig) error {
	var lastErr error
	for attempt := 0; attempt <= config.RetryCount; attempt++ {
		done := make(chan error, 1)
		go func() {
			err := s.Commit(txnID)
			done <- err
		}()
		select {
		case err := <-done:
			if err == nil {
				return nil
			}
			lastErr = err
		case <-time.After(config.CommitTimeout):
			lastErr = errors.New("commit timeout")
		}
		time.Sleep(config.BackoffInterval * time.Duration(attempt+1))
	}
	return lastErr
}

// rollbackWithRetry calls the Rollback method of a bank service with a retry mechanism and timeout for each attempt.
func rollbackWithRetry(s BankService, txnID string, config CoordinatorConfig) error {
	var lastErr error
	for attempt := 0; attempt <= config.RetryCount; attempt++ {
		done := make(chan error, 1)
		go func() {
			err := s.Rollback(txnID)
			done <- err
		}()
		select {
		case err := <-done:
			if err == nil {
				return nil
			}
			lastErr = err
		case <-time.After(config.RollbackTimeout):
			lastErr = errors.New("rollback timeout")
		}
		time.Sleep(config.BackoffInterval * time.Duration(attempt+1))
	}
	return lastErr
}