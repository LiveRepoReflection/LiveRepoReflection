package concurrent_bank

import (
	"os"
	"sync"
	"testing"
	"time"
)

func TestDepositConcurrent(t *testing.T) {
	// Initialize bank with test accounts
	accounts := map[string]int{
		"acc1": 1000,
		"acc2": 2000,
	}
	bank := NewBank(accounts)
	defer os.Remove("accounts_snapshot.json")

	var wg sync.WaitGroup
	iterations := 1000

	// Concurrent deposits
	wg.Add(iterations)
	for i := 0; i < iterations; i++ {
		go func() {
			defer wg.Done()
			err := bank.Deposit("acc1", 10)
			if err != nil {
				t.Errorf("Deposit failed: %v", err)
			}
		}()
	}
	wg.Wait()

	balance, err := bank.GetBalance("acc1")
	if err != nil {
		t.Fatalf("GetBalance failed: %v", err)
	}

	expected := 1000 + (10 * iterations)
	if balance != expected {
		t.Errorf("Expected balance %d, got %d", expected, balance)
	}
}

func TestWithdrawalConcurrent(t *testing.T) {
	accounts := map[string]int{
		"acc1": 10000,
	}
	bank := NewBank(accounts)
	defer os.Remove("accounts_snapshot.json")

	var wg sync.WaitGroup
	iterations := 1000

	wg.Add(iterations)
	for i := 0; i < iterations; i++ {
		go func() {
			defer wg.Done()
			err := bank.Withdraw("acc1", 5)
			if err != nil {
				t.Errorf("Withdrawal failed: %v", err)
			}
		}()
	}
	wg.Wait()

	balance, err := bank.GetBalance("acc1")
	if err != nil {
		t.Fatalf("GetBalance failed: %v", err)
	}

	expected := 10000 - (5 * iterations)
	if balance != expected {
		t.Errorf("Expected balance %d, got %d", expected, balance)
	}
}

func TestTransferConcurrent(t *testing.T) {
	accounts := map[string]int{
		"acc1": 10000,
		"acc2": 0,
	}
	bank := NewBank(accounts)
	defer os.Remove("accounts_snapshot.json")

	var wg sync.WaitGroup
	iterations := 1000

	wg.Add(iterations)
	for i := 0; i < iterations; i++ {
		go func() {
			defer wg.Done()
			err := bank.Transfer("acc1", "acc2", 1)
			if err != nil {
				t.Errorf("Transfer failed: %v", err)
			}
		}()
	}
	wg.Wait()

	balance1, err := bank.GetBalance("acc1")
	if err != nil {
		t.Fatalf("GetBalance failed for acc1: %v", err)
	}

	balance2, err := bank.GetBalance("acc2")
	if err != nil {
		t.Fatalf("GetBalance failed for acc2: %v", err)
	}

	total := balance1 + balance2
	if total != 10000 {
		t.Errorf("Total amount changed during transfers, expected 10000, got %d", total)
	}
}

func TestInsufficientFunds(t *testing.T) {
	accounts := map[string]int{
		"acc1": 100,
	}
	bank := NewBank(accounts)
	defer os.Remove("accounts_snapshot.json")

	err := bank.Withdraw("acc1", 200)
	if err == nil {
		t.Error("Expected error for insufficient funds, got nil")
	}

	balance, _ := bank.GetBalance("acc1")
	if balance != 100 {
		t.Errorf("Balance should remain unchanged, got %d", balance)
	}
}

func TestNonexistentAccount(t *testing.T) {
	bank := NewBank(map[string]int{})
	defer os.Remove("accounts_snapshot.json")

	err := bank.Deposit("nonexistent", 100)
	if err == nil {
		t.Error("Expected error for nonexistent account, got nil")
	}
}

func TestSnapshot(t *testing.T) {
	accounts := map[string]int{
		"acc1": 1000,
		"acc2": 2000,
	}
	bank := NewBank(accounts)
	defer os.Remove("accounts_snapshot.json")

	err := bank.SaveSnapshot("accounts_snapshot.json")
	if err != nil {
		t.Fatalf("SaveSnapshot failed: %v", err)
	}

	newBank := NewBank(map[string]int{})
	err = newBank.LoadSnapshot("accounts_snapshot.json")
	if err != nil {
		t.Fatalf("LoadSnapshot failed: %v", err)
	}

	for acc, balance := range accounts {
		loadedBalance, err := newBank.GetBalance(acc)
		if err != nil {
			t.Errorf("GetBalance failed for %s: %v", acc, err)
		}
		if loadedBalance != balance {
			t.Errorf("For account %s, expected balance %d, got %d", acc, balance, loadedBalance)
		}
	}
}

func TestTransactionLog(t *testing.T) {
	accounts := map[string]int{
		"acc1": 1000,
	}
	bank := NewBank(accounts)
	defer os.Remove("accounts_snapshot.json")
	defer os.Remove("transaction.log")

	// Perform multiple operations
	bank.Deposit("acc1", 100)
	bank.Withdraw("acc1", 50)
	bank.Transfer("acc1", "acc2", 25)

	logs, err := bank.GetTransactionLogs()
	if err != nil {
		t.Fatalf("GetTransactionLogs failed: %v", err)
	}

	if len(logs) != 3 {
		t.Errorf("Expected 3 transaction logs, got %d", len(logs))
	}

	// Verify log contents
	for _, log := range logs {
		if log.Timestamp.IsZero() {
			t.Error("Log timestamp is zero")
		}
		if log.TransactionType == "" {
			t.Error("Log transaction type is empty")
		}
	}
}

func TestDeadlockDetection(t *testing.T) {
	accounts := map[string]int{
		"acc1": 1000,
		"acc2": 1000,
	}
	bank := NewBank(accounts)
	defer os.Remove("accounts_snapshot.json")

	// Setup deadlock scenario
	var wg sync.WaitGroup
	wg.Add(2)

	go func() {
		defer wg.Done()
		bank.Transfer("acc1", "acc2", 100)
	}()

	go func() {
		defer wg.Done()
		bank.Transfer("acc2", "acc1", 100)
	}()

	// Wait with timeout
	done := make(chan struct{})
	go func() {
		wg.Wait()
		close(done)
	}()

	select {
	case <-done:
		// Test passed, no deadlock
	case <-time.After(2 * time.Second):
		t.Error("Potential deadlock detected")
	}
}