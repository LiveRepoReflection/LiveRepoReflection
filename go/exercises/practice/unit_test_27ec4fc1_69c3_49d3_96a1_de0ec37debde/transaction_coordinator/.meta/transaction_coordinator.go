package transaction_coordinator

import (
	"errors"
	"fmt"
	"math"
	"strconv"
	"sync"
	"time"
)

// Service is the interface that each participating service must implement.
type Service interface {
	Prepare(transactionID string) error
	Commit(transactionID string) error
	Rollback(transactionID string) error
}

// TransactionCoordinator orchestrates a distributed transaction using the 2PC protocol.
type TransactionCoordinator struct {
	prepareTimeout  time.Duration
	commitTimeout   time.Duration
	rollbackTimeout time.Duration
	commitRetries   int

	mux          sync.Mutex
	transactions map[string][]Service
	nextID       int64
}

// NewTransactionCoordinator creates a new TransactionCoordinator with specified timeouts and commit retry count.
func NewTransactionCoordinator(prepareTimeout time.Duration, commitTimeout time.Duration, rollbackTimeout time.Duration, commitRetries int) *TransactionCoordinator {
	return &TransactionCoordinator{
		prepareTimeout:  prepareTimeout,
		commitTimeout:   commitTimeout,
		rollbackTimeout: rollbackTimeout,
		commitRetries:   commitRetries,
		transactions:    make(map[string][]Service),
		nextID:          0,
	}
}

// BeginTransaction starts a new transaction by storing the list of participating services and returns a unique transaction ID.
func (tc *TransactionCoordinator) BeginTransaction(services []Service) (string, error) {
	tc.mux.Lock()
	defer tc.mux.Unlock()
	tc.nextID++
	txID := strconv.FormatInt(tc.nextID, 10)
	tc.transactions[txID] = services
	return txID, nil
}

// EndTransaction completes the transaction identified by transactionID.
// It runs the 2PC protocol: prepare, then commit phases. If any phase fails, it triggers rollback.
func (tc *TransactionCoordinator) EndTransaction(transactionID string) error {
	tc.mux.Lock()
	services, ok := tc.transactions[transactionID]
	if !ok {
		tc.mux.Unlock()
		return errors.New("transaction not found")
	}
	// Remove transaction from map so that EndTransaction is idempotent.
	delete(tc.transactions, transactionID)
	tc.mux.Unlock()

	// Prepare Phase
	var prepareWg sync.WaitGroup
	prepareErrCh := make(chan error, len(services))
	for _, svc := range services {
		prepareWg.Add(1)
		go func(s Service) {
			defer prepareWg.Done()
			err := callWithTimeout(func() error { return s.Prepare(transactionID) }, tc.prepareTimeout)
			if err != nil {
				prepareErrCh <- err
			}
		}(svc)
	}
	prepareWg.Wait()
	close(prepareErrCh)
	var prepareErr error
	for err := range prepareErrCh {
		if prepareErr == nil {
			prepareErr = err
		}
		fmt.Println("Prepare error:", err)
	}
	if prepareErr != nil {
		rollbackErr := tc.rollbackAll(transactionID, services)
		if rollbackErr != nil {
			return errors.New("prepare failed and rollback encountered errors")
		}
		return errors.New("prepare failed, transaction rolled back")
	}

	// Commit Phase
	var commitWg sync.WaitGroup
	commitErrCh := make(chan error, len(services))
	for _, svc := range services {
		commitWg.Add(1)
		go func(s Service) {
			defer commitWg.Done()
			var err error
			retries := tc.commitRetries
			for attempt := 0; attempt < retries; attempt++ {
				err = callWithTimeout(func() error { return s.Commit(transactionID) }, tc.commitTimeout)
				if err == nil {
					break
				}
				fmt.Println("Commit error on attempt", attempt+1, ":", err)
				backoff := 50 * time.Millisecond * time.Duration(int(math.Pow(2, float64(attempt))))
				time.Sleep(backoff)
			}
			if err != nil {
				commitErrCh <- err
			}
		}(svc)
	}
	commitWg.Wait()
	close(commitErrCh)
	var commitErr error
	for err := range commitErrCh {
		if commitErr == nil {
			commitErr = err
		}
		fmt.Println("Commit error:", err)
	}
	if commitErr != nil {
		rollbackErr := tc.rollbackAll(transactionID, services)
		if rollbackErr != nil {
			return errors.New("commit failed and rollback encountered errors")
		}
		return errors.New("commit failed, transaction rolled back")
	}

	return nil
}

// rollbackAll attempts to rollback the transaction on all participating services.
func (tc *TransactionCoordinator) rollbackAll(transactionID string, services []Service) error {
	var rollbackWg sync.WaitGroup
	rollbackErrCh := make(chan error, len(services))
	for _, svc := range services {
		rollbackWg.Add(1)
		go func(s Service) {
			defer rollbackWg.Done()
			err := callWithTimeout(func() error { return s.Rollback(transactionID) }, tc.rollbackTimeout)
			if err != nil {
				rollbackErrCh <- err
				fmt.Println("Rollback error:", err)
			}
		}(svc)
	}
	rollbackWg.Wait()
	close(rollbackErrCh)
	var rollbackErr error
	for err := range rollbackErrCh {
		if rollbackErr == nil {
			rollbackErr = err
		}
	}
	return rollbackErr
}

// callWithTimeout executes the given function and returns its error result.
// If the function does not complete within the timeout duration, it returns a timeout error.
func callWithTimeout(fn func() error, timeout time.Duration) error {
	ch := make(chan error, 1)
	go func() {
		ch <- fn()
	}()
	select {
	case err := <-ch:
		return err
	case <-time.After(timeout):
		return errors.New("operation timeout")
	}
}