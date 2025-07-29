package txnkvstore

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

// Helper function to create a new coordinator with N nodes, each with M memory capacity
func setupCoordinator(n int, m int) *Coordinator {
	return NewCoordinator(n, m)
}

func TestBasicTransaction(t *testing.T) {
	coordinator := setupCoordinator(3, 1000)

	// Start a transaction
	txn := coordinator.Begin()
	if txn == nil {
		t.Fatal("Failed to start a transaction")
	}

	// Write some values
	err := txn.Write(0, "key1", "value1")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}

	err = txn.Write(1, "key2", "value2")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}

	// Commit the transaction
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	// Start a new transaction to verify writes
	txn = coordinator.Begin()

	// Read the values
	val1, err := txn.Read(0, "key1")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val1 != "value1" {
		t.Fatalf("Expected 'value1', got '%s'", val1)
	}

	val2, err := txn.Read(1, "key2")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val2 != "value2" {
		t.Fatalf("Expected 'value2', got '%s'", val2)
	}

	// Abort this transaction (just for coverage)
	err = txn.Abort()
	if err != nil {
		t.Fatalf("Abort failed: %v", err)
	}
}

func TestTransactionAbort(t *testing.T) {
	coordinator := setupCoordinator(3, 1000)

	// Start a transaction
	txn := coordinator.Begin()
	if txn == nil {
		t.Fatal("Failed to start a transaction")
	}

	// Write some values
	err := txn.Write(0, "key1", "value1")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}

	err = txn.Write(1, "key2", "value2")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}

	// Abort the transaction
	err = txn.Abort()
	if err != nil {
		t.Fatalf("Abort failed: %v", err)
	}

	// Start a new transaction to verify writes didn't take effect
	txn = coordinator.Begin()

	// Read the values
	val1, err := txn.Read(0, "key1")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val1 != "" {
		t.Fatalf("Expected empty string after abort, got '%s'", val1)
	}

	val2, err := txn.Read(1, "key2")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val2 != "" {
		t.Fatalf("Expected empty string after abort, got '%s'", val2)
	}

	// Clean up
	_ = txn.Commit()
}

func TestMemoryConstraints(t *testing.T) {
	// Create a coordinator with small memory capacity
	coordinator := setupCoordinator(1, 20)

	// Start a transaction
	txn := coordinator.Begin()
	if txn == nil {
		t.Fatal("Failed to start a transaction")
	}

	// Write a value that fits in memory
	err := txn.Write(0, "key1", "value1")
	if err != nil {
		t.Fatalf("Write should succeed with small value, but failed: %v", err)
	}

	// Try to write a value that exceeds memory capacity
	err = txn.Write(0, "largeKey", "thisisaverylargeanddramaticallyoversizedvaluethatexceedsmemory")
	if err == nil {
		t.Fatal("Write should fail with large value, but succeeded")
	}

	// Commit should work for first write
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	// Verify first write
	txn = coordinator.Begin()
	val, err := txn.Read(0, "key1")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "value1" {
		t.Fatalf("Expected 'value1', got '%s'", val)
	}
	
	// Verify second write did not succeed
	val, err = txn.Read(0, "largeKey")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "" {
		t.Fatalf("Expected empty string for large key, got '%s'", val)
	}

	// Clean up
	_ = txn.Commit()
}

func TestConcurrentTransactions(t *testing.T) {
	coordinator := setupCoordinator(3, 1000)
	const numTransactions = 10
	var wg sync.WaitGroup

	// Start concurrent transactions
	for i := 0; i < numTransactions; i++ {
		wg.Add(1)
		go func(idx int) {
			defer wg.Done()

			// Start a transaction
			txn := coordinator.Begin()
			if txn == nil {
				t.Errorf("Failed to start transaction %d", idx)
				return
			}

			// Write to multiple nodes
			key := fmt.Sprintf("key%d", idx)
			value := fmt.Sprintf("value%d", idx)

			nodeID := idx % 3 // Distribute across nodes
			err := txn.Write(nodeID, key, value)
			if err != nil {
				t.Errorf("Write failed for txn %d: %v", idx, err)
				return
			}

			// Small delay to increase chance of overlap
			time.Sleep(time.Millisecond * 10)

			// Commit transaction
			err = txn.Commit()
			if err != nil {
				t.Errorf("Commit failed for txn %d: %v", idx, err)
			}
		}(i)
	}

	// Wait for all transactions to complete
	wg.Wait()

	// Verify all writes
	txn := coordinator.Begin()
	for i := 0; i < numTransactions; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		nodeID := i % 3

		val, err := txn.Read(nodeID, key)
		if err != nil {
			t.Errorf("Read failed for key%d: %v", i, err)
			continue
		}
		if val != value {
			t.Errorf("Expected '%s' for key%d, got '%s'", value, i, val)
		}
	}

	// Clean up
	_ = txn.Commit()
}

func TestTransactionReadWrite(t *testing.T) {
	coordinator := setupCoordinator(2, 1000)

	// Transaction 1: Write initial values
	txn1 := coordinator.Begin()
	err := txn1.Write(0, "counter", "10")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	err = txn1.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	// Transaction 2: Read-modify-write
	txn2 := coordinator.Begin()
	val, err := txn2.Read(0, "counter")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "10" {
		t.Fatalf("Expected '10', got '%s'", val)
	}

	// Simulate incrementing the counter
	err = txn2.Write(0, "counter", "11")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}

	// Transaction 3: Should not see uncommitted changes
	txn3 := coordinator.Begin()
	val, err = txn3.Read(0, "counter")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "10" {
		t.Fatalf("Expected '10' (isolation violation), got '%s'", val)
	}
	
	// Clean up transaction 3
	err = txn3.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	// Commit transaction 2
	err = txn2.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	// Transaction 4: Should see committed changes
	txn4 := coordinator.Begin()
	val, err = txn4.Read(0, "counter")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "11" {
		t.Fatalf("Expected '11', got '%s'", val)
	}
	
	// Clean up transaction 4
	err = txn4.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
}

func TestTwoPhaseCommit(t *testing.T) {
	coordinator := setupCoordinator(3, 1000)

	// Start a transaction that will modify multiple nodes
	txn := coordinator.Begin()
	if txn == nil {
		t.Fatal("Failed to start a transaction")
	}

	// Write to multiple nodes
	for i := 0; i < 3; i++ {
		err := txn.Write(i, fmt.Sprintf("key%d", i), fmt.Sprintf("value%d", i))
		if err != nil {
			t.Fatalf("Write failed: %v", err)
		}
	}

	// Commit should apply 2PC
	err := txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	// Verify all writes
	verifyTxn := coordinator.Begin()

	for i := 0; i < 3; i++ {
		val, err := verifyTxn.Read(i, fmt.Sprintf("key%d", i))
		if err != nil {
			t.Fatalf("Read failed: %v", err)
		}
		if val != fmt.Sprintf("value%d", i) {
			t.Fatalf("Expected 'value%d', got '%s'", i, val)
		}
	}

	// Clean up
	_ = verifyTxn.Commit()
}

func TestEdgeCases(t *testing.T) {
	coordinator := setupCoordinator(3, 100)

	// Test case 1: Invalid node ID
	txn := coordinator.Begin()
	err := txn.Write(10, "key", "value") // Node ID 10 doesn't exist
	if err == nil {
		t.Fatal("Expected error for invalid node ID, but got nil")
	}
	
	err = txn.Abort()
	if err != nil {
		t.Fatalf("Abort failed: %v", err)
	}

	// Test case 2: Empty key
	txn = coordinator.Begin()
	err = txn.Write(0, "", "value")
	if err == nil {
		t.Fatal("Expected error for empty key, but got nil")
	}
	
	err = txn.Abort()
	if err != nil {
		t.Fatalf("Abort failed: %v", err)
	}

	// Test case 3: Operations after commit
	txn = coordinator.Begin()
	err = txn.Write(0, "key", "value")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
	
	// Operations after commit should fail
	_, err = txn.Read(0, "key")
	if err == nil {
		t.Fatal("Expected error for read after commit, but got nil")
	}
	
	err = txn.Write(0, "key2", "value2")
	if err == nil {
		t.Fatal("Expected error for write after commit, but got nil")
	}
	
	err = txn.Commit()
	if err == nil {
		t.Fatal("Expected error for double commit, but got nil")
	}
	
	err = txn.Abort()
	if err == nil {
		t.Fatal("Expected error for abort after commit, but got nil")
	}

	// Test case 4: Operations after abort
	txn = coordinator.Begin()
	err = txn.Write(0, "key", "value")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	
	err = txn.Abort()
	if err != nil {
		t.Fatalf("Abort failed: %v", err)
	}
	
	// Operations after abort should fail
	_, err = txn.Read(0, "key")
	if err == nil {
		t.Fatal("Expected error for read after abort, but got nil")
	}
	
	err = txn.Write(0, "key2", "value2")
	if err == nil {
		t.Fatal("Expected error for write after abort, but got nil")
	}
	
	err = txn.Commit()
	if err == nil {
		t.Fatal("Expected error for commit after abort, but got nil")
	}
	
	err = txn.Abort()
	if err == nil {
		t.Fatal("Expected error for double abort, but got nil")
	}
}

func TestLargeNumberOfKeys(t *testing.T) {
	// Create a coordinator with enough memory for many keys
	coordinator := setupCoordinator(1, 10000)
	
	// Write 100 keys in a transaction
	txn := coordinator.Begin()
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		err := txn.Write(0, key, value)
		if err != nil {
			t.Fatalf("Write failed for key %s: %v", key, err)
		}
	}
	
	err := txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
	
	// Read all keys to verify
	txn = coordinator.Begin()
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("key%d", i)
		expectedValue := fmt.Sprintf("value%d", i)
		
		value, err := txn.Read(0, key)
		if err != nil {
			t.Fatalf("Read failed for key %s: %v", key, err)
		}
		
		if value != expectedValue {
			t.Fatalf("Expected %s for key %s, got %s", expectedValue, key, value)
		}
	}
	
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
}

func TestOverwritingValues(t *testing.T) {
	coordinator := setupCoordinator(1, 1000)
	
	// Write initial value
	txn := coordinator.Begin()
	err := txn.Write(0, "key", "value1")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
	
	// Overwrite the value
	txn = coordinator.Begin()
	err = txn.Write(0, "key", "value2")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
	
	// Read the value to verify
	txn = coordinator.Begin()
	value, err := txn.Read(0, "key")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	
	if value != "value2" {
		t.Fatalf("Expected 'value2', got '%s'", value)
	}
	
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
	
	// Test memory reclamation: replace with a larger value, then a smaller one
	txn = coordinator.Begin()
	err = txn.Write(0, "key", "thisislongvalue")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
	
	txn = coordinator.Begin()
	err = txn.Write(0, "key", "short")
	if err != nil {
		t.Fatalf("Write failed: %v", err)
	}
	
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
	
	// Verify the final value
	txn = coordinator.Begin()
	value, err = txn.Read(0, "key")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	
	if value != "short" {
		t.Fatalf("Expected 'short', got '%s'", value)
	}
	
	err = txn.Commit()
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
}

func TestStressTest(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping stress test in short mode")
	}
	
	coordinator := setupCoordinator(5, 10000)
	const numGoroutines = 20
	const operationsPerGoroutine = 50
	
	var wg sync.WaitGroup
	errChan := make(chan error, numGoroutines)
	
	wg.Add(numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		go func(id int) {
			defer wg.Done()
			
			for j := 0; j < operationsPerGoroutine; j++ {
				txn := coordinator.Begin()
				if txn == nil {
					errChan <- fmt.Errorf("goroutine %d: failed to begin transaction", id)
					return
				}
				
				// Read-modify-write cycle
				key := fmt.Sprintf("counter%d", id)
				nodeID := id % 5
				
				value, err := txn.Read(nodeID, key)
				if err != nil {
					errChan <- fmt.Errorf("goroutine %d: read failed: %v", id, err)
					return
				}
				
				var nextValue string
				if value == "" {
					nextValue = "1"
				} else {
					// Simple increment for the test
					var val int
					_, err := fmt.Sscanf(value, "%d", &val)
					if err != nil {
						errChan <- fmt.Errorf("goroutine %d: failed to parse value: %v", id, err)
						return
					}
					nextValue = fmt.Sprintf("%d", val+1)
				}
				
				err = txn.Write(nodeID, key, nextValue)
				if err != nil {
					errChan <- fmt.Errorf("goroutine %d: write failed: %v", id, err)
					return
				}
				
				err = txn.Commit()
				if err != nil {
					errChan <- fmt.Errorf("goroutine %d: commit failed: %v", id, err)
					return
				}
				
				// Small delay to increase contention chances
				time.Sleep(time.Millisecond)
			}
		}(i)
	}
	
	// Wait for all goroutines to finish
	wg.Wait()
	close(errChan)
	
	// Check for errors
	for err := range errChan {
		t.Error(err)
	}
	
	// Verify final state
	txn := coordinator.Begin()
	for i := 0; i < numGoroutines; i++ {
		key := fmt.Sprintf("counter%d", i)
		nodeID := i % 5
		
		value, err := txn.Read(nodeID, key)
		if err != nil {
			t.Fatalf("Final verification read failed for key %s: %v", key, err)
		}
		
		// Check that the final value is operationsPerGoroutine
		var finalVal int
		_, err = fmt.Sscanf(value, "%d", &finalVal)
		if err != nil {
			t.Fatalf("Failed to parse final value for key %s: %v", key, err)
		}
		
		if finalVal != operationsPerGoroutine {
			t.Errorf("Expected final value %d for key %s, got %d",
				operationsPerGoroutine, key, finalVal)
		}
	}
	
	err := txn.Commit()
	if err != nil {
		t.Fatalf("Final verification commit failed: %v", err)
	}
}