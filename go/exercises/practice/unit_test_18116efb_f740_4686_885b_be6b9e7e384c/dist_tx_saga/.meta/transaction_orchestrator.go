package dist_tx_saga

import (
	"errors"
	"sync"
)

type TxStatus string

const (
	Committed TxStatus = "Committed"
	Aborted   TxStatus = "Aborted"
)

type Orchestrator struct {
	inventoryFunc            func(txID string) error
	paymentFunc              func(txID string) error
	shippingFunc             func(txID string) error
	compensateInventoryFunc  func(txID string) error
	compensatePaymentFunc    func(txID string) error
	compensateShippingFunc   func(txID string) error

	logLock              sync.Mutex
	transactionLog       map[string]TxStatus

	execLock             sync.Mutex
	executedTransactions map[string]bool
}

func NewOrchestrator() *Orchestrator {
	return &Orchestrator{
		transactionLog:       make(map[string]TxStatus),
		executedTransactions: make(map[string]bool),
	}
}

func (o *Orchestrator) SetInventoryFunc(f func(txID string) error) {
	o.inventoryFunc = f
}

func (o *Orchestrator) SetPaymentFunc(f func(txID string) error) {
	o.paymentFunc = f
}

func (o *Orchestrator) SetShippingFunc(f func(txID string) error) {
	o.shippingFunc = f
}

func (o *Orchestrator) SetCompensateInventoryFunc(f func(txID string) error) {
	o.compensateInventoryFunc = f
}

func (o *Orchestrator) SetCompensatePaymentFunc(f func(txID string) error) {
	o.compensatePaymentFunc = f
}

func (o *Orchestrator) SetCompensateShippingFunc(f func(txID string) error) {
	o.compensateShippingFunc = f
}

func (o *Orchestrator) ExecuteTransaction(txID string) error {
	// Idempotency check: if transaction already executed, return immediately.
	o.execLock.Lock()
	if o.executedTransactions[txID] {
		o.execLock.Unlock()
		return nil
	}
	// Mark transaction as executing to enforce idempotency.
	o.executedTransactions[txID] = true
	o.execLock.Unlock()

	// Track completed steps for potential compensation.
	var completedSteps []string

	// Step 1: Inventory
	if o.inventoryFunc != nil {
		if err := o.inventoryFunc(txID); err != nil {
			o.logTransaction(txID, Aborted)
			return err
		}
		completedSteps = append(completedSteps, "inventory")
	}

	// Step 2: Payment
	if o.paymentFunc != nil {
		if err := o.paymentFunc(txID); err != nil {
			// Compensate previously successful steps.
			if contains(completedSteps, "inventory") && o.compensateInventoryFunc != nil {
				_ = o.compensateInventoryFunc(txID)
			}
			o.logTransaction(txID, Aborted)
			return err
		}
		completedSteps = append(completedSteps, "payment")
	}

	// Step 3: Shipping
	if o.shippingFunc != nil {
		if err := o.shippingFunc(txID); err != nil {
			// Compensate in reverse order.
			if contains(completedSteps, "payment") && o.compensatePaymentFunc != nil {
				_ = o.compensatePaymentFunc(txID)
			}
			if contains(completedSteps, "inventory") && o.compensateInventoryFunc != nil {
				_ = o.compensateInventoryFunc(txID)
			}
			o.logTransaction(txID, Aborted)
			return err
		}
		completedSteps = append(completedSteps, "shipping")
	}

	o.logTransaction(txID, Committed)
	return nil
}

func contains(slice []string, item string) bool {
	for _, s := range slice {
		if s == item {
			return true
		}
	}
	return false
}

func (o *Orchestrator) logTransaction(txID string, status TxStatus) {
	o.logLock.Lock()
	defer o.logLock.Unlock()
	o.transactionLog[txID] = status
}

func (o *Orchestrator) GetTransactionStatus(txID string) (TxStatus, error) {
	o.logLock.Lock()
	defer o.logLock.Unlock()
	status, ok := o.transactionLog[txID]
	if !ok {
		return "", errors.New("transaction not found")
	}
	return status, nil
}