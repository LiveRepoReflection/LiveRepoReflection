package dist_tx

import (
	"errors"
	"sync"
)

type DTM struct {
	mu            sync.Mutex
	state         map[string]interface{}
	transactions  map[string]*Transaction
	serviceLocks  map[string]string // maps serviceID to txID
	shadowStates  map[string]map[string]interface{}
}

type Transaction struct {
	txID       string
	serviceIDs []string
	operations map[string][]func(map[string]interface{}) (map[string]interface{}, error)
	prepared   bool
}

func NewDTM() *DTM {
	return &DTM{
		state:        make(map[string]interface{}),
		transactions: make(map[string]*Transaction),
		serviceLocks: make(map[string]string),
		shadowStates: make(map[string]map[string]interface{}),
	}
}

func (dtm *DTM) RegisterTransaction(txID string, serviceIDs []string) error {
	dtm.mu.Lock()
	defer dtm.mu.Unlock()

	if _, exists := dtm.transactions[txID]; exists {
		return errors.New("transaction already exists")
	}

	for _, svcID := range serviceIDs {
		if lockedTxID, locked := dtm.serviceLocks[svcID]; locked && lockedTxID != txID {
			return errors.New("service already in another transaction")
		}
	}

	tx := &Transaction{
		txID:       txID,
		serviceIDs: serviceIDs,
		operations: make(map[string][]func(map[string]interface{}) (map[string]interface{}, error)),
		prepared:   false,
	}

	dtm.transactions[txID] = tx
	for _, svcID := range serviceIDs {
		dtm.serviceLocks[svcID] = txID
	}

	dtm.shadowStates[txID] = make(map[string]interface{})
	for k, v := range dtm.state {
		dtm.shadowStates[txID][k] = v
	}

	return nil
}

func (dtm *DTM) SubmitOperation(txID string, serviceID string, op func(map[string]interface{}) (map[string]interface{}, error)) error {
	dtm.mu.Lock()
	defer dtm.mu.Unlock()

	tx, exists := dtm.transactions[txID]
	if !exists {
		return errors.New("transaction does not exist")
	}

	if lockedTxID, locked := dtm.serviceLocks[serviceID]; !locked || lockedTxID != txID {
		return errors.New("service not registered in this transaction")
	}

	tx.operations[serviceID] = append(tx.operations[serviceID], op)
	return nil
}

func (dtm *DTM) CommitTransaction(txID string) error {
	dtm.mu.Lock()
	defer dtm.mu.Unlock()

	tx, exists := dtm.transactions[txID]
	if !exists {
		return errors.New("transaction does not exist")
	}

	// Phase 1: Prepare
	for _, svcID := range tx.serviceIDs {
		for _, op := range tx.operations[svcID] {
			newState, err := op(dtm.shadowStates[txID])
			if err != nil {
				return errors.New("operation failed during prepare phase")
			}
			dtm.shadowStates[txID] = newState
		}
	}
	tx.prepared = true

	// Phase 2: Commit
	dtm.state = dtm.shadowStates[txID]

	// Cleanup
	for _, svcID := range tx.serviceIDs {
		delete(dtm.serviceLocks, svcID)
	}
	delete(dtm.transactions, txID)
	delete(dtm.shadowStates, txID)

	return nil
}

func (dtm *DTM) AbortTransaction(txID string) error {
	dtm.mu.Lock()
	defer dtm.mu.Unlock()

	tx, exists := dtm.transactions[txID]
	if !exists {
		return errors.New("transaction does not exist")
	}

	// Release service locks
	for _, svcID := range tx.serviceIDs {
		delete(dtm.serviceLocks, svcID)
	}

	// Cleanup
	delete(dtm.transactions, txID)
	delete(dtm.shadowStates, txID)

	return nil
}

func (dtm *DTM) GetState() map[string]interface{} {
	dtm.mu.Lock()
	defer dtm.mu.Unlock()

	stateCopy := make(map[string]interface{})
	for k, v := range dtm.state {
		stateCopy[k] = v
	}
	return stateCopy
}