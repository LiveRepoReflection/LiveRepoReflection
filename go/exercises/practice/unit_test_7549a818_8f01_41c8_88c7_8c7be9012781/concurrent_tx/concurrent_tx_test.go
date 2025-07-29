package concurrent_tx

import (
	"fmt"
	"math/rand"
	"sync"
	"testing"
	"time"
)

func TestAccountCreationAndBalance(t *testing.T) {
	db := NewDatabase()
	
	err := db.CreateAccount("user1", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	// Check if account exists
	balance, err := db.GetBalance("user1")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	
	if balance != 1000 {
		t.Fatalf("Expected balance 1000, got %d", balance)
	}
	
	// Attempt to create duplicate account
	err = db.CreateAccount("user1", 500)
	if err == nil {
		t.Fatal("Expected error when creating duplicate account, but got nil")
	}
	
	// Non-existent account
	_, err = db.GetBalance("nonexistent")
	if err == nil {
		t.Fatal("Expected error when getting balance of non-existent account, but got nil")
	}
}

func TestSingleTransaction(t *testing.T) {
	db := NewDatabase()
	
	err := db.CreateAccount("user1", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	tx := db.BeginTransaction()
	
	err = tx.Deposit("user1", 500)
	if err != nil {
		t.Fatalf("Failed to deposit: %v", err)
	}
	
	// Balance should not change until commit
	balance, err := db.GetBalance("user1")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	if balance != 1000 {
		t.Fatalf("Expected balance to remain 1000 before commit, got %d", balance)
	}
	
	err = tx.Commit()
	if err != nil {
		t.Fatalf("Failed to commit transaction: %v", err)
	}
	
	// Balance should update after commit
	balance, err = db.GetBalance("user1")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	if balance != 1500 {
		t.Fatalf("Expected balance 1500 after deposit, got %d", balance)
	}
}

func TestTransactionRollback(t *testing.T) {
	db := NewDatabase()
	
	err := db.CreateAccount("user1", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	tx := db.BeginTransaction()
	
	err = tx.Deposit("user1", 500)
	if err != nil {
		t.Fatalf("Failed to deposit: %v", err)
	}
	
	err = tx.Rollback()
	if err != nil {
		t.Fatalf("Failed to rollback: %v", err)
	}
	
	// Balance should not change after rollback
	balance, err := db.GetBalance("user1")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	if balance != 1000 {
		t.Fatalf("Expected balance to remain 1000 after rollback, got %d", balance)
	}
}

func TestInsufficientFunds(t *testing.T) {
	db := NewDatabase()
	
	err := db.CreateAccount("user1", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	tx := db.BeginTransaction()
	
	// Try to withdraw more than available
	err = tx.Withdraw("user1", 1500)
	if err == nil {
		t.Fatal("Expected error when withdrawing more than available, but got nil")
	}
	
	// Balance should remain unchanged
	balance, err := db.GetBalance("user1")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	if balance != 1000 {
		t.Fatalf("Expected balance to remain 1000, got %d", balance)
	}
}

func TestNegativeDeposit(t *testing.T) {
	db := NewDatabase()
	
	err := db.CreateAccount("user1", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	tx := db.BeginTransaction()
	
	// Try negative deposit (effectively a withdraw)
	err = tx.Deposit("user1", -500)
	if err != nil {
		t.Fatalf("Failed to make negative deposit: %v", err)
	}
	
	err = tx.Commit()
	if err != nil {
		t.Fatalf("Failed to commit transaction: %v", err)
	}
	
	// Balance should be updated
	balance, err := db.GetBalance("user1")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	if balance != 500 {
		t.Fatalf("Expected balance 500 after negative deposit, got %d", balance)
	}
}

func TestNegativeWithdraw(t *testing.T) {
	db := NewDatabase()
	
	err := db.CreateAccount("user1", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	tx := db.BeginTransaction()
	
	// Try negative withdraw (effectively a deposit)
	err = tx.Withdraw("user1", -500)
	if err != nil {
		t.Fatalf("Failed to make negative withdraw: %v", err)
	}
	
	err = tx.Commit()
	if err != nil {
		t.Fatalf("Failed to commit transaction: %v", err)
	}
	
	// Balance should be updated
	balance, err := db.GetBalance("user1")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	if balance != 1500 {
		t.Fatalf("Expected balance 1500 after negative withdraw, got %d", balance)
	}
}

func TestTransactionIsolation(t *testing.T) {
	db := NewDatabase()
	
	err := db.CreateAccount("user1", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	tx1 := db.BeginTransaction()
	tx2 := db.BeginTransaction()
	
	// First transaction deposits 500
	err = tx1.Deposit("user1", 500)
	if err != nil {
		t.Fatalf("Failed to deposit in tx1: %v", err)
	}
	
	// Second transaction should still see original balance
	err = tx2.Withdraw("user1", 800)
	if err != nil {
		t.Fatalf("Failed to withdraw in tx2: %v", err)
	}
	
	// Commit first transaction
	err = tx1.Commit()
	if err != nil {
		t.Fatalf("Failed to commit tx1: %v", err)
	}
	
	// Commit second transaction (should handle conflicts if any)
	err = tx2.Commit()
	if err != nil {
		t.Fatalf("Failed to commit tx2: %v", err)
	}
	
	// Check final balance (should reflect both transactions)
	balance, err := db.GetBalance("user1")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	if balance != 700 {
		t.Fatalf("Expected final balance 700, got %d", balance)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	db := NewDatabase()
	
	// Create 10 accounts
	for i := 1; i <= 10; i++ {
		err := db.CreateAccount(fmt.Sprintf("user%d", i), 1000)
		if err != nil {
			t.Fatalf("Failed to create account: %v", err)
		}
	}
	
	var wg sync.WaitGroup
	// Run 100 concurrent transactions
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(txNum int) {
			defer wg.Done()
			
			// Random source account
			srcAcct := fmt.Sprintf("user%d", rand.Intn(10)+1)
			// Random destination account (different from source)
			var destAcct string
			for {
				destAcct = fmt.Sprintf("user%d", rand.Intn(10)+1)
				if destAcct != srcAcct {
					break
				}
			}
			
			tx := db.BeginTransaction()
			
			// Random amount between 1-100
			amount := rand.Intn(100) + 1
			
			// Transfer funds
			err := tx.Withdraw(srcAcct, amount)
			if err != nil {
				return // Just ignore if insufficient funds
			}
			
			err = tx.Deposit(destAcct, amount)
			if err != nil {
				t.Errorf("Transaction %d: Failed to deposit to %s: %v", txNum, destAcct, err)
				tx.Rollback()
				return
			}
			
			err = tx.Commit()
			if err != nil {
				// Expected conflict in some cases, just roll back
				tx.Rollback()
			}
		}(i)
	}
	
	wg.Wait()
	
	// Total balance across all accounts should still be 10,000
	var totalBalance int
	for i := 1; i <= 10; i++ {
		acct := fmt.Sprintf("user%d", i)
		balance, err := db.GetBalance(acct)
		if err != nil {
			t.Fatalf("Failed to get balance for %s: %v", acct, err)
		}
		totalBalance += balance
	}
	
	if totalBalance != 10000 {
		t.Fatalf("Expected total balance 10000, got %d", totalBalance)
	}
}

func TestDeadlockPrevention(t *testing.T) {
	db := NewDatabase()
	
	err := db.CreateAccount("user1", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	err = db.CreateAccount("user2", 1000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	// Create a potential deadlock situation
	var wg sync.WaitGroup
	wg.Add(2)
	
	// Set a timeout for deadlock detection
	done := make(chan bool)
	go func() {
		wg.Wait()
		done <- true
	}()
	
	go func() {
		defer wg.Done()
		tx := db.BeginTransaction()
		
		err := tx.Withdraw("user1", 100)
		if err != nil {
			t.Logf("TX1: Error withdrawing: %v", err)
			return
		}
		
		// Introduce some delay to increase chance of deadlock
		time.Sleep(10 * time.Millisecond)
		
		err = tx.Deposit("user2", 100)
		if err != nil {
			t.Logf("TX1: Error depositing: %v", err)
			return
		}
		
		err = tx.Commit()
		if err != nil {
			tx.Rollback()
		}
	}()
	
	go func() {
		defer wg.Done()
		tx := db.BeginTransaction()
		
		err := tx.Withdraw("user2", 50)
		if err != nil {
			t.Logf("TX2: Error withdrawing: %v", err)
			return
		}
		
		// Introduce some delay to increase chance of deadlock
		time.Sleep(10 * time.Millisecond)
		
		err = tx.Deposit("user1", 50)
		if err != nil {
			t.Logf("TX2: Error depositing: %v", err)
			return
		}
		
		err = tx.Commit()
		if err != nil {
			tx.Rollback()
		}
	}()
	
	// Set a timeout to detect potential deadlock
	select {
	case <-done:
		// Test passed - no deadlock
	case <-time.After(5 * time.Second):
		t.Fatal("Potential deadlock detected - test timed out")
	}
	
	// Check that total balance is preserved
	balance1, _ := db.GetBalance("user1")
	balance2, _ := db.GetBalance("user2")
	if balance1+balance2 != 2000 {
		t.Fatalf("Expected total balance to be 2000, got %d", balance1+balance2)
	}
}

func TestLargeTransactions(t *testing.T) {
	db := NewDatabase()
	
	// Create one account
	err := db.CreateAccount("user", 10000)
	if err != nil {
		t.Fatalf("Failed to create account: %v", err)
	}
	
	tx := db.BeginTransaction()
	
	// Perform 1000 operations in a single transaction
	for i := 0; i < 500; i++ {
		err = tx.Withdraw("user", 1)
		if err != nil {
			t.Fatalf("Failed to withdraw on operation %d: %v", i, err)
		}
		
		err = tx.Deposit("user", 1)
		if err != nil {
			t.Fatalf("Failed to deposit on operation %d: %v", i, err)
		}
	}
	
	err = tx.Commit()
	if err != nil {
		t.Fatalf("Failed to commit large transaction: %v", err)
	}
	
	// Balance should be unchanged
	balance, err := db.GetBalance("user")
	if err != nil {
		t.Fatalf("Failed to get balance: %v", err)
	}
	
	if balance != 10000 {
		t.Fatalf("Expected balance to remain 10000, got %d", balance)
	}
}

func TestStressTest(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping stress test in short mode")
	}
	
	db := NewDatabase()
	
	// Create 100 accounts with 1000 balance each
	for i := 0; i < 100; i++ {
		err := db.CreateAccount(fmt.Sprintf("user%d", i), 1000)
		if err != nil {
			t.Fatalf("Failed to create account: %v", err)
		}
	}
	
	// Concurrent workers
	numWorkers := 10
	txPerWorker := 100
	
	var wg sync.WaitGroup
	wg.Add(numWorkers)
	
	for w := 0; w < numWorkers; w++ {
		go func(workerID int) {
			defer wg.Done()
			
			for i := 0; i < txPerWorker; i++ {
				// Random sender
				sender := fmt.Sprintf("user%d", rand.Intn(100))
				// Random receiver (different from sender)
				var receiver string
				for {
					receiver = fmt.Sprintf("user%d", rand.Intn(100))
					if receiver != sender {
						break
					}
				}
				
				// Random amount between 1-10
				amount := rand.Intn(10) + 1
				
				tx := db.BeginTransaction()
				
				err := tx.Withdraw(sender, amount)
				if err != nil {
					tx.Rollback()
					continue
				}
				
				err = tx.Deposit(receiver, amount)
				if err != nil {
					tx.Rollback()
					continue
				}
				
				err = tx.Commit()
				if err != nil {
					tx.Rollback()
				}
			}
		}(w)
	}
	
	// Wait for all workers to complete
	wg.Wait()
	
	// Verify total balance across all accounts
	var totalBalance int
	for i := 0; i < 100; i++ {
		balance, err := db.GetBalance(fmt.Sprintf("user%d", i))
		if err != nil {
			t.Fatalf("Failed to get balance: %v", err)
		}
		totalBalance += balance
	}
	
	if totalBalance != 100*1000 {
		t.Fatalf("Expected total balance to be 100,000, got %d", totalBalance)
	}
}

func BenchmarkConcurrentTransactions(b *testing.B) {
	db := NewDatabase()
	
	// Create 100 accounts
	for i := 0; i < 100; i++ {
		err := db.CreateAccount(fmt.Sprintf("user%d", i), 1000)
		if err != nil {
			b.Fatalf("Failed to create account: %v", err)
		}
	}
	
	b.ResetTimer()
	
	// Run b.N transactions
	b.RunParallel(func(pb *testing.PB) {
		r := rand.New(rand.NewSource(time.Now().UnixNano()))
		for pb.Next() {
			// Random sender and receiver
			sender := fmt.Sprintf("user%d", r.Intn(100))
			var receiver string
			for {
				receiver = fmt.Sprintf("user%d", r.Intn(100))
				if receiver != sender {
					break
				}
			}
			
			tx := db.BeginTransaction()
			
			// Transfer random amount
			amount := r.Intn(10) + 1
			err := tx.Withdraw(sender, amount)
			if err != nil {
				tx.Rollback()
				continue
			}
			
			err = tx.Deposit(receiver, amount)
			if err != nil {
				tx.Rollback()
				continue
			}
			
			tx.Commit()
		}
	})
}