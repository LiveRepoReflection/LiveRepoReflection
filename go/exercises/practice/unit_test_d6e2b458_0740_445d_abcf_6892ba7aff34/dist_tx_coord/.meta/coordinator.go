package dist_tx_coord

import (
	"errors"
	"sync"
	"time"
)

type Service interface {
	Prepare() error
	CommitRollback(commit bool) error
	GetName() string
}

type TransactionID string

type transactionState struct {
	services []Service
	prepared bool
	done     bool
	mu       sync.Mutex
}

type TransactionCoordinator struct {
	transactions   map[TransactionID]*transactionState
	mu             sync.RWMutex
	concurrency    int
	semaphore      chan struct{}
	requestQueue   chan func()
	shutdown       chan struct{}
	wg             sync.WaitGroup
	nextID         int
	idMu           sync.Mutex
}

func NewTransactionCoordinator(concurrency int, queueSize int) *TransactionCoordinator {
	tc := &TransactionCoordinator{
		transactions: make(map[TransactionID]*transactionState),
		concurrency:  concurrency,
		semaphore:    make(chan struct{}, concurrency),
		requestQueue: make(chan func(), queueSize),
		shutdown:     make(chan struct{}),
	}

	for i := 0; i < concurrency; i++ {
		tc.semaphore <- struct{}{}
	}

	go tc.processRequests()
	return tc
}

func (tc *TransactionCoordinator) generateID() TransactionID {
	tc.idMu.Lock()
	defer tc.idMu.Unlock()
	tc.nextID++
	return TransactionID(time.Now().Format("20060102150405") + "-" + string(rune(tc.nextID)))
}

func (tc *TransactionCoordinator) Begin() TransactionID {
	txID := tc.generateID()

	tc.mu.Lock()
	tc.transactions[txID] = &transactionState{
		services: make([]Service, 0),
	}
	tc.mu.Unlock()

	return txID
}

func (tc *TransactionCoordinator) Register(txID TransactionID, service Service) error {
	tc.mu.RLock()
	state, exists := tc.transactions[txID]
	tc.mu.RUnlock()

	if !exists {
		return errors.New("transaction does not exist")
	}

	state.mu.Lock()
	defer state.mu.Unlock()

	if state.done {
		return errors.New("transaction already completed")
	}

	state.services = append(state.services, service)
	return nil
}

func (tc *TransactionCoordinator) End(txID TransactionID, commit bool) error {
	tc.mu.RLock()
	state, exists := tc.transactions[txID]
	tc.mu.RUnlock()

	if !exists {
		return errors.New("transaction does not exist")
	}

	state.mu.Lock()
	if state.done {
		state.mu.Unlock()
		return errors.New("transaction already completed")
	}
	state.done = true
	state.mu.Unlock()

	var prepareErrors []error
	var wg sync.WaitGroup
	var mu sync.Mutex

	// Prepare phase
	for _, svc := range state.services {
		wg.Add(1)
		go func(s Service) {
			defer wg.Done()
			err := tc.runWithTimeout(func() error {
				return s.Prepare()
			}, 500*time.Millisecond)
			if err != nil {
				mu.Lock()
				prepareErrors = append(prepareErrors, err)
				mu.Unlock()
			}
		}(svc)
	}
	wg.Wait()

	if len(prepareErrors) > 0 {
		tc.rollbackAll(state.services)
		return &TransactionError{
			Phase:     "prepare",
			Errors:    prepareErrors,
			ServiceNames: getServiceNamesFromErrors(prepareErrors, state.services),
		}
	}

	state.mu.Lock()
	state.prepared = true
	state.mu.Unlock()

	if !commit {
		tc.rollbackAll(state.services)
		return nil
	}

	// Commit phase
	var commitErrors []error
	for _, svc := range state.services {
		wg.Add(1)
		go func(s Service) {
			defer wg.Done()
			err := tc.runWithTimeout(func() error {
				return s.CommitRollback(true)
			}, 500*time.Millisecond)
			if err != nil {
				mu.Lock()
				commitErrors = append(commitErrors, err)
				mu.Unlock()
			}
		}(svc)
	}
	wg.Wait()

	if len(commitErrors) > 0 {
		return &TransactionError{
			Phase:     "commit",
			Errors:    commitErrors,
			ServiceNames: getServiceNamesFromErrors(commitErrors, state.services),
		}
	}

	tc.mu.Lock()
	delete(tc.transactions, txID)
	tc.mu.Unlock()

	return nil
}

func (tc *TransactionCoordinator) rollbackAll(services []Service) {
	var wg sync.WaitGroup
	for _, svc := range services {
		wg.Add(1)
		go func(s Service) {
			defer wg.Done()
			_ = tc.runWithTimeout(func() error {
				return s.CommitRollback(false)
			}, 500*time.Millisecond)
		}(svc)
	}
	wg.Wait()
}

func (tc *TransactionCoordinator) runWithTimeout(fn func() error, timeout time.Duration) error {
	result := make(chan error, 1)
	go func() {
		result <- fn()
	}()

	select {
	case err := <-result:
		return err
	case <-time.After(timeout):
		return errors.New("operation timed out")
	}
}

func (tc *TransactionCoordinator) processRequests() {
	for {
		select {
		case req := <-tc.requestQueue:
			<-tc.semaphore
			go func() {
				req()
				tc.semaphore <- struct{}{}
			}()
		case <-tc.shutdown:
			return
		}
	}
}

func (tc *TransactionCoordinator) Shutdown() {
	close(tc.shutdown)
	tc.wg.Wait()
}

type TransactionError struct {
	Phase       string
	Errors      []error
	ServiceNames []string
}

func (e *TransactionError) Error() string {
	return "transaction failed during " + e.Phase + " phase"
}

func getServiceNamesFromErrors(errors []error, services []Service) []string {
	names := make([]string, 0, len(errors))
	for _, svc := range services {
		for _, err := range errors {
			if err != nil {
				names = append(names, svc.GetName())
				break
			}
		}
	}
	return names
}