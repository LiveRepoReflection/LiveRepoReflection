package tx_processor

import (
	"errors"
	"fmt"
	"sync"
	"sync/atomic"
)

// Transaction represents a financial transaction in the system.
type Transaction struct {
	AccountID     string
	Amount        int64 // Can be positive (deposit) or negative (withdrawal)
	TransactionID string // Unique identifier for each transaction
}

// TransactionProcessor handles transaction processing.
type TransactionProcessor struct {
	// mu protects access to the accounts map
	mu sync.RWMutex
	// accounts stores the current balance for each account
	accounts map[string]int64
	// accountLocks provides a per-account mutex for transaction ordering
	accountLocks map[string]*sync.Mutex
	// accountLocksLock protects the accountLocks map
	accountLocksLock sync.RWMutex
	// processedTxs tracks all processed transaction IDs
	processedTxs sync.Map
	// errorCount tracks the total number of errors
	errorCount int64
}

// txError represents an error in transaction processing.
type txError struct {
	message string
}

// Error implements the error interface.
func (e *txError) Error() string {
	return e.message
}

// NewTransactionProcessor creates a new transaction processor with the given initial balances.
func NewTransactionProcessor(initialBalances map[string]int64) *TransactionProcessor {
	accounts := make(map[string]int64, len(initialBalances))
	accountLocks := make(map[string]*sync.Mutex, len(initialBalances))

	// Copy initial balances to avoid modifying the input map
	for id, balance := range initialBalances {
		accounts[id] = balance
		accountLocks[id] = &sync.Mutex{}
	}

	return &TransactionProcessor{
		accounts:     accounts,
		accountLocks: accountLocks,
		errorCount:   0,
	}
}

// getAccountLock gets or creates a mutex for the specified account.
func (tp *TransactionProcessor) getAccountLock(accountID string) (*sync.Mutex, bool) {
	// First try to get the lock without writing
	tp.accountLocksLock.RLock()
	lock, exists := tp.accountLocks[accountID]
	tp.accountLocksLock.RUnlock()

	if exists {
		return lock, true
	}

	// If the account doesn't exist, don't create a new lock
	tp.mu.RLock()
	_, accountExists := tp.accounts[accountID]
	tp.mu.RUnlock()

	if !accountExists {
		return nil, false
	}

	// If the account exists but the lock doesn't, create a new lock
	tp.accountLocksLock.Lock()
	defer tp.accountLocksLock.Unlock()

	// Check again in case another goroutine created the lock while we were waiting
	lock, exists = tp.accountLocks[accountID]
	if exists {
		return lock, true
	}

	// Create a new lock for this account
	lock = &sync.Mutex{}
	tp.accountLocks[accountID] = lock
	return lock, true
}

// SubmitTransaction submits a transaction for processing.
func (tp *TransactionProcessor) SubmitTransaction(tx Transaction) error {
	// Validate transaction
	if tx.AccountID == "" {
		atomic.AddInt64(&tp.errorCount, 1)
		return &txError{"account ID cannot be empty"}
	}
	if tx.TransactionID == "" {
		atomic.AddInt64(&tp.errorCount, 1)
		return &txError{"transaction ID cannot be empty"}
	}

	// Check if transaction has already been processed
	if _, exists := tp.processedTxs.Load(tx.TransactionID); exists {
		atomic.AddInt64(&tp.errorCount, 1)
		return &txError{fmt.Sprintf("duplicate transaction ID: %s", tx.TransactionID)}
	}

	// Get account lock
	accountLock, exists := tp.getAccountLock(tx.AccountID)
	if !exists {
		atomic.AddInt64(&tp.errorCount, 1)
		return &txError{fmt.Sprintf("account not found: %s", tx.AccountID)}
	}

	// Lock the specific account to ensure transactions for this account
	// are processed in order
	accountLock.Lock()
	defer accountLock.Unlock()

	// Check if account exists and get current balance
	tp.mu.RLock()
	balance, exists := tp.accounts[tx.AccountID]
	tp.mu.RUnlock()

	if !exists {
		atomic.AddInt64(&tp.errorCount, 1)
		return &txError{fmt.Sprintf("account not found: %s", tx.AccountID)}
	}

	// Check if transaction would cause a negative balance
	if tx.Amount < 0 && balance+tx.Amount < 0 {
		atomic.AddInt64(&tp.errorCount, 1)
		return &txError{fmt.Sprintf("insufficient funds in account %s: %d < %d", tx.AccountID, balance, -tx.Amount)}
	}

	// Check for int64 overflow on deposit
	if tx.Amount > 0 && balance > (0x7FFFFFFFFFFFFFFF-tx.Amount) {
		atomic.AddInt64(&tp.errorCount, 1)
		return &txError{fmt.Sprintf("balance overflow for account %s", tx.AccountID)}
	}

	// Update balance
	tp.mu.Lock()
	tp.accounts[tx.AccountID] = balance + tx.Amount
	tp.mu.Unlock()

	// Mark transaction as processed
	tp.processedTxs.Store(tx.TransactionID, true)

	return nil
}

// GetBalance returns the current balance for an account.
func (tp *TransactionProcessor) GetBalance(accountID string) (int64, error) {
	tp.mu.RLock()
	balance, exists := tp.accounts[accountID]
	tp.mu.RUnlock()

	if !exists {
		return 0, errors.New("account not found")
	}

	return balance, nil
}

// GetErrorCount returns the total number of transaction processing errors.
func (tp *TransactionProcessor) GetErrorCount() int {
	return int(atomic.LoadInt64(&tp.errorCount))
}