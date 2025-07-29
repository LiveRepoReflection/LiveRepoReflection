package dtc_banking

import (
	"errors"
	"fmt"
	"log"
	"sync"
	"time"
)

// Operation represents a single transfer operation within a transaction
type Operation struct {
	SourceBankID   string
	SourceAccountID string
	DestBankID     string
	DestAccountID  string
	Amount         int
}

// Transaction represents a collection of operations that should be executed atomically
type Transaction struct {
	ID         string
	Operations []Operation
}

// BankService defines the interface that bank services must implement
type BankService interface {
	Prepare(transactionID string, operations []Operation) error
	Commit(transactionID string) error
	Rollback(transactionID string) error
}

// Coordinator manages distributed transactions across multiple bank services
type Coordinator struct {
	services        map[string]BankService
	mutex           sync.RWMutex
	maxRetries      int
	retryDelay      time.Duration
	operationTimeout time.Duration
}

// NewCoordinator creates a new transaction coordinator
func NewCoordinator(services map[string]BankService) *Coordinator {
	return &Coordinator{
		services:        services,
		mutex:           sync.RWMutex{},
		maxRetries:      5,
		retryDelay:      500 * time.Millisecond,
		operationTimeout: 2 * time.Second,
	}
}

// ExecuteTransaction coordinates the execution of a distributed transaction
func (c *Coordinator) ExecuteTransaction(transaction Transaction) error {
	log.Printf("Starting transaction %s", transaction.ID)

	// First, validate the transaction
	if err := c.validateTransaction(transaction); err != nil {
		log.Printf("Transaction %s validation failed: %v", transaction.ID, err)
		return err
	}

	// Get participating services
	participants := c.getParticipants(transaction)

	// Prepare phase
	prepareErr := c.prepareAll(transaction, participants)
	if prepareErr != nil {
		// Prepare failed, rollback all participants
		log.Printf("Transaction %s prepare phase failed: %v, starting rollback", transaction.ID, prepareErr)
		c.rollbackAll(transaction.ID, participants)
		return prepareErr
	}

	// Commit phase
	commitErr := c.commitAll(transaction.ID, participants)
	if commitErr != nil {
		// Some commits failed - try to rollback, but the transaction might be in an inconsistent state
		log.Printf("Transaction %s commit phase failed: %v, attempting rollback", transaction.ID, commitErr)
		c.rollbackAll(transaction.ID, participants)
		return commitErr
	}

	log.Printf("Transaction %s completed successfully", transaction.ID)
	return nil
}

// validateTransaction checks if the transaction is valid
func (c *Coordinator) validateTransaction(transaction Transaction) error {
	if transaction.ID == "" {
		return errors.New("transaction ID cannot be empty")
	}
	
	if len(transaction.Operations) == 0 {
		return errors.New("transaction must have at least one operation")
	}
	
	for i, op := range transaction.Operations {
		if op.Amount <= 0 {
			return fmt.Errorf("operation %d has invalid amount: %d", i, op.Amount)
		}
		
		if op.SourceBankID == "" || op.SourceAccountID == "" {
			return fmt.Errorf("operation %d has invalid source", i)
		}
		
		if op.DestBankID == "" || op.DestAccountID == "" {
			return fmt.Errorf("operation %d has invalid destination", i)
		}
		
		// Check if the services exist
		c.mutex.RLock()
		_, sourceExists := c.services[op.SourceBankID]
		_, destExists := c.services[op.DestBankID]
		c.mutex.RUnlock()
		
		if !sourceExists {
			return fmt.Errorf("source bank %s does not exist", op.SourceBankID)
		}
		
		if !destExists {
			return fmt.Errorf("destination bank %s does not exist", op.DestBankID)
		}
	}
	
	return nil
}

// getParticipants returns a set of unique bank services involved in the transaction
func (c *Coordinator) getParticipants(transaction Transaction) map[string]BankService {
	participants := make(map[string]BankService)
	
	c.mutex.RLock()
	defer c.mutex.RUnlock()
	
	for _, op := range transaction.Operations {
		if _, exists := participants[op.SourceBankID]; !exists {
			participants[op.SourceBankID] = c.services[op.SourceBankID]
		}
		
		if _, exists := participants[op.DestBankID]; !exists {
			participants[op.DestBankID] = c.services[op.DestBankID]
		}
	}
	
	return participants
}

// prepareAll attempts to prepare all participants
func (c *Coordinator) prepareAll(transaction Transaction, participants map[string]BankService) error {
	// Group operations by bank service
	operationsByBank := make(map[string][]Operation)
	for _, op := range transaction.Operations {
		if _, ok := operationsByBank[op.SourceBankID]; !ok {
			operationsByBank[op.SourceBankID] = []Operation{}
		}
		operationsByBank[op.SourceBankID] = append(operationsByBank[op.SourceBankID], op)
		
		if op.DestBankID != op.SourceBankID {
			if _, ok := operationsByBank[op.DestBankID]; !ok {
				operationsByBank[op.DestBankID] = []Operation{}
			}
			operationsByBank[op.DestBankID] = append(operationsByBank[op.DestBankID], op)
		}
	}

	// Prepare phase - execute in parallel for all participants
	var wg sync.WaitGroup
	var mutex sync.Mutex
	var firstError error

	for bankID, service := range participants {
		wg.Add(1)
		go func(bankID string, service BankService, ops []Operation) {
			defer wg.Done()
			
			// With retries
			var err error
			for retry := 0; retry < c.maxRetries; retry++ {
				err = c.executeWithTimeout(func() error {
					return service.Prepare(transaction.ID, ops)
				})
				
				if err == nil {
					log.Printf("Bank %s successfully prepared for transaction %s", bankID, transaction.ID)
					return
				}
				
				log.Printf("Bank %s prepare failed for transaction %s (attempt %d/%d): %v", 
					bankID, transaction.ID, retry+1, c.maxRetries, err)
				
				// Only retry on simulated network/service failures, not validation errors
				if retry < c.maxRetries-1 {
					time.Sleep(c.retryDelay)
				}
			}
			
			// Failed after all retries
			mutex.Lock()
			if firstError == nil {
				firstError = fmt.Errorf("bank %s prepare failed: %v", bankID, err)
			}
			mutex.Unlock()
		}(bankID, service, operationsByBank[bankID])
	}
	
	wg.Wait()
	return firstError
}

// commitAll attempts to commit all participants
func (c *Coordinator) commitAll(transactionID string, participants map[string]BankService) error {
	var wg sync.WaitGroup
	var mutex sync.Mutex
	var firstError error
	
	for bankID, service := range participants {
		wg.Add(1)
		go func(bankID string, service BankService) {
			defer wg.Done()
			
			// With retries
			var err error
			for retry := 0; retry < c.maxRetries; retry++ {
				err = c.executeWithTimeout(func() error {
					return service.Commit(transactionID)
				})
				
				if err == nil {
					log.Printf("Bank %s successfully committed transaction %s", bankID, transactionID)
					return
				}
				
				log.Printf("Bank %s commit failed for transaction %s (attempt %d/%d): %v", 
					bankID, transactionID, retry+1, c.maxRetries, err)
				
				if retry < c.maxRetries-1 {
					time.Sleep(c.retryDelay)
				}
			}
			
			// Failed after all retries
			mutex.Lock()
			if firstError == nil {
				firstError = fmt.Errorf("bank %s commit failed: %v", bankID, err)
			}
			mutex.Unlock()
		}(bankID, service)
	}
	
	wg.Wait()
	return firstError
}

// rollbackAll attempts to rollback all participants
func (c *Coordinator) rollbackAll(transactionID string, participants map[string]BankService) {
	var wg sync.WaitGroup
	
	for bankID, service := range participants {
		wg.Add(1)
		go func(bankID string, service BankService) {
			defer wg.Done()
			
			// With retries
			var err error
			for retry := 0; retry < c.maxRetries; retry++ {
				err = c.executeWithTimeout(func() error {
					return service.Rollback(transactionID)
				})
				
				if err == nil {
					log.Printf("Bank %s successfully rolled back transaction %s", bankID, transactionID)
					return
				}
				
				log.Printf("Bank %s rollback failed for transaction %s (attempt %d/%d): %v", 
					bankID, transactionID, retry+1, c.maxRetries, err)
				
				if retry < c.maxRetries-1 {
					time.Sleep(c.retryDelay)
				}
			}
			
			// Failed after all retries
			log.Printf("Bank %s rollback permanently failed for transaction %s: %v", bankID, transactionID, err)
		}(bankID, service)
	}
	
	wg.Wait()
}

// executeWithTimeout executes a function with a timeout
func (c *Coordinator) executeWithTimeout(fn func() error) error {
	resultCh := make(chan error, 1)
	
	go func() {
		defer func() {
			if r := recover(); r != nil {
				resultCh <- fmt.Errorf("panic in operation: %v", r)
			}
		}()
		resultCh <- fn()
	}()
	
	select {
	case result := <-resultCh:
		return result
	case <-time.After(c.operationTimeout):
		return errors.New("operation timed out")
	}
}