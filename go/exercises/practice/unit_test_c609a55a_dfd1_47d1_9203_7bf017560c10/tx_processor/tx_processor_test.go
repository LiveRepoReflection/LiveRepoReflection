package tx_processor

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestNewTransactionProcessor(t *testing.T) {
	balances := map[string]int64{
		"A": 100,
		"B": 200,
	}

	processor := NewTransactionProcessor(balances)
	if processor == nil {
		t.Fatal("Expected processor to be non-nil")
	}

	// Check initial balances
	balance, err := processor.GetBalance("A")
	if err != nil {
		t.Errorf("Error getting balance for account A: %v", err)
	}
	if balance != 100 {
		t.Errorf("Expected balance for account A to be 100, got %d", balance)
	}

	balance, err = processor.GetBalance("B")
	if err != nil {
		t.Errorf("Error getting balance for account B: %v", err)
	}
	if balance != 200 {
		t.Errorf("Expected balance for account B to be 200, got %d", balance)
	}

	// Check non-existent account
	_, err = processor.GetBalance("C")
	if err == nil {
		t.Error("Expected error when getting balance for non-existent account")
	}
}

func TestBasicTransactionProcessing(t *testing.T) {
	balances := map[string]int64{
		"A": 100,
		"B": 50,
	}

	processor := NewTransactionProcessor(balances)

	// Valid withdrawal
	err := processor.SubmitTransaction(Transaction{AccountID: "A", Amount: -20, TransactionID: "tx1"})
	if err != nil {
		t.Errorf("Error processing valid transaction: %v", err)
	}

	balanceA, _ := processor.GetBalance("A")
	if balanceA != 80 {
		t.Errorf("Expected balance of A to be 80, got %d", balanceA)
	}

	// Insufficient balance
	err = processor.SubmitTransaction(Transaction{AccountID: "A", Amount: -100, TransactionID: "tx2"})
	if err == nil {
		t.Error("Expected error for transaction with insufficient balance")
	}

	balanceA, _ = processor.GetBalance("A")
	if balanceA != 80 {
		t.Errorf("Expected balance of A to still be 80, got %d", balanceA)
	}

	// Duplicate transaction ID
	err = processor.SubmitTransaction(Transaction{AccountID: "A", Amount: 10, TransactionID: "tx1"})
	if err == nil {
		t.Error("Expected error for transaction with duplicate ID")
	}

	// Valid deposit
	err = processor.SubmitTransaction(Transaction{AccountID: "B", Amount: 30, TransactionID: "tx3"})
	if err != nil {
		t.Errorf("Error processing valid deposit: %v", err)
	}

	balanceB, _ := processor.GetBalance("B")
	if balanceB != 80 {
		t.Errorf("Expected balance of B to be 80, got %d", balanceB)
	}

	// Non-existent account
	err = processor.SubmitTransaction(Transaction{AccountID: "C", Amount: 10, TransactionID: "tx4"})
	if err == nil {
		t.Error("Expected error for transaction with non-existent account")
	}

	// Check error count
	errorCount := processor.GetErrorCount()
	if errorCount != 3 {
		t.Errorf("Expected error count to be 3, got %d", errorCount)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	// Initialize with some accounts
	balances := map[string]int64{
		"A": 1000,
		"B": 1000,
		"C": 1000,
	}

	processor := NewTransactionProcessor(balances)

	// Number of concurrent transactions per account
	const numTxPerAccount = 100

	var wg sync.WaitGroup
	// Process transactions concurrently for each account
	for i := 0; i < numTxPerAccount; i++ {
		wg.Add(3) // 3 accounts

		// Process transactions for account A
		go func(i int) {
			defer wg.Done()
			txID := fmt.Sprintf("A-tx-%d", i)
			// Withdraw 1 each time
			err := processor.SubmitTransaction(Transaction{
				AccountID:    "A",
				Amount:       -1,
				TransactionID: txID,
			})
			if err != nil {
				t.Errorf("Error processing transaction for account A: %v", err)
			}
		}(i)

		// Process transactions for account B
		go func(i int) {
			defer wg.Done()
			txID := fmt.Sprintf("B-tx-%d", i)
			// Deposit 2 each time
			err := processor.SubmitTransaction(Transaction{
				AccountID:    "B",
				Amount:       2,
				TransactionID: txID,
			})
			if err != nil {
				t.Errorf("Error processing transaction for account B: %v", err)
			}
		}(i)

		// Process alternating transactions for account C
		go func(i int) {
			defer wg.Done()
			txID := fmt.Sprintf("C-tx-%d", i)
			// Alternate between deposit and withdrawal
			amount := int64(1)
			if i%2 == 0 {
				amount = -1
			}
			err := processor.SubmitTransaction(Transaction{
				AccountID:    "C",
				Amount:       amount,
				TransactionID: txID,
			})
			if err != nil {
				t.Errorf("Error processing transaction for account C: %v", err)
			}
		}(i)
	}

	wg.Wait()

	// Verify final balances
	balanceA, _ := processor.GetBalance("A")
	if balanceA != 1000-numTxPerAccount {
		t.Errorf("Expected balance of A to be %d, got %d", 1000-numTxPerAccount, balanceA)
	}

	balanceB, _ := processor.GetBalance("B")
	if balanceB != 1000+(2*numTxPerAccount) {
		t.Errorf("Expected balance of B to be %d, got %d", 1000+(2*numTxPerAccount), balanceB)
	}

	balanceC, _ := processor.GetBalance("C")
	expectedC := 1000
	if numTxPerAccount%2 == 1 {
		// If odd number of transactions, there's one more deposit than withdrawal
		expectedC += numTxPerAccount / 2 + 1 - numTxPerAccount/2
	}
	if balanceC != int64(expectedC) {
		t.Errorf("Expected balance of C to be %d, got %d", expectedC, balanceC)
	}
}

func TestTransactionOrdering(t *testing.T) {
	balances := map[string]int64{
		"A": 100,
	}

	processor := NewTransactionProcessor(balances)

	// Create a channel to control when transactions complete
	doneCh := make(chan struct{})
	errorCh := make(chan error, 2)

	// Submit a transaction that will block
	go func() {
		// This transaction should complete first
		err := processor.SubmitTransaction(Transaction{
			AccountID:    "A",
			Amount:       -50,
			TransactionID: "tx1",
		})
		if err != nil {
			errorCh <- fmt.Errorf("tx1 error: %v", err)
		}
		// Signal that tx1 is complete
		close(doneCh)
	}()

	// Give the first transaction time to start processing
	time.Sleep(100 * time.Millisecond)

	// Submit a second transaction for the same account
	go func() {
		// This should wait until tx1 completes
		err := processor.SubmitTransaction(Transaction{
			AccountID:    "A",
			Amount:       -50,
			TransactionID: "tx2",
		})
		if err != nil {
			errorCh <- fmt.Errorf("tx2 error: %v", err)
		}
	}()

	// Wait for tx1 to complete
	<-doneCh

	// Give tx2 time to process
	time.Sleep(100 * time.Millisecond)

	// Check for any errors
	select {
	case err := <-errorCh:
		t.Fatalf("Unexpected error: %v", err)
	default:
		// No errors, continue
	}

	// Verify final balance
	balance, _ := processor.GetBalance("A")
	if balance != 0 {
		t.Errorf("Expected balance to be 0, got %d", balance)
	}
}

func TestLargeNumberOfTransactions(t *testing.T) {
	// Skip this test in short mode
	if testing.Short() {
		t.Skip("Skipping large transaction test in short mode")
	}

	// Create 1000 accounts
	balances := make(map[string]int64)
	for i := 0; i < 1000; i++ {
		accountID := fmt.Sprintf("account-%d", i)
		balances[accountID] = 1000
	}

	processor := NewTransactionProcessor(balances)

	// Process 100,000 transactions concurrently
	var wg sync.WaitGroup
	for i := 0; i < 100000; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			accountID := fmt.Sprintf("account-%d", i%1000)
			txID := fmt.Sprintf("tx-%d", i)
			amount := int64(i%5 + 1) // 1 to 5
			if i%2 == 0 {
				amount = -amount // Make half of transactions withdrawals
			}
			err := processor.SubmitTransaction(Transaction{
				AccountID:    accountID,
				Amount:       amount,
				TransactionID: txID,
			})
			if err != nil {
				// Ignore errors in this test - we're just testing volume
			}
		}(i)
	}

	wg.Wait()

	// We don't verify specific balances here, just ensure the system doesn't crash
	// under load and that we can still get balances afterward
	for i := 0; i < 10; i++ { // Check a few random accounts
		accountID := fmt.Sprintf("account-%d", i*100)
		_, err := processor.GetBalance(accountID)
		if err != nil {
			t.Errorf("Error getting balance for account %s: %v", accountID, err)
		}
	}
}

func TestEdgeCases(t *testing.T) {
	balances := map[string]int64{
		"A": 100,
		"B": 0,
		"C": 9223372036854775807, // max int64
	}

	processor := NewTransactionProcessor(balances)

	// Test zero amount transaction
	err := processor.SubmitTransaction(Transaction{
		AccountID:    "A",
		Amount:       0,
		TransactionID: "zero-tx",
	})
	if err != nil {
		t.Errorf("Error processing zero amount transaction: %v", err)
	}

	// Test withdrawal from zero balance
	err = processor.SubmitTransaction(Transaction{
		AccountID:    "B",
		Amount:       -1,
		TransactionID: "zero-balance-withdrawal",
	})
	if err == nil {
		t.Error("Expected error when withdrawing from zero balance")
	}

	// Test deposit to max int64 balance
	err = processor.SubmitTransaction(Transaction{
		AccountID:    "C",
		Amount:       1,
		TransactionID: "overflow-deposit",
	})
	if err == nil {
		t.Error("Expected error when depositing to max int64 balance")
	}

	// Test empty transaction ID
	err = processor.SubmitTransaction(Transaction{
		AccountID:    "A",
		Amount:       10,
		TransactionID: "",
	})
	if err == nil {
		t.Error("Expected error with empty transaction ID")
	}

	// Test empty account ID
	err = processor.SubmitTransaction(Transaction{
		AccountID:    "",
		Amount:       10,
		TransactionID: "empty-account",
	})
	if err == nil {
		t.Error("Expected error with empty account ID")
	}
}

func BenchmarkTransactionProcessing(b *testing.B) {
	// Create 1000 accounts
	balances := make(map[string]int64)
	for i := 0; i < 1000; i++ {
		accountID := fmt.Sprintf("account-%d", i)
		balances[accountID] = 1000
	}

	processor := NewTransactionProcessor(balances)

	// Reset the timer to exclude setup time
	b.ResetTimer()

	// Run b.N transactions
	for i := 0; i < b.N; i++ {
		accountID := fmt.Sprintf("account-%d", i%1000)
		txID := fmt.Sprintf("tx-%d", i)
		amount := int64(i%5 + 1) // 1 to 5
		if i%2 == 0 {
			amount = -amount // Make half of transactions withdrawals
		}
		err := processor.SubmitTransaction(Transaction{
			AccountID:    accountID,
			Amount:       amount,
			TransactionID: txID,
		})
		if err != nil {
			b.Fatalf("Error processing transaction: %v", err)
		}
	}
}

func BenchmarkConcurrentTransactionProcessing(b *testing.B) {
	// Create 1000 accounts
	balances := make(map[string]int64)
	for i := 0; i < 1000; i++ {
		accountID := fmt.Sprintf("account-%d", i)
		balances[accountID] = 1000
	}

	processor := NewTransactionProcessor(balances)

	// Reset the timer to exclude setup time
	b.ResetTimer()

	b.RunParallel(func(pb *testing.PB) {
		i := 0
		for pb.Next() {
			accountID := fmt.Sprintf("account-%d", i%1000)
			txID := fmt.Sprintf("tx-%d-%d", i, time.Now().UnixNano()) // Ensure unique tx ID
			amount := int64(i%5 + 1)                                   // 1 to 5
			if i%2 == 0 {
				amount = -amount // Make half of transactions withdrawals
			}
			processor.SubmitTransaction(Transaction{
				AccountID:    accountID,
				Amount:       amount,
				TransactionID: txID,
			})
			i++
		}
	})
}