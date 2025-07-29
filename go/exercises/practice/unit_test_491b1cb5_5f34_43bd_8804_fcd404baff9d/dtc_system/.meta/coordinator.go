package dtc_system

import (
	"bytes"
	"errors"
	"fmt"
	"io/ioutil"
	"net/http"
	"sync"
	"time"
)

// Transaction statuses
const (
	StatusPending    = "PENDING"
	StatusPrepared   = "PREPARED"
	StatusCommitted  = "COMMITTED"
	StatusRolledBack = "ROLLEDBACK"
)

// Transaction represents a distributed transaction.
type Transaction struct {
	ID           string
	Participants []string
	Status       string
}

// Coordinator is responsible for managing distributed transactions.
type Coordinator struct {
	services     map[string]string   // map of service name to base URL
	transactions map[string]*Transaction
	timeout      time.Duration
	mu           sync.Mutex
	httpClient   *http.Client
}

// NewCoordinator creates a new Coordinator with a specified timeout.
func NewCoordinator(timeout time.Duration) *Coordinator {
	return &Coordinator{
		services:     make(map[string]string),
		transactions: make(map[string]*Transaction),
		timeout:      timeout,
		httpClient: &http.Client{
			Timeout: timeout,
		},
	}
}

// RegisterService registers a new service with a unique name and its base URL.
func (c *Coordinator) RegisterService(serviceName string, url string) error {
	c.mu.Lock()
	defer c.mu.Unlock()

	if _, exists := c.services[serviceName]; exists {
		return fmt.Errorf("service %s already registered", serviceName)
	}
	c.services[serviceName] = url
	return nil
}

// BeginTransaction starts a new distributed transaction using the 2PC protocol.
func (c *Coordinator) BeginTransaction(txID string, serviceNames []string) error {
	// Create a new transaction record.
	tx := &Transaction{
		ID:           txID,
		Participants: serviceNames,
		Status:       StatusPending,
	}

	c.mu.Lock()
	c.transactions[txID] = tx
	c.mu.Unlock()

	// Phase 1: Prepare
	preparedServices := []string{}
	for _, name := range serviceNames {
		url, ok := c.getServiceURL(name)
		if !ok {
			c.rollback(tx, preparedServices)
			c.updateTransactionStatus(txID, StatusRolledBack)
			return fmt.Errorf("service %s is not registered", name)
		}
		if err := c.sendRequest(url+"/prepare", txID); err != nil {
			c.rollback(tx, preparedServices)
			c.updateTransactionStatus(txID, StatusRolledBack)
			return fmt.Errorf("prepare failed for service %s: %v", name, err)
		}
		preparedServices = append(preparedServices, name)
	}

	// Update status to PREPARED temporarily.
	c.updateTransactionStatus(txID, StatusPrepared)

	// Phase 2: Commit
	for _, name := range serviceNames {
		url, _ := c.getServiceURL(name)
		if err := c.sendRequest(url+"/commit", txID); err != nil {
			// If any commit fails, rollback all services that have been prepared.
			c.rollback(tx, serviceNames)
			c.updateTransactionStatus(txID, StatusRolledBack)
			return fmt.Errorf("commit failed for service %s: %v", name, err)
		}
	}
	c.updateTransactionStatus(txID, StatusCommitted)
	return nil
}

// GetTransactionStatus returns the status of a given transaction by its ID.
func (c *Coordinator) GetTransactionStatus(txID string) string {
	c.mu.Lock()
	defer c.mu.Unlock()

	tx, exists := c.transactions[txID]
	if !exists {
		return "NOT_FOUND"
	}
	return tx.Status
}

// rollback sends a rollback request to the provided list of services.
func (c *Coordinator) rollback(tx *Transaction, serviceNames []string) {
	for _, name := range serviceNames {
		url, ok := c.getServiceURL(name)
		if !ok {
			continue
		}
		// Ignore errors during rollback.
		_ = c.sendRequest(url+"/rollback", tx.ID)
	}
}

// sendRequest sends an HTTP POST request to the given URL with the transaction ID as body.
func (c *Coordinator) sendRequest(url string, txID string) error {
	reqBody := bytes.NewBuffer([]byte(txID))
	req, err := http.NewRequest("POST", url, reqBody)
	if err != nil {
		return err
	}
	req.Header.Set("Content-Type", "text/plain")

	resp, err := c.httpClient.Do(req)
	if err != nil {
		return err
	}
	defer resp.Body.Close()
	// consume body to allow connection reuse
	_, _ = ioutil.ReadAll(resp.Body)

	if resp.StatusCode != http.StatusOK {
		return errors.New(fmt.Sprintf("received status code %d", resp.StatusCode))
	}
	return nil
}

// getServiceURL retrieves the registered URL for a given service name.
func (c *Coordinator) getServiceURL(serviceName string) (string, bool) {
	c.mu.Lock()
	defer c.mu.Unlock()
	url, exists := c.services[serviceName]
	return url, exists
}

// updateTransactionStatus safely updates the status of a transaction.
func (c *Coordinator) updateTransactionStatus(txID string, status string) {
	c.mu.Lock()
	defer c.mu.Unlock()

	if tx, ok := c.transactions[txID]; ok {
		tx.Status = status
	}
}