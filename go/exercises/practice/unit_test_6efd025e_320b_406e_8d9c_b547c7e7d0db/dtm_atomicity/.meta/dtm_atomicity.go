package dtm_atomicity

import (
	"context"
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
	"time"
)

type OperationFunc func(txID string) error

type operation struct {
	prepare  OperationFunc
	commit   OperationFunc
	rollback OperationFunc
}

type Transaction struct {
	ops []operation
}

// DistributedTransactionManager is a simplified in-memory distributed transaction manager
// implementing the two-phase commit protocol.
type DistributedTransactionManager struct {
	transactions   map[string]*Transaction
	mu             sync.Mutex
	idCounter      uint64
	sem            chan struct{}
	prepareTimeout time.Duration
}

// NewDistributedTransactionManager creates a new DistributedTransactionManager with default settings.
func NewDistributedTransactionManager() *DistributedTransactionManager {
	return &DistributedTransactionManager{
		transactions:   make(map[string]*Transaction),
		sem:            make(chan struct{}, 100),
		prepareTimeout: 50 * time.Millisecond,
	}
}

// BeginTransaction registers a new transaction and returns a unique transaction ID.
// It blocks if the maximum concurrent transactions limit is reached.
func (dtm *DistributedTransactionManager) BeginTransaction() string {
	// Acquire semaphore for concurrent transaction limit.
	dtm.sem <- struct{}{}

	txID := fmt.Sprintf("tx-%d", atomic.AddUint64(&dtm.idCounter, 1))
	dtm.mu.Lock()
	dtm.transactions[txID] = &Transaction{
		ops: []operation{},
	}
	dtm.mu.Unlock()
	return txID
}

// Register adds a service's operations (prepare, commit, rollback) to the transaction identified by txID.
func (dtm *DistributedTransactionManager) Register(txID string, prepare OperationFunc, commit OperationFunc, rollback OperationFunc) {
	dtm.mu.Lock()
	defer dtm.mu.Unlock()
	trx, exists := dtm.transactions[txID]
	if !exists {
		// If transaction is not found, create a new one (should normally not happen).
		trx = &Transaction{
			ops: []operation{},
		}
		dtm.transactions[txID] = trx
	}
	op := operation{
		prepare:  prepare,
		commit:   commit,
		rollback: rollback,
	}
	trx.ops = append(trx.ops, op)
}

// EndTransaction executes the two-phase commit protocol for the transaction identified by txID.
// In phase 1, it calls prepare on all registered operations concurrently with a timeout.
// If all prepare operations succeed before the timeout, it proceeds to the commit phase.
// Otherwise, it initiates rollback for all registered operations.
func (dtm *DistributedTransactionManager) EndTransaction(txID string) error {
	dtm.mu.Lock()
	transaction, exists := dtm.transactions[txID]
	if !exists {
		dtm.mu.Unlock()
		<-dtm.sem
		return errors.New("transaction not found")
	}
	// Remove transaction to prevent reuse.
	delete(dtm.transactions, txID)
	dtm.mu.Unlock()
	defer func() { <-dtm.sem }()

	ctx, cancel := context.WithTimeout(context.Background(), dtm.prepareTimeout)
	defer cancel()

	prepareErrCh := make(chan error, len(transaction.ops))
	var wg sync.WaitGroup

	// Phase 1: Prepare
	for _, op := range transaction.ops {
		wg.Add(1)
		go func(op operation) {
			defer wg.Done()
			if err := op.prepare(txID); err != nil {
				prepareErrCh <- err
			}
		}(op)
	}
	doneCh := make(chan struct{})
	go func() {
		wg.Wait()
		close(doneCh)
	}()

	select {
	case <-ctx.Done():
		// Timeout reached; prepare phase did not complete in time.
		return dtm.rollbackAll(transaction.ops, txID)
	case <-doneCh:
		// All prepare operations finished.
		close(prepareErrCh)
		var prepareErrors []error
		for err := range prepareErrCh {
			prepareErrors = append(prepareErrors, err)
		}
		if len(prepareErrors) > 0 {
			return dtm.rollbackAll(transaction.ops, txID)
		}
	}

	// Phase 2: Commit
	commitErr := dtm.commitAll(transaction.ops, txID)
	if commitErr != nil {
		return commitErr
	}
	return nil
}

// commitAll concurrently calls commit for all operations and aggregates any errors.
func (dtm *DistributedTransactionManager) commitAll(ops []operation, txID string) error {
	var wg sync.WaitGroup
	commitErrCh := make(chan error, len(ops))
	for _, op := range ops {
		wg.Add(1)
		go func(op operation) {
			defer wg.Done()
			if err := op.commit(txID); err != nil {
				commitErrCh <- err
			}
		}(op)
	}
	wg.Wait()
	close(commitErrCh)
	var commitErrors []error
	for err := range commitErrCh {
		commitErrors = append(commitErrors, err)
	}
	if len(commitErrors) > 0 {
		return combineErrors("commit phase failed", commitErrors)
	}
	return nil
}

// rollbackAll concurrently calls rollback for all operations and aggregates any errors.
func (dtm *DistributedTransactionManager) rollbackAll(ops []operation, txID string) error {
	var wg sync.WaitGroup
	rollbackErrCh := make(chan error, len(ops))
	for _, op := range ops {
		wg.Add(1)
		go func(op operation) {
			defer wg.Done()
			if err := op.rollback(txID); err != nil {
				rollbackErrCh <- err
			}
		}(op)
	}
	wg.Wait()
	close(rollbackErrCh)
	var rollbackErrors []error
	for err := range rollbackErrCh {
		rollbackErrors = append(rollbackErrors, err)
	}
	return combineErrors("transaction rolled back", rollbackErrors)
}

// combineErrors aggregates multiple errors into one error message.
func combineErrors(prefix string, errs []error) error {
	if len(errs) == 0 {
		return errors.New(prefix)
	}
	msg := prefix + ": "
	for i, err := range errs {
		if i > 0 {
			msg += "; "
		}
		msg += err.Error()
	}
	return errors.New(msg)
}