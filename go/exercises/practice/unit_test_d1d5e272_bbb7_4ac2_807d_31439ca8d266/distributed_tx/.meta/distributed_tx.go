package distributedtx

import (
    "errors"
    "fmt"
    "sync"
    "time"
)

type TransactionID int64

type Service interface {
    Prepare(txID TransactionID) error
    Commit(txID TransactionID) error
    Rollback(txID TransactionID) error
    GetState(txID TransactionID) string
}

type Coordinator struct {
    services        []Service
    timeout         time.Duration
    nextTxID        int64
    activeTransactions map[TransactionID]*transactionState
    mutex          sync.RWMutex
}

type transactionState struct {
    preparedServices map[Service]bool
    status          string
    mutex           sync.RWMutex
}

var (
    ErrTransactionNotFound = errors.New("transaction not found")
    ErrPrepareFailed      = errors.New("prepare phase failed")
    ErrCommitFailed       = errors.New("commit phase failed")
    ErrTimeout            = errors.New("transaction timeout")
)

func NewCoordinator(services []Service, timeout time.Duration) *Coordinator {
    return &Coordinator{
        services:           services,
        timeout:           timeout,
        activeTransactions: make(map[TransactionID]*transactionState),
    }
}

func (c *Coordinator) BeginTransaction() TransactionID {
    c.mutex.Lock()
    c.nextTxID++
    txID := TransactionID(c.nextTxID)
    c.activeTransactions[txID] = &transactionState{
        preparedServices: make(map[Service]bool),
        status:          "active",
    }
    c.mutex.Unlock()
    return txID
}

func (c *Coordinator) CommitTransaction(txID TransactionID) error {
    // Get transaction state
    c.mutex.RLock()
    txState, exists := c.activeTransactions[txID]
    c.mutex.RUnlock()
    
    if !exists {
        return ErrTransactionNotFound
    }

    // Prepare phase
    if err := c.preparePhase(txID, txState); err != nil {
        c.rollbackAll(txID, txState)
        return fmt.Errorf("prepare phase failed: %w", err)
    }

    // Commit phase
    if err := c.commitPhase(txID, txState); err != nil {
        c.rollbackAll(txID, txState)
        return fmt.Errorf("commit phase failed: %w", err)
    }

    // Cleanup
    c.mutex.Lock()
    delete(c.activeTransactions, txID)
    c.mutex.Unlock()

    return nil
}

func (c *Coordinator) preparePhase(txID TransactionID, txState *transactionState) error {
    results := make(chan error, len(c.services))
    timeout := time.After(c.timeout)

    // Send prepare to all services
    for _, svc := range c.services {
        go func(s Service) {
            results <- s.Prepare(txID)
        }(svc)
    }

    // Wait for all results or timeout
    for i := 0; i < len(c.services); i++ {
        select {
        case err := <-results:
            if err != nil {
                return err
            }
        case <-timeout:
            return ErrTimeout
        }
    }

    txState.mutex.Lock()
    txState.status = "prepared"
    txState.mutex.Unlock()
    return nil
}

func (c *Coordinator) commitPhase(txID TransactionID, txState *transactionState) error {
    results := make(chan error, len(c.services))

    // Send commit to all services
    for _, svc := range c.services {
        go func(s Service) {
            results <- s.Commit(txID)
        }(svc)
    }

    // Wait for all results
    for i := 0; i < len(c.services); i++ {
        if err := <-results; err != nil {
            return err
        }
    }

    txState.mutex.Lock()
    txState.status = "committed"
    txState.mutex.Unlock()
    return nil
}

func (c *Coordinator) rollbackAll(txID TransactionID, txState *transactionState) error {
    results := make(chan error, len(c.services))

    // Send rollback to all services
    for _, svc := range c.services {
        go func(s Service) {
            results <- s.Rollback(txID)
        }(svc)
    }

    // Wait for all results
    var lastErr error
    for i := 0; i < len(c.services); i++ {
        if err := <-results; err != nil {
            lastErr = err
        }
    }

    txState.mutex.Lock()
    txState.status = "rolledback"
    txState.mutex.Unlock()
    
    return lastErr
}

func (c *Coordinator) RollbackTransaction(txID TransactionID) error {
    c.mutex.RLock()
    txState, exists := c.activeTransactions[txID]
    c.mutex.RUnlock()

    if !exists {
        return ErrTransactionNotFound
    }

    err := c.rollbackAll(txID, txState)

    c.mutex.Lock()
    delete(c.activeTransactions, txID)
    c.mutex.Unlock()

    return err
}

// Recover simulates coordinator recovery after crash
func (c *Coordinator) Recover() error {
    c.mutex.RLock()
    defer c.mutex.RUnlock()

    for txID, txState := range c.activeTransactions {
        txState.mutex.RLock()
        status := txState.status
        txState.mutex.RUnlock()

        if status == "prepared" {
            // If transaction was prepared but not committed, roll it back
            if err := c.rollbackAll(txID, txState); err != nil {
                return fmt.Errorf("recovery rollback failed for transaction %d: %w", txID, err)
            }
        }
    }
    return nil
}