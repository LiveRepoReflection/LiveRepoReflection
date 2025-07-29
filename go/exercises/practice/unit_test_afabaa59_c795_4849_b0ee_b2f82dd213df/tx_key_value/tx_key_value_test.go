package tx_key_value

import (
	"sync"
	"testing"
	"time"
)

func TestTransactionCommit(t *testing.T) {
	nodeAddresses := []string{"node1", "node2", "node3"}
	store, err := NewDistributedKVStore(nodeAddresses)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	txID, err := store.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	err = store.Write(txID, "key1", "value1")
	if err != nil {
		t.Fatalf("Write failed in transaction: %v", err)
	}

	err = store.Commit(txID)
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}

	txID2, err := store.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}

	val, err := store.Read(txID2, "key1")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "value1" {
		t.Errorf("Expected \"value1\", got \"%v\"", val)
	}
	err = store.Commit(txID2)
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
}

func TestConflictResolution(t *testing.T) {
	nodeAddresses := []string{"node1", "node2", "node3"}
	store, err := NewDistributedKVStore(nodeAddresses)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	txID1, err := store.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}
	err = store.Write(txID1, "key_conflict", "A")
	if err != nil {
		t.Fatalf("Write in txID1 failed: %v", err)
	}
	// Delay to simulate a lower timestamp for txID1
	time.Sleep(10 * time.Millisecond)
	err = store.Commit(txID1)
	if err != nil {
		t.Fatalf("Commit txID1 failed: %v", err)
	}

	txID2, err := store.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}
	err = store.Write(txID2, "key_conflict", "B")
	if err != nil {
		t.Fatalf("Write in txID2 failed: %v", err)
	}
	err = store.Commit(txID2)
	if err != nil {
		t.Fatalf("Commit txID2 failed: %v", err)
	}

	txID3, err := store.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}
	val, err := store.Read(txID3, "key_conflict")
	if err != nil {
		t.Fatalf("Read failed: %v", err)
	}
	if val != "B" {
		t.Errorf("Conflict resolution failed: expected \"B\", got \"%v\"", val)
	}
	err = store.Commit(txID3)
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
}

func TestConcurrentTransactions(t *testing.T) {
	nodeAddresses := []string{"node1", "node2", "node3"}
	store, err := NewDistributedKVStore(nodeAddresses)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	keys := []string{"k1", "k2", "k3", "k4", "k5"}
	var wg sync.WaitGroup
	for i := 0; i < len(keys); i++ {
		wg.Add(1)
		go func(key string) {
			defer wg.Done()
			txID, err := store.BeginTransaction()
			if err != nil {
				t.Errorf("BeginTransaction failed: %v", err)
				return
			}
			err = store.Write(txID, key, "val_"+key)
			if err != nil {
				t.Errorf("Write failed for key %v: %v", key, err)
				return
			}
			err = store.Commit(txID)
			if err != nil {
				t.Errorf("Commit failed for key %v: %v", key, err)
				return
			}
		}(keys[i])
	}
	wg.Wait()

	txID, err := store.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}
	for _, key := range keys {
		val, err := store.Read(txID, key)
		if err != nil {
			t.Errorf("Read failed for key %v: %v", key, err)
			continue
		}
		expected := "val_" + key
		if val != expected {
			t.Errorf("For key %v, expected \"%v\" but got \"%v\"", key, expected, val)
		}
	}
	err = store.Commit(txID)
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
}

func TestTransactionErrorHandling(t *testing.T) {
	nodeAddresses := []string{"node1", "node2", "node3"}
	store, err := NewDistributedKVStore(nodeAddresses)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	_, err = store.Read("invalid_tx", "nonexistent")
	if err == nil {
		t.Errorf("Expected error when reading with invalid transaction id")
	}

	err = store.Write("invalid_tx", "key", "value")
	if err == nil {
		t.Errorf("Expected error when writing with invalid transaction id")
	}

	err = store.Commit("invalid_tx")
	if err == nil {
		t.Errorf("Expected error when committing with invalid transaction id")
	}
}

func TestIsolation(t *testing.T) {
	nodeAddresses := []string{"node1", "node2", "node3"}
	store, err := NewDistributedKVStore(nodeAddresses)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	txID1, err := store.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}
	err = store.Write(txID1, "key_iso", "uncommitted")
	if err != nil {
		t.Fatalf("Write failed in transaction: %v", err)
	}
	// Do not commit txID1

	txID2, err := store.BeginTransaction()
	if err != nil {
		t.Fatalf("BeginTransaction failed: %v", err)
	}
	val, err := store.Read(txID2, "key_iso")
	if err != nil {
		t.Fatalf("Read failed in txID2: %v", err)
	}
	if val != "" {
		t.Errorf("Isolation failed: uncommitted value is visible, got \"%v\"", val)
	}
	err = store.Commit(txID2)
	if err != nil {
		t.Fatalf("Commit failed: %v", err)
	}
}