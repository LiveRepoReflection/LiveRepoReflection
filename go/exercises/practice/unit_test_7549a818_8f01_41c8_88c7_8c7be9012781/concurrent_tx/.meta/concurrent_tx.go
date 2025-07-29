package concurrent_tx

import (
	"fmt"
	"sync"
	"time"
)

// Common errors
var (
	ErrAccountNotFound     = fmt.Errorf("account not found")
	ErrAccountExists       = fmt.Errorf("account already exists")
	ErrInsufficientFunds   = fmt.Errorf("insufficient funds")
	ErrTransactionConflict = fmt.Errorf("transaction conflict")
	ErrInvalidAmount       = fmt.Errorf("invalid amount")
	ErrTransactionClosed   = fmt.Errorf("transaction already closed")
)

// Account represents a bank account with a balance
type Account struct {
	ID      string
	Balance int
	mu      sync.RWMutex // Mutex for this specific account
}

// Database is the main in-memory database structure
type Database struct {
	accounts     map[string]*Account
	mu           sync.RWMutex // Mutex for the accounts map
	txCounter    int64
	txCounterMu  sync.Mutex
	lockTimeout  time.Duration
}

// Transaction represents an ongoing database transaction
type Transaction interface {
	Deposit(accountID string, amount int) error
	Withdraw(accountID string, amount int) error
	Commit() error
	Rollback() error
}

// TransactionImpl is the concrete implementation of the Transaction interface
type TransactionImpl struct {
	db               *Database
	id               int64
	operations       []*Operation
	accountChanges   map[string]int
	lockedAccounts   map[string]*Account
	active           bool
	mu               sync.Mutex // Protects the transaction state
}

// Operation represents a single operation within a transaction
type Operation struct {
	AccountID string
	OpType    string // "deposit" or "withdraw"
	Amount    int
}

// NewDatabase creates a new database instance
func NewDatabase() *Database {
	return &Database{
		accounts:    make(map[string]*Account),
		lockTimeout: 500 * time.Millisecond,
	}
}

// CreateAccount creates a new account with the specified ID and initial balance
func (db *Database) CreateAccount(accountID string, initialBalance int) error {
	db.mu.Lock()
	defer db.mu.Unlock()

	if _, exists := db.accounts[accountID]; exists {
		return ErrAccountExists
	}

	db.accounts[accountID] = &Account{
		ID:      accountID,
		Balance: initialBalance,
	}

	return nil
}

// GetBalance retrieves the current balance of the specified account
func (db *Database) GetBalance(accountID string) (int, error) {
	db.mu.RLock()
	account, exists := db.accounts[accountID]
	db.mu.RUnlock()

	if !exists {
		return 0, ErrAccountNotFound
	}

	account.mu.RLock()
	defer account.mu.RUnlock()
	return account.Balance, nil
}

// getNextTxID generates a unique transaction ID
func (db *Database) getNextTxID() int64 {
	db.txCounterMu.Lock()
	defer db.txCounterMu.Unlock()
	
	db.txCounter++
	return db.txCounter
}

// BeginTransaction starts a new transaction
func (db *Database) BeginTransaction() Transaction {
	return &TransactionImpl{
		db:             db,
		id:             db.getNextTxID(),
		operations:     make([]*Operation, 0),
		accountChanges: make(map[string]int),
		lockedAccounts: make(map[string]*Account),
		active:         true,
	}
}

// Deposit adds funds to an account within the transaction context
func (tx *TransactionImpl) Deposit(accountID string, amount int) error {
	tx.mu.Lock()
	defer tx.mu.Unlock()

	if !tx.active {
		return ErrTransactionClosed
	}

	// Record the operation
	tx.operations = append(tx.operations, &Operation{
		AccountID: accountID,
		OpType:    "deposit",
		Amount:    amount,
	})

	// Update the account changes map
	tx.accountChanges[accountID] = tx.accountChanges[accountID] + amount

	return nil
}

// Withdraw removes funds from an account within the transaction context
func (tx *TransactionImpl) Withdraw(accountID string, amount int) error {
	tx.mu.Lock()
	defer tx.mu.Unlock()

	if !tx.active {
		return ErrTransactionClosed
	}

	// Check if account exists
	tx.db.mu.RLock()
	account, exists := tx.db.accounts[accountID]
	tx.db.mu.RUnlock()

	if !exists {
		return ErrAccountNotFound
	}

	// Calculate new balance after all operations in this transaction
	newBalance := account.Balance + tx.accountChanges[accountID] - amount

	// Check if there are sufficient funds
	if newBalance < 0 {
		return ErrInsufficientFunds
	}

	// Record the operation
	tx.operations = append(tx.operations, &Operation{
		AccountID: accountID,
		OpType:    "withdraw",
		Amount:    amount,
	})

	// Update the account changes map
	tx.accountChanges[accountID] = tx.accountChanges[accountID] - amount

	return nil
}

// lockAccounts attempts to acquire locks on all affected accounts
// It uses a timeout and ordered locking to prevent deadlocks
func (tx *TransactionImpl) lockAccounts() error {
	// Get all unique account IDs affected by this transaction
	accountIDs := make([]string, 0, len(tx.accountChanges))
	for accountID := range tx.accountChanges {
		accountIDs = append(accountIDs, accountID)
	}

	// Sort account IDs to avoid deadlocks (always lock in the same order)
	sortStringSlice(accountIDs)

	// Try to acquire locks with a timeout
	deadline := time.Now().Add(tx.db.lockTimeout)

	// Lock accounts in order
	for _, accountID := range accountIDs {
		tx.db.mu.RLock()
		account, exists := tx.db.accounts[accountID]
		tx.db.mu.RUnlock()

		if !exists {
			// Unlock all previously locked accounts
			for _, lockedAccount := range tx.lockedAccounts {
				lockedAccount.mu.Unlock()
			}
			return ErrAccountNotFound
		}

		// Try to acquire the lock with timeout
		acquired := make(chan struct{})
		go func() {
			account.mu.Lock()
			close(acquired)
		}()

		select {
		case <-acquired:
			// Lock acquired
			tx.lockedAccounts[accountID] = account
		case <-time.After(time.Until(deadline)):
			// Timeout - unlock all previously locked accounts
			for _, lockedAccount := range tx.lockedAccounts {
				lockedAccount.mu.Unlock()
			}
			return fmt.Errorf("failed to acquire locks in time - possible deadlock avoided")
		}
	}

	return nil
}

// unlockAccounts releases all locks acquired by this transaction
func (tx *TransactionImpl) unlockAccounts() {
	for _, account := range tx.lockedAccounts {
		account.mu.Unlock()
	}
	tx.lockedAccounts = make(map[string]*Account)
}

// Commit applies all changes made within the transaction to the main database
func (tx *TransactionImpl) Commit() error {
	tx.mu.Lock()
	defer tx.mu.Unlock()

	if !tx.active {
		return ErrTransactionClosed
	}

	// Lock all affected accounts
	err := tx.lockAccounts()
	if err != nil {
		return err
	}
	defer tx.unlockAccounts()

	// Verify all operations are still valid
	for accountID, change := range tx.accountChanges {
		account := tx.lockedAccounts[accountID]
		if account.Balance+change < 0 {
			return ErrInsufficientFunds
		}
	}

	// Apply all changes
	for accountID, change := range tx.accountChanges {
		account := tx.lockedAccounts[accountID]
		account.Balance += change
	}

	// Mark transaction as inactive
	tx.active = false
	return nil
}

// Rollback discards all changes made within the transaction
func (tx *TransactionImpl) Rollback() error {
	tx.mu.Lock()
	defer tx.mu.Unlock()

	if !tx.active {
		return ErrTransactionClosed
	}

	// Mark transaction as inactive
	tx.active = false
	return nil
}

// sortStringSlice sorts a slice of strings in place
func sortStringSlice(s []string) {
	for i := 0; i < len(s); i++ {
		for j := i + 1; j < len(s); j++ {
			if s[i] > s[j] {
				s[i], s[j] = s[j], s[i]
			}
		}
	}
}