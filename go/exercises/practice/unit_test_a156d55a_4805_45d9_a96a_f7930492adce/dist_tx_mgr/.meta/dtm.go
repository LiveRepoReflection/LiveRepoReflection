package dtm

import (
	"errors"
	"sync"
	"time"
)

type Participant struct {
	prepare       func() (string, error)
	commit        func(string) error
	rollback      func() error
	preparedValue string
}

type Transaction struct {
	txID         string
	participants []*Participant
	status       string // "pending", "committed", "rolledback"
	mu           sync.Mutex
}

type TransactionManager struct {
	timeout      time.Duration
	mu           sync.Mutex
	transactions map[string]*Transaction
}

// NewTransactionManager creates a new TransactionManager with the specified timeout.
func NewTransactionManager(timeout time.Duration) *TransactionManager {
	return &TransactionManager{
		timeout:      timeout,
		transactions: make(map[string]*Transaction),
	}
}

// RegisterParticipant registers a participant for the given transaction ID.
func (tm *TransactionManager) RegisterParticipant(txID string,
	prepare func() (string, error),
	commit func(string) error,
	rollback func() error) error {

	tm.mu.Lock()
	defer tm.mu.Unlock()

	// If transaction already exists, ensure it's in a state we can add participants.
	tx, exists := tm.transactions[txID]
	if !exists {
		tx = &Transaction{
			txID:         txID,
			participants: []*Participant{},
			status:       "pending",
		}
		tm.transactions[txID] = tx
	} else {
		// If already committed or rolledback, we cannot add new participants.
		if tx.status != "pending" {
			return errors.New("cannot add participant to finalized transaction")
		}
	}

	p := &Participant{
		prepare:  prepare,
		commit:   commit,
		rollback: rollback,
	}
	tx.participants = append(tx.participants, p)
	return nil
}

// CommitTransaction performs the two-phase commit for the transaction with the given txID.
func (tm *TransactionManager) CommitTransaction(txID string) error {
	tm.mu.Lock()
	tx, exists := tm.transactions[txID]
	tm.mu.Unlock()
	if !exists {
		return errors.New("transaction not found")
	}

	// Phase 1: Prepare Phase
	type prepareResult struct {
		idx int
		val string
		err error
	}

	results := make(chan prepareResult, len(tx.participants))
	var wg sync.WaitGroup

	for i, p := range tx.participants {
		wg.Add(1)
		go func(idx int, part *Participant) {
			defer wg.Done()
			val, err := callPrepare(tm.timeout, part.prepare)
			results <- prepareResult{idx: idx, val: val, err: err}
		}(i, p)
	}

	wg.Wait()
	close(results)

	var prepareFailed bool
	var prepareErr error

	// Collect prepare results.
	for res := range results {
		if res.err != nil {
			prepareFailed = true
			prepareErr = res.err
		} else {
			tx.participants[res.idx].preparedValue = res.val
		}
	}

	if prepareFailed {
		// If prepare fails, proceed to rollback.
		rollbackErr := tm.rollbackTransaction(tx)
		if rollbackErr != nil {
			return errors.New("prepare failed: " + prepareErr.Error() + " and rollback error: " + rollbackErr.Error())
		}
		return errors.New("prepare failed: " + prepareErr.Error())
	}

	// Phase 2: Commit Phase
	commitErrors := make(chan error, len(tx.participants))
	var commitWg sync.WaitGroup

	for _, p := range tx.participants {
		commitWg.Add(1)
		go func(part *Participant) {
			defer commitWg.Done()
			err := callCommit(tm.timeout, part.commit, part.preparedValue)
			commitErrors <- err
		}(p)
	}

	commitWg.Wait()
	close(commitErrors)

	var commitFailed bool
	var finalCommitErr error
	for err := range commitErrors {
		if err != nil {
			commitFailed = true
			finalCommitErr = err
		}
	}

	tx.mu.Lock()
	if commitFailed {
		tx.status = "failed"
	} else {
		tx.status = "committed"
	}
	tx.mu.Unlock()

	if commitFailed {
		return errors.New("commit phase error: " + finalCommitErr.Error())
	}
	return nil
}

// RollbackTransaction explicitly rolls back the transaction with the given txID.
func (tm *TransactionManager) RollbackTransaction(txID string) error {
	tm.mu.Lock()
	tx, exists := tm.transactions[txID]
	tm.mu.Unlock()
	if !exists {
		return errors.New("transaction not found")
	}
	return tm.rollbackTransaction(tx)
}

// Internal function to perform rollback concurrently.
func (tm *TransactionManager) rollbackTransaction(tx *Transaction) error {
	tx.mu.Lock()
	// Mark the transaction as rolledback regardless of current state.
	tx.status = "rolledback"
	tx.mu.Unlock()

	rollbackErrors := make(chan error, len(tx.participants))
	var wg sync.WaitGroup

	for _, p := range tx.participants {
		wg.Add(1)
		go func(part *Participant) {
			defer wg.Done()
			err := callRollback(tm.timeout, part.rollback)
			rollbackErrors <- err
		}(p)
	}

	wg.Wait()
	close(rollbackErrors)

	var rollbackFailed bool
	var finalErr error
	for err := range rollbackErrors {
		if err != nil {
			rollbackFailed = true
			finalErr = err
		}
	}

	if rollbackFailed {
		return errors.New("rollback phase error: " + finalErr.Error())
	}
	return nil
}

// callPrepare executes the prepare function with a timeout.
func callPrepare(timeout time.Duration, prepare func() (string, error)) (string, error) {
	type result struct {
		value string
		err   error
	}
	ch := make(chan result, 1)
	go func() {
		val, err := prepare()
		ch <- result{value: val, err: err}
	}()
	select {
	case res := <-ch:
		return res.value, res.err
	case <-time.After(timeout):
		return "", errors.New("prepare timeout")
	}
}

// callCommit executes the commit function with a timeout.
func callCommit(timeout time.Duration, commit func(string) error, data string) error {
	errCh := make(chan error, 1)
	go func() {
		errCh <- commit(data)
	}()
	select {
	case err := <-errCh:
		return err
	case <-time.After(timeout):
		return errors.New("commit timeout")
	}
}

// callRollback executes the rollback function with a timeout.
func callRollback(timeout time.Duration, rollback func() error) error {
	errCh := make(chan error, 1)
	go func() {
		errCh <- rollback()
	}()
	select {
	case err := <-errCh:
		return err
	case <-time.After(timeout):
		return errors.New("rollback timeout")
	}
}