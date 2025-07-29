package transaction_processor

import (
	"errors"
	"sync"
	"testing"
	"time"
)

func TestTransactionProcessor(t *testing.T) {
	t.Run("SingleTransaction", func(t *testing.T) {
		processor := NewTransactionProcessor()
		accounts := map[int]int{
			1: 1000,
			2: 500,
		}
		processor.InitializeAccounts(accounts)

		tx := Transaction{
			ID:     1,
			From:   1,
			To:     2,
			Amount: 200,
		}

		err := processor.ProcessTransaction(tx)
		if err != nil {
			t.Fatalf("Expected no error, got %v", err)
		}

		balance1, err := processor.GetBalance(1)
		if err != nil {
			t.Fatal(err)
		}
		if balance1 != 800 {
			t.Errorf("Expected account 1 balance 800, got %d", balance1)
		}

		balance2, err := processor.GetBalance(2)
		if err != nil {
			t.Fatal(err)
		}
		if balance2 != 700 {
			t.Errorf("Expected account 2 balance 700, got %d", balance2)
		}
	})

	t.Run("ConcurrentTransactions", func(t *testing.T) {
		processor := NewTransactionProcessor()
		accounts := map[int]int{
			1: 1000,
			2: 500,
			3: 1500,
		}
		processor.InitializeAccounts(accounts)

		var wg sync.WaitGroup
		transactions := []Transaction{
			{ID: 1, From: 1, To: 2, Amount: 200},
			{ID: 2, From: 3, To: 1, Amount: 300},
			{ID: 3, From: 2, To: 3, Amount: 100},
		}

		for _, tx := range transactions {
			wg.Add(1)
			go func(tx Transaction) {
				defer wg.Done()
				err := processor.ProcessTransaction(tx)
				if err != nil {
					t.Errorf("Transaction %d failed: %v", tx.ID, err)
				}
			}(tx)
		}

		wg.Wait()

		expectedBalances := map[int]int{
			1: 1000 - 200 + 300,  // 1100
			2: 500 + 200 - 100,   // 600
			3: 1500 + 100 - 300,  // 1300
		}

		for accountID, expectedBalance := range expectedBalances {
			balance, err := processor.GetBalance(accountID)
			if err != nil {
				t.Fatal(err)
			}
			if balance != expectedBalance {
				t.Errorf("Account %d: expected balance %d, got %d", accountID, expectedBalance, balance)
			}
		}
	})

	t.Run("InsufficientFunds", func(t *testing.T) {
		processor := NewTransactionProcessor()
		accounts := map[int]int{
			1: 100,
			2: 500,
		}
		processor.InitializeAccounts(accounts)

		tx := Transaction{
			ID:     1,
			From:   1,
			To:     2,
			Amount: 200,
		}

		err := processor.ProcessTransaction(tx)
		if !errors.Is(err, ErrInsufficientFunds) {
			t.Errorf("Expected ErrInsufficientFunds, got %v", err)
		}
	})

	t.Run("NonexistentAccount", func(t *testing.T) {
		processor := NewTransactionProcessor()
		accounts := map[int]int{
			1: 1000,
		}
		processor.InitializeAccounts(accounts)

		tx := Transaction{
			ID:     1,
			From:   1,
			To:     999,
			Amount: 200,
		}

		err := processor.ProcessTransaction(tx)
		if !errors.Is(err, ErrAccountNotFound) {
			t.Errorf("Expected ErrAccountNotFound, got %v", err)
		}
	})

	t.Run("DuplicateTransactionID", func(t *testing.T) {
		processor := NewTransactionProcessor()
		accounts := map[int]int{
			1: 1000,
			2: 500,
		}
		processor.InitializeAccounts(accounts)

		tx1 := Transaction{
			ID:     1,
			From:   1,
			To:     2,
			Amount: 200,
		}

		tx2 := Transaction{
			ID:     1,
			From:   2,
			To:     1,
			Amount: 100,
		}

		err := processor.ProcessTransaction(tx1)
		if err != nil {
			t.Fatal(err)
		}

		err = processor.ProcessTransaction(tx2)
		if !errors.Is(err, ErrDuplicateTransactionID) {
			t.Errorf("Expected ErrDuplicateTransactionID, got %v", err)
		}
	})

	t.Run("NegativeAmount", func(t *testing.T) {
		processor := NewTransactionProcessor()
		accounts := map[int]int{
			1: 1000,
			2: 500,
		}
		processor.InitializeAccounts(accounts)

		tx := Transaction{
			ID:     1,
			From:   1,
			To:     2,
			Amount: -100,
		}

		err := processor.ProcessTransaction(tx)
		if !errors.Is(err, ErrInvalidAmount) {
			t.Errorf("Expected ErrInvalidAmount, got %v", err)
		}
	})

	t.Run("TransactionLog", func(t *testing.T) {
		processor := NewTransactionProcessor()
		accounts := map[int]int{
			1: 1000,
			2: 500,
		}
		processor.InitializeAccounts(accounts)

		transactions := []Transaction{
			{ID: 1, From: 1, To: 2, Amount: 200},
			{ID: 2, From: 1, To: 2, Amount: 1000}, // Should fail
			{ID: 3, From: 2, To: 1, Amount: 50},
		}

		for _, tx := range transactions {
			_ = processor.ProcessTransaction(tx)
		}

		logs := processor.GetTransactionLog()
		if len(logs) != 3 {
			t.Fatalf("Expected 3 log entries, got %d", len(logs))
		}

		if !logs[0].Success {
			t.Error("First transaction should be successful")
		}

		if logs[1].Success {
			t.Error("Second transaction should fail")
		}

		if !logs[2].Success {
			t.Error("Third transaction should be successful")
		}
	})

	t.Run("HighVolumePerformance", func(t *testing.T) {
		if testing.Short() {
			t.Skip("Skipping performance test in short mode")
		}

		processor := NewTransactionProcessor()
		numAccounts := 1000
		accounts := make(map[int]int)
		for i := 1; i <= numAccounts; i++ {
			accounts[i] = 10000
		}
		processor.InitializeAccounts(accounts)

		numTransactions := 10000
		var wg sync.WaitGroup
		start := time.Now()

		for i := 0; i < numTransactions; i++ {
			wg.Add(1)
			go func(id int) {
				defer wg.Done()
				tx := Transaction{
					ID:     id,
					From:   (id % numAccounts) + 1,
					To:     ((id + 1) % numAccounts) + 1,
					Amount: 10,
				}
				_ = processor.ProcessTransaction(tx)
			}(i)
		}

		wg.Wait()
		elapsed := time.Since(start)

		t.Logf("Processed %d transactions in %v", numTransactions, elapsed)

		totalBalance := 0
		for i := 1; i <= numAccounts; i++ {
			balance, err := processor.GetBalance(i)
			if err != nil {
				t.Fatal(err)
			}
			totalBalance += balance
		}

		expectedTotal := numAccounts * 10000
		if totalBalance != expectedTotal {
			t.Errorf("Total balance mismatch: expected %d, got %d", expectedTotal, totalBalance)
		}
	})
}