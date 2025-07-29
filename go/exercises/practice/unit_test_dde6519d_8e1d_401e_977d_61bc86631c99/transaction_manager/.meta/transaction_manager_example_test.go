package transaction_manager

import (
	"fmt"
)

func ExampleTransactionManager() {
	// Create a new transaction manager
	tm := NewTransactionManager()

	// Begin a new transaction
	err := tm.Begin(123)
	if err != nil {
		fmt.Println("Error beginning transaction:", err)
		return
	}

	// Add participating service nodes
	err = tm.Participate(123, 1)
	if err != nil {
		fmt.Println("Error adding participant 1:", err)
		return
	}

	err = tm.Participate(123, 2)
	if err != nil {
		fmt.Println("Error adding participant 2:", err)
		return
	}

	// Simulate the PrepareVote function for service nodes
	serviceNodeVotes := map[int]bool{
		1: true,
		2: true,
	}
	tm.PrepareVoteFunc = func(transactionID, serviceNode int) bool {
		return serviceNodeVotes[serviceNode]
	}

	// Prepare the transaction
	err = tm.Prepare(123)
	if err != nil {
		fmt.Println("Error preparing transaction:", err)
		return
	}

	// Commit the transaction
	err = tm.Commit(123)
	if err != nil {
		fmt.Println("Error committing transaction:", err)
		return
	}

	// Get the final state of the transaction
	state := tm.GetTransactionState(123)
	fmt.Println("Transaction state:", state)
}

func ExampleTransactionManager_abort() {
	// Create a new transaction manager
	tm := NewTransactionManager()

	// Begin a new transaction
	err := tm.Begin(456)
	if err != nil {
		fmt.Println("Error beginning transaction:", err)
		return
	}

	// Add participating service nodes
	err = tm.Participate(456, 3)
	if err != nil {
		fmt.Println("Error adding participant 3:", err)
		return
	}

	err = tm.Participate(456, 4)
	if err != nil {
		fmt.Println("Error adding participant 4:", err)
		return
	}

	// Simulate one service node voting to abort
	serviceNodeVotes := map[int]bool{
		3: true,
		4: false,
	}
	tm.PrepareVoteFunc = func(transactionID, serviceNode int) bool {
		return serviceNodeVotes[serviceNode]
	}

	// Prepare the transaction (should automatically abort)
	err = tm.Prepare(456)
	if err != nil {
		fmt.Println("Transaction preparation failed (expected):", err)
	}

	// Get the final state of the transaction
	state := tm.GetTransactionState(456)
	fmt.Println("Transaction state:", state)

	// Trying to commit should fail
	err = tm.Commit(456)
	if err != nil {
		fmt.Println("Cannot commit aborted transaction (expected):", err)
	}
}