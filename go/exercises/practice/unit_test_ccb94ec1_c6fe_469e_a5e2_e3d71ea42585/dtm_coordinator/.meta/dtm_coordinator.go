package dtm_coordinator

import (
	"errors"
	"sync"
	"time"
)

type ServiceInfo struct {
	Status string // "pending", "confirmed", "failed"
	Err    error
}

type Transaction struct {
	ID       int
	Status   string // "pending", "committed", "rolledback"
	Services map[string]*ServiceInfo
}

type Coordinator struct {
	mu           sync.Mutex
	nextTxID     int
	transactions map[int]*Transaction
	timeout      time.Duration
}

func NewCoordinator() *Coordinator {
	return &Coordinator{
		transactions: make(map[int]*Transaction),
		nextTxID:     1,
		timeout:      5 * time.Second,
	}
}

func (c *Coordinator) SetTimeout(t time.Duration) {
	c.mu.Lock()
	defer c.mu.Unlock()
	c.timeout = t
}

func (c *Coordinator) BeginTransaction() (*Transaction, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	tx := &Transaction{
		ID:       c.nextTxID,
		Status:   "pending",
		Services: make(map[string]*ServiceInfo),
	}
	c.transactions[c.nextTxID] = tx
	c.nextTxID++
	return tx, nil
}

func (c *Coordinator) RegisterService(txID int, serviceName string) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	tx, ok := c.transactions[txID]
	if !ok {
		return errors.New("transaction not found")
	}
	if tx.Status != "pending" {
		return errors.New("cannot register service to finalized transaction")
	}
	if _, exists := tx.Services[serviceName]; exists {
		return errors.New("service already registered")
	}
	tx.Services[serviceName] = &ServiceInfo{
		Status: "pending",
		Err:    nil,
	}
	return nil
}

func (c *Coordinator) SimulateServiceCommit(txID int, serviceName string) {
	c.mu.Lock()
	defer c.mu.Unlock()
	tx, ok := c.transactions[txID]
	if !ok {
		return
	}
	if svc, exists := tx.Services[serviceName]; exists && svc.Status == "pending" {
		svc.Status = "confirmed"
		svc.Err = nil
	}
}

func (c *Coordinator) SimulateServiceFailure(txID int, serviceName string, err error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	tx, ok := c.transactions[txID]
	if !ok {
		return
	}
	if svc, exists := tx.Services[serviceName]; exists && svc.Status == "pending" {
		svc.Status = "failed"
		svc.Err = err
	}
}

func (c *Coordinator) CommitTransaction(txID int) error {
	startTime := time.Now()
	for {
		c.mu.Lock()
		tx, ok := c.transactions[txID]
		if !ok {
			c.mu.Unlock()
			return errors.New("transaction not found")
		}
		// if already committed, idempotent commit returns nil.
		if tx.Status == "committed" {
			c.mu.Unlock()
			return nil
		}
		// if already rolled back, commit cannot proceed.
		if tx.Status == "rolledback" {
			c.mu.Unlock()
			return errors.New("transaction already rolled back")
		}
		allConfirmed := true
		for _, svc := range tx.Services {
			if svc.Status == "failed" {
				// mark as rolledback
				tx.Status = "rolledback"
				c.mu.Unlock()
				return errors.New("one or more services failed during commit")
			}
			if svc.Status != "confirmed" {
				allConfirmed = false
				break
			}
		}
		if allConfirmed {
			tx.Status = "committed"
			c.mu.Unlock()
			return nil
		}
		// check for timeout
		if time.Since(startTime) >= c.timeout {
			tx.Status = "rolledback"
			c.mu.Unlock()
			return errors.New("commit transaction timeout reached, transaction rolled back")
		}
		c.mu.Unlock()
		time.Sleep(100 * time.Millisecond)
	}
}

func (c *Coordinator) RollbackTransaction(txID int) error {
	c.mu.Lock()
	defer c.mu.Unlock()
	tx, ok := c.transactions[txID]
	if !ok {
		return errors.New("transaction not found")
	}
	// if already rolled back, idempotent rollback
	if tx.Status == "rolledback" {
		return nil
	}
	// if already committed, rollback is not allowed
	if tx.Status == "committed" {
		return errors.New("transaction already committed, cannot rollback")
	}
	tx.Status = "rolledback"
	return nil
}

func (c *Coordinator) GetTransactionStatus(txID int) (string, error) {
	c.mu.Lock()
	defer c.mu.Unlock()
	tx, ok := c.transactions[txID]
	if !ok {
		return "", errors.New("transaction not found")
	}
	return tx.Status, nil
}