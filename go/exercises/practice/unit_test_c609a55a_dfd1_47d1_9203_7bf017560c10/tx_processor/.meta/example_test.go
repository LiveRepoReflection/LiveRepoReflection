package tx_processor_test

import (
	"fmt"
	"tx_processor"
)

func Example() {
	// Initialize with some accounts
	balances := map[string]int64{"A": 100, "B": 50}
	processor := tx_processor.NewTransactionProcessor(balances)

	// Process a valid withdrawal
	err := processor.SubmitTransaction(tx_processor.Transaction{AccountID: "A", Amount: -20, TransactionID: "tx1"})
	if err != nil {
		fmt.Println("Transaction failed:", err)
	}

	// Get and print balance
	balanceA, _ := processor.GetBalance("A")
	fmt.Println("Balance of A:", balanceA)

	// Process a transaction with insufficient funds
	err = processor.SubmitTransaction(tx_processor.Transaction{AccountID: "A", Amount: -100, TransactionID: "tx2"})
	if err != nil {
		fmt.Println("Transaction failed:", err)
	}

	// Balance should be unchanged
	balanceA, _ = processor.GetBalance("A")
	fmt.Println("Balance of A:", balanceA)

	// Process a duplicate transaction ID
	err = processor.SubmitTransaction(tx_processor.Transaction{AccountID: "A", Amount: 10, TransactionID: "tx1"})
	if err != nil {
		fmt.Println("Transaction failed:", err)
	}

	// Output:
	// Balance of A: 80
	// Transaction failed: insufficient funds in account A: 80 < 100
	// Balance of A: 80
	// Transaction failed: duplicate transaction ID: tx1
}