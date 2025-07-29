package dtc_atomic

import (
	"errors"
	"sync"
	"time"
)

// Service defines the interface for a participating service in a distributed transaction.
type Service interface {
	Prepare(timeout time.Duration) error
	Commit(timeout time.Duration) error
	Rollback(timeout time.Duration) error
}

// Coordinator orchestrates distributed transactions using the Two-Phase Commit protocol.
type Coordinator struct {
	timeout time.Duration
}

// NewCoordinator creates a new instance of Coordinator with the specified timeout for service operations.
func NewCoordinator(timeout time.Duration) *Coordinator {
	return &Coordinator{timeout: timeout}
}

// ExecuteTransaction executes a distributed transaction using the 2PC protocol.
// It first runs the prepare phase on all services concurrently. If every service responds successfully,
// it proceeds to the commit phase. If any service fails during prepare, it rolls back all services.
func (c *Coordinator) ExecuteTransaction(services []Service) error {
	var wg sync.WaitGroup
	prepareErrs := make([]error, len(services))

	// Phase 1: Prepare
	for i, svc := range services {
		wg.Add(1)
		go func(i int, svc Service) {
			defer wg.Done()
			prepareErrs[i] = svc.Prepare(c.timeout)
		}(i, svc)
	}
	wg.Wait()

	prepareFailed := false
	for _, err := range prepareErrs {
		if err != nil {
			prepareFailed = true
			break
		}
	}

	if prepareFailed {
		// Phase 2 (Rollback): Rollback all services concurrently.
		var rbWg sync.WaitGroup
		for _, svc := range services {
			rbWg.Add(1)
			go func(svc Service) {
				defer rbWg.Done()
				_ = svc.Rollback(c.timeout)
			}(svc)
		}
		rbWg.Wait()
		return errors.New("prepare phase failed; transaction rolled back")
	}

	// Phase 2 (Commit): Commit all services concurrently.
	commitErrs := make([]error, len(services))
	wg = sync.WaitGroup{}
	for i, svc := range services {
		wg.Add(1)
		go func(i int, svc Service) {
			defer wg.Done()
			commitErrs[i] = svc.Commit(c.timeout)
		}(i, svc)
	}
	wg.Wait()

	for _, err := range commitErrs {
		if err != nil {
			return errors.New("commit phase failed; transaction might be inconsistent")
		}
	}
	return nil
}