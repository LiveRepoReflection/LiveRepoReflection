package consistent_kvs_test

import (
	"sync"
	"testing"
	"time"

	"consistent_kvs"
)

func TestSingleNodeBasic(t *testing.T) {
	store, err := consistent_kvs.NewStore(1, 1)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	// Test Put operation
	err = store.Put("key1", "value1")
	if err != nil {
		t.Errorf("Put operation failed: %v", err)
	}

	// Test Get operation
	value, err := store.Get("key1")
	if err != nil {
		t.Errorf("Get operation failed: %v", err)
	}
	if value != "value1" {
		t.Errorf("expected value 'value1', got '%s'", value)
	}
}

func TestReplication(t *testing.T) {
	// Initialize a store with 3 nodes and replication factor of 2.
	store, err := consistent_kvs.NewStore(3, 2)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	keys := []string{"alpha", "beta", "gamma", "delta"}
	// Insert several key-value pairs.
	for _, key := range keys {
		err = store.Put(key, key+"-value")
		if err != nil {
			t.Errorf("Put failed for key %s: %v", key, err)
		}
	}

	// Simulate a node failure.
	err = store.SimulateNodeFailure(0)
	if err != nil {
		t.Errorf("SimulateNodeFailure failed: %v", err)
	}

	// Validate reads from the remaining replicas.
	for _, key := range keys {
		value, err := store.Get(key)
		if err != nil {
			t.Errorf("Get failed for key %s: %v", key, err)
		}
		if value != key+"-value" {
			t.Errorf("expected %s for key %s, got %s", key+"-value", key, value)
		}
	}
}

func TestConcurrentAccess(t *testing.T) {
	// Initialize a store with 5 nodes and replication factor of 3.
	store, err := consistent_kvs.NewStore(5, 3)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	var wg sync.WaitGroup
	totalOps := 100

	// Concurrently perform Put operations.
	for i := 0; i < totalOps; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			key := "key" + string(rune(i))
			value := "value" + string(rune(i))
			if err := store.Put(key, value); err != nil {
				t.Errorf("Put failed for key %s: %v", key, err)
			}
		}(i)
	}

	// Concurrently perform Get operations.
	for i := 0; i < totalOps; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			// Introduce a small delay to allow some Put operations to complete
			time.Sleep(5 * time.Millisecond)
			key := "key" + string(rune(i))
			value, err := store.Get(key)
			if err != nil {
				// It is acceptable if the key is not found due to timing
				if err != consistent_kvs.ErrKeyNotFound {
					t.Errorf("Get failed for key %s: %v", key, err)
				}
				return
			}
			expected := "value" + string(rune(i))
			if value != expected {
				t.Errorf("expected %s for key %s, got %s", expected, key, value)
			}
		}(i)
	}

	wg.Wait()
}

func TestSequentialConsistency(t *testing.T) {
	// Initialize a store with 3 nodes and replication factor of 2.
	store, err := consistent_kvs.NewStore(3, 2)
	if err != nil {
		t.Fatalf("failed to initialize store: %v", err)
	}

	// Execute a known sequence of operations.
	ops := []struct {
		op    string
		key   string
		value string
	}{
		{"put", "x", "1"},
		{"put", "y", "2"},
		{"put", "x", "3"},
	}

	for _, op := range ops {
		if op.op == "put" {
			if err := store.Put(op.key, op.value); err != nil {
				t.Errorf("Put operation failed for key %s: %v", op.key, err)
			}
		}
	}

	// Test that the most recent write is visible.
	value, err := store.Get("x")
	if err != nil {
		t.Errorf("Get operation failed for key x: %v", err)
	}
	if value != "3" {
		t.Errorf("expected value '3' for key x, got '%s'", value)
	}
}