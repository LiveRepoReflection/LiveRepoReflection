package txncoordinator

import (
	"errors"
	"fmt"
	"log"
	"sync"
	"time"
)

// Constants for configuration
const (
	defaultTimeout     = 5 * time.Second
	maxRetries        = 3
	baseRetryInterval = 100 * time.Millisecond
)

// Participant interface defines the contract for participating services
type Participant interface {
	Prepare(transactionID string, data map[string]interface{}) error
	Commit(transactionID string) error
	Rollback(transactionID string) error
}

// Transaction represents a distributed transaction
type Transaction struct {
	ID           string
	Participants []Participant
	Status       TransactionStatus
	mu           sync.RWMutex
}

// TransactionStatus represents the current state of a transaction
type TransactionStatus int

const (
	StatusActive TransactionStatus = iota
	StatusPreparing
	StatusCommitting
	StatusRollingBack
	StatusCommitted
	StatusRolledBack
)

// Coordinator manages distributed transactions
type Coordinator struct {
	transactions map[string]*Transaction
	mu           sync.RWMutex
	idCounter    uint64
}

// NewCoordinator creates a new transaction coordinator
func NewCoordinator() *Coordinator {
	return &Coordinator{
		transactions: make(map[string]*Transaction),
	}
}

// BeginTransaction starts a new transaction
func (c *Coordinator) BeginTransaction() string {
	c.mu.Lock()
	defer c.mu.Unlock()

	c.idCounter++
	txID := fmt.Sprintf("tx-%d", c.idCounter)
	
	transaction := &Transaction{
		ID:     txID,
		Status: StatusActive,
	}
	
	c.transactions[txID] = transaction
	log.Printf("Transaction started: %s", txID)
	return txID
}

// EnlistParticipant adds a participant to an existing transaction
func (c *Coordinator) EnlistParticipant(transactionID string, participant Participant) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	tx, exists := c.transactions[transactionID]
	if !exists {
		return fmt.Errorf("transaction %s not found", transactionID)
	}

	tx.mu.Lock()
	defer tx.mu.Unlock()

	if tx.Status != StatusActive {
		return fmt.Errorf("transaction %s is not active", transactionID)
	}

	tx.Participants = append(tx.Participants, participant)
	log.Printf("Participant enlisted in transaction %s", transactionID)
	return nil
}

// CommitTransaction attempts to commit the transaction using 2PC
func (c *Coordinator) CommitTransaction(transactionID string, data map[string]interface{}) error {
	c.mu.RLock()
	tx, exists := c.transactions[transactionID]
	c.mu.RUnlock()

	if !exists {
		return fmt.Errorf("transaction %s not found", transactionID)
	}

	tx.mu.Lock()
	if tx.Status != StatusActive {
		tx.mu.Unlock()
		return fmt.Errorf("transaction %s is not active", transactionID)
	}
	tx.Status = StatusPreparing
	tx.mu.Unlock()

	// Prepare phase
	prepareResults := make(chan error, len(tx.Participants))
	var wg sync.WaitGroup

	for _, p := range tx.Participants {
		wg.Add(1)
		go func(participant Participant) {
			defer wg.Done()
			err := c.prepareWithRetry(participant, transactionID, data)
			prepareResults <- err
		}(p)
	}

	// Wait for all prepare operations with timeout
	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		// Continue with processing results
	case <-time.After(defaultTimeout):
		log.Printf("Prepare phase timeout for transaction %s", transactionID)
		c.rollbackTransaction(tx)
		return errors.New("prepare phase timeout")
	}

	// Check prepare results
	close(prepareResults)
	for err := range prepareResults {
		if err != nil {
			log.Printf("Prepare phase failed for transaction %s: %v", transactionID, err)
			c.rollbackTransaction(tx)
			return fmt.Errorf("prepare phase failed: %v", err)
		}
	}

	// Commit phase
	tx.mu.Lock()
	tx.Status = StatusCommitting
	tx.mu.Unlock()

	var commitError error
	for _, p := range tx.Participants {
		if err := c.commitWithRetry(p, transactionID); err != nil {
			commitError = err
			log.Printf("Commit failed for transaction %s: %v", transactionID, err)
			// Continue committing other participants
		}
	}

	tx.mu.Lock()
	tx.Status = StatusCommitted
	tx.mu.Unlock()

	if commitError != nil {
		return fmt.Errorf("commit phase failed: %v", commitError)
	}

	log.Printf("Transaction %s committed successfully", transactionID)
	return nil
}

// RollbackTransaction explicitly rolls back a transaction
func (c *Coordinator) RollbackTransaction(transactionID string) error {
	c.mu.RLock()
	tx, exists := c.transactions[transactionID]
	c.mu.RUnlock()

	if !exists {
		return fmt.Errorf("transaction %s not found", transactionID)
	}

	return c.rollbackTransaction(tx)
}

// rollbackTransaction performs the rollback operation
func (c *Coordinator) rollbackTransaction(tx *Transaction) error {
	tx.mu.Lock()
	if tx.Status == StatusRolledBack {
		tx.mu.Unlock()
		return nil
	}
	tx.Status = StatusRollingBack
	tx.mu.Unlock()

	var rollbackError error
	for _, p := range tx.Participants {
		if err := c.rollbackWithRetry(p, tx.ID); err != nil {
			rollbackError = err
			log.Printf("Rollback failed for transaction %s: %v", tx.ID, err)
			// Continue rolling back other participants
		}
	}

	tx.mu.Lock()
	tx.Status = StatusRolledBack
	tx.mu.Unlock()

	if rollbackError != nil {
		return fmt.Errorf("rollback failed: %v", rollbackError)
	}

	log.Printf("Transaction %s rolled back successfully", tx.ID)
	return nil
}

// Helper functions for retrying operations with exponential backoff

func (c *Coordinator) prepareWithRetry(p Participant, txID string, data map[string]interface{}) error {
	return c.retryOperation(func() error {
		return p.Prepare(txID, data)
	})
}

func (c *Coordinator) commitWithRetry(p Participant, txID string) error {
	return c.retryOperation(func() error {
		return p.Commit(txID)
	})
}

func (c *Coordinator) rollbackWithRetry(p Participant, txID string) error {
	return c.retryOperation(func() error {
		return p.Rollback(txID)
	})
}

func (c *Coordinator) retryOperation(operation func() error) error {
	var lastErr error
	for attempt := 0; attempt < maxRetries; attempt++ {
		if attempt > 0 {
			backoff := time.Duration(1<<uint(attempt-1)) * baseRetryInterval
			time.Sleep(backoff)
		}

		if err := operation(); err != nil {
			lastErr = err
			log.Printf("Operation failed (attempt %d/%d): %v", attempt+1, maxRetries, err)
			continue
		}
		return nil
	}
	return lastErr
}