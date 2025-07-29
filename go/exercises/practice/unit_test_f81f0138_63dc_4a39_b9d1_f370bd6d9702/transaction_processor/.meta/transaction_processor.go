package transaction_processor

import (
	"errors"
	"sync"
)

var (
	ErrAccountNotFound        = errors.New("account not found")
	ErrInsufficientFunds     = errors.New("insufficient funds")
	ErrDuplicateTransactionID = errors.New("duplicate transaction ID")
	ErrInvalidAmount         = errors.New("invalid amount")
)

type Transaction struct {
	ID     int
	From   int
	To     int
	Amount int
}

type TransactionLog struct {
	Transaction Transaction
	Success     bool
	Error       error
}

type TransactionProcessor struct {
	accounts      map[int]int
	accountsLock  sync.RWMutex
	processedTx   map[int]bool
	processedLock sync.RWMutex
	logs          []TransactionLog
	logsLock      sync.Mutex
}

func NewTransactionProcessor() *TransactionProcessor {
	return &TransactionProcessor{
		accounts:    make(map[int]int),
		processedTx: make(map[int]bool),
		logs:        make([]TransactionLog, 0),
	}
}

func (tp *TransactionProcessor) InitializeAccounts(initialBalances map[int]int) {
	tp.accountsLock.Lock()
	defer tp.accountsLock.Unlock()
	
	for id, balance := range initialBalances {
		tp.accounts[id] = balance
	}
}

func (tp *TransactionProcessor) ProcessTransaction(tx Transaction) error {
	if tx.Amount <= 0 {
		tp.logTransaction(tx, false, ErrInvalidAmount)
		return ErrInvalidAmount
	}

	tp.processedLock.RLock()
	if tp.processedTx[tx.ID] {
		tp.processedLock.RUnlock()
		tp.logTransaction(tx, false, ErrDuplicateTransactionID)
		return ErrDuplicateTransactionID
	}
	tp.processedLock.RUnlock()

	tp.accountsLock.Lock()
	defer tp.accountsLock.Unlock()

	fromBalance, fromExists := tp.accounts[tx.From]
	if !fromExists {
		tp.logTransaction(tx, false, ErrAccountNotFound)
		return ErrAccountNotFound
	}

	_, toExists := tp.accounts[tx.To]
	if !toExists {
		tp.logTransaction(tx, false, ErrAccountNotFound)
		return ErrAccountNotFound
	}

	if fromBalance < tx.Amount {
		tp.logTransaction(tx, false, ErrInsufficientFunds)
		return ErrInsufficientFunds
	}

	tp.processedLock.Lock()
	tp.processedTx[tx.ID] = true
	tp.processedLock.Unlock()

	tp.accounts[tx.From] -= tx.Amount
	tp.accounts[tx.To] += tx.Amount

	tp.logTransaction(tx, true, nil)
	return nil
}

func (tp *TransactionProcessor) GetBalance(accountID int) (int, error) {
	tp.accountsLock.RLock()
	defer tp.accountsLock.RUnlock()

	balance, exists := tp.accounts[accountID]
	if !exists {
		return 0, ErrAccountNotFound
	}
	return balance, nil
}

func (tp *TransactionProcessor) GetTransactionLog() []TransactionLog {
	tp.logsLock.Lock()
	defer tp.logsLock.Unlock()

	logs := make([]TransactionLog, len(tp.logs))
	copy(logs, tp.logs)
	return logs
}

func (tp *TransactionProcessor) logTransaction(tx Transaction, success bool, err error) {
	tp.logsLock.Lock()
	defer tp.logsLock.Unlock()

	tp.logs = append(tp.logs, TransactionLog{
		Transaction: tx,
		Success:     success,
		Error:       err,
	})
}