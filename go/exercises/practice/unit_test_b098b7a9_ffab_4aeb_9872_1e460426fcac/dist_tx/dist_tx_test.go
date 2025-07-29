package dist_tx

import (
	"errors"
	"testing"
)

func TestTransactionLifecycle(t *testing.T) {
	dtm := NewDTM()

	// Test successful transaction
	txID := "tx1"
	serviceIDs := []string{"svc1", "svc2"}
	err := dtm.RegisterTransaction(txID, serviceIDs)
	if err != nil {
		t.Fatalf("Failed to register transaction: %v", err)
	}

	// Submit operations
	err = dtm.SubmitOperation(txID, "svc1", func(state map[string]interface{}) (map[string]interface{}, error) {
		newState := make(map[string]interface{})
		for k, v := range state {
			newState[k] = v
		}
		newState["key1"] = "value1"
		return newState, nil
	})
	if err != nil {
		t.Fatalf("Failed to submit operation: %v", err)
	}

	err = dtm.SubmitOperation(txID, "svc2", func(state map[string]interface{}) (map[string]interface{}, error) {
		newState := make(map[string]interface{})
		for k, v := range state {
			newState[k] = v
		}
		newState["key2"] = "value2"
		return newState, nil
	})
	if err != nil {
		t.Fatalf("Failed to submit operation: %v", err)
	}

	// Commit transaction
	err = dtm.CommitTransaction(txID)
	if err != nil {
		t.Fatalf("Failed to commit transaction: %v", err)
	}

	// Verify state
	if dtm.state["key1"] != "value1" || dtm.state["key2"] != "value2" {
		t.Errorf("State not updated correctly")
	}
}

func TestServiceConflict(t *testing.T) {
	dtm := NewDTM()

	// First transaction
	tx1 := "tx1"
	err := dtm.RegisterTransaction(tx1, []string{"svc1"})
	if err != nil {
		t.Fatalf("Failed to register first transaction: %v", err)
	}

	// Second transaction trying to use same service
	tx2 := "tx2"
	err = dtm.RegisterTransaction(tx2, []string{"svc1"})
	if err == nil {
		t.Error("Expected error when registering service in multiple transactions")
	}
}

func TestOperationFailure(t *testing.T) {
	dtm := NewDTM()

	txID := "tx1"
	err := dtm.RegisterTransaction(txID, []string{"svc1"})
	if err != nil {
		t.Fatalf("Failed to register transaction: %v", err)
	}

	// Submit failing operation
	err = dtm.SubmitOperation(txID, "svc1", func(state map[string]interface{}) (map[string]interface{}, error) {
		return nil, errors.New("operation failed")
	})
	if err != nil {
		t.Fatalf("Failed to submit operation: %v", err)
	}

	// Attempt to commit
	err = dtm.CommitTransaction(txID)
	if err == nil {
		t.Error("Expected error when committing transaction with failed operation")
	}
}

func TestConcurrentTransactions(t *testing.T) {
	dtm := NewDTM()

	// Channel to collect results
	results := make(chan error, 2)

	// First transaction
	go func() {
		txID := "tx1"
		err := dtm.RegisterTransaction(txID, []string{"svc1"})
		if err != nil {
			results <- err
			return
		}

		err = dtm.SubmitOperation(txID, "svc1", func(state map[string]interface{}) (map[string]interface{}, error) {
			newState := make(map[string]interface{})
			for k, v := range state {
				newState[k] = v
			}
			newState["tx1"] = "success"
			return newState, nil
		})
		if err != nil {
			results <- err
			return
		}

		results <- dtm.CommitTransaction(txID)
	}()

	// Second transaction (different service)
	go func() {
		txID := "tx2"
		err := dtm.RegisterTransaction(txID, []string{"svc2"})
		if err != nil {
			results <- err
			return
		}

		err = dtm.SubmitOperation(txID, "svc2", func(state map[string]interface{}) (map[string]interface{}, error) {
			newState := make(map[string]interface{})
			for k, v := range state {
				newState[k] = v
			}
			newState["tx2"] = "success"
			return newState, nil
		})
		if err != nil {
			results <- err
			return
		}

		results <- dtm.CommitTransaction(txID)
	}()

	// Wait for both transactions to complete
	err1 := <-results
	err2 := <-results

	if err1 != nil || err2 != nil {
		t.Errorf("Concurrent transactions failed: %v, %v", err1, err2)
	}

	// Verify both transactions committed
	if dtm.state["tx1"] != "success" || dtm.state["tx2"] != "success" {
		t.Error("Concurrent transactions did not update state correctly")
	}
}

func TestRollback(t *testing.T) {
	dtm := NewDTM()

	// Set initial state
	dtm.state["initial"] = "value"

	txID := "tx1"
	err := dtm.RegisterTransaction(txID, []string{"svc1", "svc2"})
	if err != nil {
		t.Fatalf("Failed to register transaction: %v", err)
	}

	// First operation succeeds
	err = dtm.SubmitOperation(txID, "svc1", func(state map[string]interface{}) (map[string]interface{}, error) {
		newState := make(map[string]interface{})
		for k, v := range state {
			newState[k] = v
		}
		newState["op1"] = "success"
		return newState, nil
	})
	if err != nil {
		t.Fatalf("Failed to submit operation: %v", err)
	}

	// Second operation fails
	err = dtm.SubmitOperation(txID, "svc2", func(state map[string]interface{}) (map[string]interface{}, error) {
		return nil, errors.New("operation failed")
	})
	if err != nil {
		t.Fatalf("Failed to submit operation: %v", err)
	}

	// Attempt to commit
	err = dtm.CommitTransaction(txID)
	if err == nil {
		t.Error("Expected error when committing transaction with failed operation")
	}

	// Verify state was rolled back
	if _, exists := dtm.state["op1"]; exists {
		t.Error("State was not rolled back after failed operation")
	}
	if dtm.state["initial"] != "value" {
		t.Error("Initial state was corrupted")
	}
}