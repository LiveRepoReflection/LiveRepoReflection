package dtc_bank

import (
	"errors"
	"sync"
	"time"
)

const (
	ResponsePrepared = "Prepared"
	ResponseReadOnly = "ReadOnly"
	ResponseAborted  = "Aborted"
)

type Operation struct {
	AccountID string
	Amount    int
}

type BankService interface {
	Prepare(transactionID string, operations []Operation) (string, error)
	Commit(transactionID string) error
	Rollback(transactionID string) error
	GetBalance(accountID string) (int, error)
}

// MockBankService simulates a bank service for testing.
type MockBankService struct {
	// Configuration for simulating behavior.
	PrepareResponse string
	PrepareError    error
	CommitError     error
	RollbackError   error

	// Simulate network delay.
	Delay time.Duration

	mu              sync.Mutex
	PreparedTxIDs   map[string]bool
	CommittedTxIDs  map[string]bool
	RolledbackTxIDs map[string]bool
	Balance         map[string]int
}

func NewMockBankService() *MockBankService {
	return &MockBankService{
		PreparedTxIDs:   make(map[string]bool),
		CommittedTxIDs:  make(map[string]bool),
		RolledbackTxIDs: make(map[string]bool),
		Balance:         make(map[string]int),
		Delay:           10 * time.Millisecond,
		// Default prepare response.
		PrepareResponse: ResponsePrepared,
	}
}

func (m *MockBankService) Prepare(transactionID string, operations []Operation) (string, error) {
	time.Sleep(m.Delay)
	if m.PrepareError != nil {
		return "", m.PrepareError
	}
	// Check for sufficient funds on withdrawal operations.
	for _, op := range operations {
		if op.Amount < 0 {
			m.mu.Lock()
			balance, ok := m.Balance[op.AccountID]
			m.mu.Unlock()
			if !ok {
				balance = 0
			}
			if balance+op.Amount < 0 {
				return ResponseAborted, errors.New("insufficient funds")
			}
		}
	}
	m.mu.Lock()
	m.PreparedTxIDs[transactionID] = true
	m.mu.Unlock()
	return m.PrepareResponse, nil
}

func (m *MockBankService) Commit(transactionID string) error {
	time.Sleep(m.Delay)
	if m.CommitError != nil {
		return m.CommitError
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	// Only commit if the transaction was prepared.
	if !m.PreparedTxIDs[transactionID] {
		return errors.New("transaction not prepared")
	}
	m.CommittedTxIDs[transactionID] = true
	return nil
}

func (m *MockBankService) Rollback(transactionID string) error {
	time.Sleep(m.Delay)
	if m.RollbackError != nil {
		return m.RollbackError
	}
	m.mu.Lock()
	defer m.mu.Unlock()
	m.RolledbackTxIDs[transactionID] = true
	return nil
}

func (m *MockBankService) GetBalance(accountID string) (int, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	balance, ok := m.Balance[accountID]
	if !ok {
		return 0, nil
	}
	return balance, nil
}