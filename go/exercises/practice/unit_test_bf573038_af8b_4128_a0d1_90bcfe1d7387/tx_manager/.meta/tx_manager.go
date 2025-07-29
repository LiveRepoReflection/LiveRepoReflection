package tx_manager

import (
	"bufio"
	"errors"
	"fmt"
	"os"
	"strings"
	"sync"
	"time"
)

type TransactionID string

type Service interface {
	Prepare(txID TransactionID) error
	Commit(txID TransactionID) error
	Rollback(txID TransactionID) error
}

type TransactionManager interface {
	BeginTransaction() TransactionID
	EnlistService(txID TransactionID, service Service) error
	CommitTransaction(txID TransactionID) error
	RollbackTransaction(txID TransactionID) error
	Recover() error
}

type transactionState string

const (
	statePending    transactionState = "pending"
	stateCommitted  transactionState = "committed"
	stateRolledBack transactionState = "rolledback"
)

type Transaction struct {
	id       TransactionID
	services []Service
	state    transactionState
}

type txManager struct {
	logFile      string
	mu           sync.Mutex
	transactions map[TransactionID]*Transaction
	timeout      time.Duration
}

// NewTransactionManager creates a new instance of TransactionManager with the specified log file.
func NewTransactionManager(logFile string) TransactionManager {
	return &txManager{
		logFile:      logFile,
		transactions: make(map[TransactionID]*Transaction),
		timeout:      100 * time.Millisecond,
	}
}

func (tm *txManager) logAction(action string, txID TransactionID) error {
	f, err := os.OpenFile(tm.logFile, os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		return err
	}
	defer f.Close()
	// Log format: ACTION txID timestamp
	logLine := fmt.Sprintf("%s %s %d\n", action, txID, time.Now().UnixNano())
	_, err = f.WriteString(logLine)
	return err
}

func (tm *txManager) BeginTransaction() TransactionID {
	tm.mu.Lock()
	defer tm.mu.Unlock()
	txID := TransactionID(fmt.Sprintf("TX%d", len(tm.transactions)+1))
	tm.transactions[txID] = &Transaction{
		id:       txID,
		services: []Service{},
		state:    statePending,
	}
	_ = tm.logAction("BEGIN", txID)
	return txID
}

func (tm *txManager) EnlistService(txID TransactionID, service Service) error {
	tm.mu.Lock()
	defer tm.mu.Unlock()
	tx, ok := tm.transactions[txID]
	if !ok {
		return errors.New("transaction not found")
	}
	if tx.state != statePending {
		return errors.New("cannot enlist service to a non-pending transaction")
	}
	tx.services = append(tx.services, service)
	_ = tm.logAction("ENLIST", txID)
	return nil
}

func (tm *txManager) CommitTransaction(txID TransactionID) error {
	tm.mu.Lock()
	tx, ok := tm.transactions[txID]
	if !ok {
		// If transaction is not found, try to recover it as pending with no services.
		tx = &Transaction{
			id:       txID,
			services: []Service{},
			state:    statePending,
		}
		tm.transactions[txID] = tx
	}
	if tx.state != statePending {
		tm.mu.Unlock()
		return errors.New("transaction is not pending")
	}
	tm.mu.Unlock()

	// Phase 1: Prepare
	prepareErrors := tm.invokeOnServices(tx.services, "Prepare", txID)
	if len(prepareErrors) > 0 {
		_ = tm.RollbackTransaction(txID)
		return errors.New("prepare phase failed, transaction rolled back")
	}

	_ = tm.logAction("PREPARE", txID)

	// Phase 2: Commit
	commitErrors := tm.invokeOnServices(tx.services, "Commit", txID)
	if len(commitErrors) > 0 {
		_ = tm.RollbackTransaction(txID)
		return errors.New("commit phase failed, transaction rolled back")
	}

	tm.mu.Lock()
	tx.state = stateCommitted
	tm.mu.Unlock()
	_ = tm.logAction("COMMIT", txID)
	return nil
}

func (tm *txManager) RollbackTransaction(txID TransactionID) error {
	tm.mu.Lock()
	tx, ok := tm.transactions[txID]
	if !ok {
		tm.mu.Unlock()
		return nil
	}
	if tx.state != statePending {
		tm.mu.Unlock()
		return nil
	}
	tm.mu.Unlock()

	_ = tm.logAction("ROLLBACK", txID)
	_ = tm.invokeOnServices(tx.services, "Rollback", txID)
	tm.mu.Lock()
	tx.state = stateRolledBack
	tm.mu.Unlock()
	return nil
}

func (tm *txManager) invokeOnServices(services []Service, method string, txID TransactionID) []error {
	var wg sync.WaitGroup
	errCh := make(chan error, len(services))
	for _, s := range services {
		wg.Add(1)
		go func(srv Service) {
			defer wg.Done()
			ch := make(chan error, 1)
			go func() {
				var err error
				switch method {
				case "Prepare":
					err = srv.Prepare(txID)
				case "Commit":
					err = srv.Commit(txID)
				case "Rollback":
					err = srv.Rollback(txID)
				}
				ch <- err
			}()
			select {
			case err := <-ch:
				if err != nil {
					errCh <- err
				}
			case <-time.After(tm.timeout):
				errCh <- errors.New("operation timeout")
			}
		}(s)
	}
	wg.Wait()
	close(errCh)
	var errs []error
	for err := range errCh {
		errs = append(errs, err)
	}
	return errs
}

func (tm *txManager) Recover() error {
	tm.mu.Lock()
	defer tm.mu.Unlock()
	file, err := os.Open(tm.logFile)
	if err != nil {
		// If there is no log file, nothing to recover.
		return nil
	}
	defer file.Close()
	scanner := bufio.NewScanner(file)
	recovered := make(map[TransactionID]*Transaction)
	for scanner.Scan() {
		line := scanner.Text()
		parts := strings.Split(line, " ")
		if len(parts) < 2 {
			continue
		}
		action := parts[0]
		txID := TransactionID(parts[1])
		switch action {
		case "BEGIN":
			if _, exists := recovered[txID]; !exists {
				recovered[txID] = &Transaction{
					id:       txID,
					services: []Service{},
					state:    statePending,
				}
			}
		case "ENLIST":
			// Recovery cannot reinstantiate service pointers; ignore.
		case "PREPARE":
			if tx, exists := recovered[txID]; exists {
				tx.state = statePending
			}
		case "COMMIT":
			if tx, exists := recovered[txID]; exists {
				tx.state = stateCommitted
			}
		case "ROLLBACK":
			if tx, exists := recovered[txID]; exists {
				tx.state = stateRolledBack
			}
		}
	}
	for id, tx := range recovered {
		tm.transactions[id] = tx
	}
	return nil
}