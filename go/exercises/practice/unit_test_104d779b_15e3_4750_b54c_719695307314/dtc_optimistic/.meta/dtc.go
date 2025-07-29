package dtc

import (
	"errors"
	"sync"
	"time"
)

type TransactionState int

const (
	Pending TransactionState = iota
	Committed
	Aborted
)

type Transaction struct {
	ID           int
	ExpectedVers map[int]int
	State        TransactionState
	mu           sync.Mutex
}

type DTC struct {
	serviceVersions map[int]int
	transactions    map[int]*Transaction
	mu             sync.RWMutex
	timeout        time.Duration
}

func NewDTC() *DTC {
	return &DTC{
		serviceVersions: make(map[int]int),
		transactions:    make(map[int]*Transaction),
	}
}

func NewDTCWithTimeout(timeout time.Duration) *DTC {
	dtc := NewDTC()
	dtc.timeout = timeout
	return dtc
}

func (d *DTC) BeginTransaction() int {
	d.mu.Lock()
	defer d.mu.Unlock()

	txID := len(d.transactions) + 1
	tx := &Transaction{
		ID:           txID,
		ExpectedVers: make(map[int]int),
		State:        Pending,
	}

	d.transactions[txID] = tx

	if d.timeout > 0 {
		go func() {
			time.Sleep(d.timeout)
			tx.mu.Lock()
			defer tx.mu.Unlock()
			if tx.State == Pending {
				tx.State = Aborted
			}
		}()
	}

	return txID
}

func (d *DTC) PrepareTransaction(txID int, serviceID int, expectedVersion int) error {
	d.mu.RLock()
	defer d.mu.RUnlock()

	tx, exists := d.transactions[txID]
	if !exists {
		return errors.New("transaction does not exist")
	}

	tx.mu.Lock()
	defer tx.mu.Unlock()

	if tx.State != Pending {
		return errors.New("transaction is not in pending state")
	}

	if _, exists := tx.ExpectedVers[serviceID]; exists {
		return errors.New("service already prepared in this transaction")
	}

	tx.ExpectedVers[serviceID] = expectedVersion
	return nil
}

func (d *DTC) CommitTransaction(txID int) bool {
	d.mu.Lock()
	defer d.mu.Unlock()

	tx, exists := d.transactions[txID]
	if !exists {
		return false
	}

	tx.mu.Lock()
	defer tx.mu.Unlock()

	if tx.State != Pending {
		return false
	}

	// Validate all expected versions
	for serviceID, expectedVersion := range tx.ExpectedVers {
		currentVersion, exists := d.serviceVersions[serviceID]
		if !exists {
			currentVersion = 0
		}
		if currentVersion != expectedVersion {
			tx.State = Aborted
			return false
		}
	}

	// Update all service versions
	for serviceID := range tx.ExpectedVers {
		d.serviceVersions[serviceID]++
	}

	tx.State = Committed
	return true
}

func (d *DTC) GetTransactionState(txID int) (TransactionState, error) {
	d.mu.RLock()
	defer d.mu.RUnlock()

	tx, exists := d.transactions[txID]
	if !exists {
		return Aborted, errors.New("transaction does not exist")
	}

	tx.mu.Lock()
	defer tx.mu.Unlock()

	return tx.State, nil
}