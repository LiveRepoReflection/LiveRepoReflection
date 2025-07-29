package dtc_atomicity

import (
	"context"
	"errors"
	"sync"
	"time"
)

type Service interface {
	Prepare(ctx context.Context, txID string) error
	Commit(ctx context.Context, txID string) error
	Rollback(ctx context.Context, txID string) error
}

type TransactionState string

const (
	StatePreparing TransactionState = "PREPARING"
	StateReady     TransactionState = "READY"
	StateCommitting TransactionState = "COMMITTING"
	StateAborting   TransactionState = "ABORTING"
	StateCommitted  TransactionState = "COMMITTED"
	StateAborted    TransactionState = "ABORTED"
)

type DTCOptions struct {
	PrepareTimeout  time.Duration
	CommitTimeout   time.Duration
	MaxRetries      int
	RetryInterval   time.Duration
}

type DTC struct {
	services      []Service
	options       DTCOptions
	transactions  map[string]TransactionState
	transactionsMu sync.RWMutex
}

func NewDTC() *DTC {
	return &DTC{
		services: make([]Service, 0),
		options: DTCOptions{
			PrepareTimeout: 5 * time.Second,
			CommitTimeout:  5 * time.Second,
			MaxRetries:     3,
			RetryInterval:  100 * time.Millisecond,
		},
		transactions: make(map[string]TransactionState),
	}
}

func NewDTCWithOptions(options DTCOptions) *DTC {
	return &DTC{
		services:     make([]Service, 0),
		options:      options,
		transactions: make(map[string]TransactionState),
	}
}

func (d *DTC) RegisterService(service Service) {
	d.services = append(d.services, service)
}

func (d *DTC) ExecuteTransaction(ctx context.Context, txID string) error {
	d.transactionsMu.Lock()
	d.transactions[txID] = StatePreparing
	d.transactionsMu.Unlock()

	defer func() {
		d.transactionsMu.Lock()
		delete(d.transactions, txID)
		d.transactionsMu.Unlock()
	}()

	// Phase 1: Prepare
	prepareCtx, cancelPrepare := context.WithTimeout(ctx, d.options.PrepareTimeout)
	defer cancelPrepare()

	var prepareErrors []error
	var wg sync.WaitGroup
	var mu sync.Mutex

	for _, service := range d.services {
		wg.Add(1)
		go func(s Service) {
			defer wg.Done()
			err := s.Prepare(prepareCtx, txID)
			if err != nil {
				mu.Lock()
				prepareErrors = append(prepareErrors, err)
				mu.Unlock()
			}
		}(service)
	}
	wg.Wait()

	if len(prepareErrors) > 0 {
		d.transactionsMu.Lock()
		d.transactions[txID] = StateAborting
		d.transactionsMu.Unlock()

		d.rollbackAll(ctx, txID)
		return errors.New("prepare phase failed")
	}

	d.transactionsMu.Lock()
	d.transactions[txID] = StateReady
	d.transactionsMu.Unlock()

	// Phase 2: Commit
	d.transactionsMu.Lock()
	d.transactions[txID] = StateCommitting
	d.transactionsMu.Unlock()

	commitCtx, cancelCommit := context.WithTimeout(ctx, d.options.CommitTimeout)
	defer cancelCommit()

	var commitErrors []error
	var commitWg sync.WaitGroup
	var commitMu sync.Mutex

	for _, service := range d.services {
		commitWg.Add(1)
		go func(s Service) {
			defer commitWg.Done()
			err := d.retryOperation(commitCtx, func(ctx context.Context) error {
				return s.Commit(ctx, txID)
			})
			if err != nil {
				commitMu.Lock()
				commitErrors = append(commitErrors, err)
				commitMu.Unlock()
			}
		}(service)
	}
	commitWg.Wait()

	if len(commitErrors) > 0 {
		d.transactionsMu.Lock()
		d.transactions[txID] = StateAborting
		d.transactionsMu.Unlock()

		d.rollbackAll(ctx, txID)
		return errors.New("commit phase failed")
	}

	d.transactionsMu.Lock()
	d.transactions[txID] = StateCommitted
	d.transactionsMu.Unlock()

	return nil
}

func (d *DTC) rollbackAll(ctx context.Context, txID string) {
	var wg sync.WaitGroup
	for _, service := range d.services {
		wg.Add(1)
		go func(s Service) {
			defer wg.Done()
			_ = d.retryOperation(ctx, func(ctx context.Context) error {
				return s.Rollback(ctx, txID)
			})
		}(service)
	}
	wg.Wait()

	d.transactionsMu.Lock()
	d.transactions[txID] = StateAborted
	d.transactionsMu.Unlock()
}

func (d *DTC) retryOperation(ctx context.Context, op func(context.Context) error) error {
	var lastErr error
	for i := 0; i < d.options.MaxRetries; i++ {
		if i > 0 {
			select {
			case <-time.After(d.options.RetryInterval):
			case <-ctx.Done():
				return ctx.Err()
			}
		}

		err := op(ctx)
		if err == nil {
			return nil
		}
		lastErr = err

		if ctx.Err() != nil {
			return ctx.Err()
		}
	}
	return lastErr
}

func (d *DTC) GetTransactionState(txID string) TransactionState {
	d.transactionsMu.RLock()
	defer d.transactionsMu.RUnlock()
	return d.transactions[txID]
}