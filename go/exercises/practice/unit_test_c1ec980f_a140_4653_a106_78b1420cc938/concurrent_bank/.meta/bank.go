package concurrent_bank

import (
	"encoding/json"
	"errors"
	"os"
	"sync"
	"time"
)

type Account struct {
	ID      string
	Balance int
	mu      sync.Mutex
}

type TransactionLog struct {
	Timestamp       time.Time
	TransactionType string
	FromAccount     string
	ToAccount       string
	Amount          int
	Status          string
	Error          string
}

type Bank struct {
	accounts map[string]*Account
	logs     []TransactionLog
	logMu    sync.Mutex
	snapMu   sync.Mutex
}

func NewBank(initialBalances map[string]int) *Bank {
	accounts := make(map[string]*Account)
	for id, balance := range initialBalances {
		accounts[id] = &Account{
			ID:      id,
			Balance: balance,
		}
	}
	return &Bank{
		accounts: accounts,
		logs:     make([]TransactionLog, 0),
	}
}

func (b *Bank) Deposit(accountID string, amount int) error {
	if amount <= 0 {
		return errors.New("amount must be positive")
	}

	account, exists := b.accounts[accountID]
	if !exists {
		b.logTransaction("deposit", accountID, "", amount, "failed", "account not found")
		return errors.New("account not found")
	}

	account.mu.Lock()
	defer account.mu.Unlock()

	account.Balance += amount
	b.logTransaction("deposit", accountID, "", amount, "success", "")
	return nil
}

func (b *Bank) Withdraw(accountID string, amount int) error {
	if amount <= 0 {
		return errors.New("amount must be positive")
	}

	account, exists := b.accounts[accountID]
	if !exists {
		b.logTransaction("withdrawal", accountID, "", amount, "failed", "account not found")
		return errors.New("account not found")
	}

	account.mu.Lock()
	defer account.mu.Unlock()

	if account.Balance < amount {
		b.logTransaction("withdrawal", accountID, "", amount, "failed", "insufficient funds")
		return errors.New("insufficient funds")
	}

	account.Balance -= amount
	b.logTransaction("withdrawal", accountID, "", amount, "success", "")
	return nil
}

func (b *Bank) Transfer(fromAccountID, toAccountID string, amount int) error {
	if amount <= 0 {
		return errors.New("amount must be positive")
	}

	fromAccount, exists := b.accounts[fromAccountID]
	if !exists {
		b.logTransaction("transfer", fromAccountID, toAccountID, amount, "failed", "from account not found")
		return errors.New("from account not found")
	}

	toAccount, exists := b.accounts[toAccountID]
	if !exists {
		b.logTransaction("transfer", fromAccountID, toAccountID, amount, "failed", "to account not found")
		return errors.New("to account not found")
	}

	// Lock ordering to prevent deadlocks
	if fromAccountID < toAccountID {
		fromAccount.mu.Lock()
		toAccount.mu.Lock()
	} else {
		toAccount.mu.Lock()
		fromAccount.mu.Lock()
	}
	defer fromAccount.mu.Unlock()
	defer toAccount.mu.Unlock()

	if fromAccount.Balance < amount {
		b.logTransaction("transfer", fromAccountID, toAccountID, amount, "failed", "insufficient funds")
		return errors.New("insufficient funds")
	}

	fromAccount.Balance -= amount
	toAccount.Balance += amount
	b.logTransaction("transfer", fromAccountID, toAccountID, amount, "success", "")
	return nil
}

func (b *Bank) GetBalance(accountID string) (int, error) {
	account, exists := b.accounts[accountID]
	if !exists {
		return 0, errors.New("account not found")
	}

	account.mu.Lock()
	defer account.mu.Unlock()

	return account.Balance, nil
}

func (b *Bank) logTransaction(tType, from, to string, amount int, status, errMsg string) {
	b.logMu.Lock()
	defer b.logMu.Unlock()

	log := TransactionLog{
		Timestamp:       time.Now(),
		TransactionType: tType,
		FromAccount:     from,
		ToAccount:       to,
		Amount:          amount,
		Status:          status,
		Error:          errMsg,
	}

	b.logs = append(b.logs, log)
}

func (b *Bank) GetTransactionLogs() ([]TransactionLog, error) {
	b.logMu.Lock()
	defer b.logMu.Unlock()

	logs := make([]TransactionLog, len(b.logs))
	copy(logs, b.logs)
	return logs, nil
}

func (b *Bank) SaveSnapshot(filename string) error {
	b.snapMu.Lock()
	defer b.snapMu.Unlock()

	accounts := make(map[string]int)
	for id, acc := range b.accounts {
		acc.mu.Lock()
		accounts[id] = acc.Balance
		acc.mu.Unlock()
	}

	data, err := json.Marshal(accounts)
	if err != nil {
		return err
	}

	return os.WriteFile(filename, data, 0644)
}

func (b *Bank) LoadSnapshot(filename string) error {
	b.snapMu.Lock()
	defer b.snapMu.Unlock()

	data, err := os.ReadFile(filename)
	if err != nil {
		return err
	}

	var accounts map[string]int
	if err := json.Unmarshal(data, &accounts); err != nil {
		return err
	}

	b.accounts = make(map[string]*Account)
	for id, balance := range accounts {
		b.accounts[id] = &Account{
			ID:      id,
			Balance: balance,
		}
	}

	return nil
}