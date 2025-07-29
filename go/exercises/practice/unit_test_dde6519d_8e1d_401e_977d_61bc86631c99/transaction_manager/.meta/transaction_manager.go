package transaction_manager

import (
	"errors"
	"sync"
)

// Transaction states
const (
	ACTIVE    = "ACTIVE"
	PREPARED  = "PREPARED"
	COMMITTED = "COMMITTED"
	ABORTED   = "ABORTED"
)

// Common errors
var (
	ErrTransactionNotFound      = errors.New("transaction not found")
	ErrTransactionAlreadyExists = errors.New("transaction already exists")
	ErrServiceNodeBusy          = errors.New("service node is already participating in another transaction")
	ErrInvalidTransactionState  = errors.New("invalid transaction state for this operation")
	ErrNoParticipants           = errors.New("transaction has no participants")
	ErrPrepareFailed            = errors.New("prepare phase failed, some participants voted to abort")
)

// Transaction represents a distributed transaction
type Transaction struct {
	ID            int
	State         string
	Participants  map[int]bool // Maps service node ID to participation status
	prepareVotes  map[int]bool // Records the prepare votes from each participant
	preparePassed bool         // Indicates if all participants voted to commit
}

// TransactionManager handles coordination of distributed transactions
type TransactionManager struct {
	transactions      map[int]*Transaction
	serviceNodeLocks  map[int]*sync.Mutex // To prevent a service node from participating in multiple transactions
	transactionsMutex sync.RWMutex        // Global mutex for the transactions map
	serviceNodesMutex sync.RWMutex        // Global mutex for the service node locks map
	PrepareVoteFunc   func(transactionID, serviceNode int) bool
}

// NewTransactionManager creates a new transaction manager
func NewTransactionManager() *TransactionManager {
	return &TransactionManager{
		transactions:     make(map[int]*Transaction),
		serviceNodeLocks: make(map[int]*sync.Mutex),
		PrepareVoteFunc:  func(transactionID, serviceNode int) bool { return true },
	}
}

// Begin initiates a new transaction
func (tm *TransactionManager) Begin(transactionID int) error {
	tm.transactionsMutex.Lock()
	defer tm.transactionsMutex.Unlock()

	// Check if the transaction already exists
	if _, exists := tm.transactions[transactionID]; exists {
		return ErrTransactionAlreadyExists
	}

	// Create a new transaction
	tm.transactions[transactionID] = &Transaction{
		ID:           transactionID,
		State:        ACTIVE,
		Participants: make(map[int]bool),
		prepareVotes: make(map[int]bool),
	}

	return nil
}

// Participate adds a service node to a transaction
func (tm *TransactionManager) Participate(transactionID, serviceNode int) error {
	// First, check if the transaction exists
	tm.transactionsMutex.RLock()
	transaction, exists := tm.transactions[transactionID]
	if !exists {
		tm.transactionsMutex.RUnlock()
		return ErrTransactionNotFound
	}

	// Check if the transaction is in a state where participation is allowed
	if transaction.State != ACTIVE {
		tm.transactionsMutex.RUnlock()
		return ErrInvalidTransactionState
	}
	tm.transactionsMutex.RUnlock()

	// Try to acquire the service node lock
	tm.serviceNodesMutex.Lock()
	nodeLock, exists := tm.serviceNodeLocks[serviceNode]
	if !exists {
		nodeLock = &sync.Mutex{}
		tm.serviceNodeLocks[serviceNode] = nodeLock
	}
	tm.serviceNodesMutex.Unlock()

	// Try to lock the service node
	if !nodeLock.TryLock() {
		return ErrServiceNodeBusy
	}

	// Successfully locked the service node, add it to the transaction participants
	tm.transactionsMutex.Lock()
	defer tm.transactionsMutex.Unlock()

	// Double-check that the transaction still exists and is still active
	transaction, exists = tm.transactions[transactionID]
	if !exists {
		nodeLock.Unlock() // Release the service node lock
		return ErrTransactionNotFound
	}

	if transaction.State != ACTIVE {
		nodeLock.Unlock() // Release the service node lock
		return ErrInvalidTransactionState
	}

	transaction.Participants[serviceNode] = true
	return nil
}

// Prepare initiates the prepare phase of the 2PC protocol
func (tm *TransactionManager) Prepare(transactionID int) error {
	// Get the transaction
	tm.transactionsMutex.Lock()
	transaction, exists := tm.transactions[transactionID]
	if !exists {
		tm.transactionsMutex.Unlock()
		return ErrTransactionNotFound
	}

	// Check if the transaction is in the right state
	if transaction.State != ACTIVE {
		tm.transactionsMutex.Unlock()
		return ErrInvalidTransactionState
	}

	// Check if there are any participants
	if len(transaction.Participants) == 0 {
		tm.transactionsMutex.Unlock()
		return ErrNoParticipants
	}

	// Change state to indicate prepare phase is in progress
	transaction.State = PREPARED
	transaction.prepareVotes = make(map[int]bool)
	tm.transactionsMutex.Unlock()

	// Collect votes from all participants
	allVoted := true
	for serviceNode := range transaction.Participants {
		vote := tm.PrepareVoteFunc(transactionID, serviceNode)
		tm.transactionsMutex.Lock()
		transaction.prepareVotes[serviceNode] = vote
		if !vote {
			allVoted = false
		}
		tm.transactionsMutex.Unlock()
	}

	tm.transactionsMutex.Lock()
	defer tm.transactionsMutex.Unlock()

	// If any participant voted to abort, abort the transaction
	if !allVoted {
		transaction.State = ABORTED
		transaction.preparePassed = false
		// Release all service node locks
		tm.releaseServiceNodeLocks(transaction)
		return ErrPrepareFailed
	}

	transaction.preparePassed = true
	return nil
}

// Commit initiates the commit phase of the 2PC protocol
func (tm *TransactionManager) Commit(transactionID int) error {
	tm.transactionsMutex.Lock()
	defer tm.transactionsMutex.Unlock()

	// Get the transaction
	transaction, exists := tm.transactions[transactionID]
	if !exists {
		return ErrTransactionNotFound
	}

	// Check if the transaction is already committed (idempotency)
	if transaction.State == COMMITTED {
		return nil
	}

	// Check if the transaction is in the right state
	if transaction.State != PREPARED || !transaction.preparePassed {
		return ErrInvalidTransactionState
	}

	// Change state to committed
	transaction.State = COMMITTED

	// Release all service node locks
	tm.releaseServiceNodeLocks(transaction)

	return nil
}

// Abort initiates the abort phase of the 2PC protocol
func (tm *TransactionManager) Abort(transactionID int) error {
	tm.transactionsMutex.Lock()
	defer tm.transactionsMutex.Unlock()

	// Get the transaction
	transaction, exists := tm.transactions[transactionID]
	if !exists {
		return ErrTransactionNotFound
	}

	// Check if the transaction is already aborted (idempotency)
	if transaction.State == ABORTED {
		return nil
	}

	// Change state to aborted
	transaction.State = ABORTED

	// Release all service node locks
	tm.releaseServiceNodeLocks(transaction)

	return nil
}

// GetTransactionState returns the current state of the transaction
func (tm *TransactionManager) GetTransactionState(transactionID int) string {
	tm.transactionsMutex.RLock()
	defer tm.transactionsMutex.RUnlock()

	transaction, exists := tm.transactions[transactionID]
	if !exists {
		return ""
	}

	return transaction.State
}

// Helper method to release all service node locks for a transaction
func (tm *TransactionManager) releaseServiceNodeLocks(transaction *Transaction) {
	tm.serviceNodesMutex.RLock()
	for serviceNode := range transaction.Participants {
		if nodeLock, exists := tm.serviceNodeLocks[serviceNode]; exists {
			nodeLock.Unlock()
		}
	}
	tm.serviceNodesMutex.RUnlock()
}