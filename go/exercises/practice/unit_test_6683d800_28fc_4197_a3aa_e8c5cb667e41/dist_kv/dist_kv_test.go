package dist_kv

import (
	"strconv"
	"sync"
	"testing"
	"time"
)

// TestBasicOperations verifies that a simple put and get operation works as expected.
func TestBasicOperations(t *testing.T) {
	cluster := NewCluster(5, 3)

	err := cluster.Put("foo", "bar")
	if err != nil {
		t.Fatalf("Put operation failed: %v", err)
	}

	value, err := cluster.Get("foo")
	if err != nil {
		t.Fatalf("Get operation failed: %v", err)
	}

	if value != "bar" {
		t.Fatalf("Expected value 'bar' for key 'foo', but got '%s'", value)
	}
}

// TestConflictResolution checks that the Last Write Wins (LWW) strategy works correctly.
// It performs sequential writes with a slight delay to ensure a later timestamp for the second write.
func TestConflictResolution(t *testing.T) {
	cluster := NewCluster(5, 3)

	err := cluster.Put("conflict", "first")
	if err != nil {
		t.Fatalf("First Put operation failed: %v", err)
	}

	// Sleep to simulate later write with a higher timestamp.
	time.Sleep(100 * time.Millisecond)

	err = cluster.Put("conflict", "second")
	if err != nil {
		t.Fatalf("Second Put operation failed: %v", err)
	}

	value, err := cluster.Get("conflict")
	if err != nil {
		t.Fatalf("Get operation failed: %v", err)
	}

	if value != "second" {
		t.Fatalf("Conflict resolution failed, expected 'second' but got '%s'", value)
	}
}

// TestNodeFailure simulates node failures and ensures that the system still processes operations.
func TestNodeFailure(t *testing.T) {
	cluster := NewCluster(5, 3)

	// Simulate node failures.
	cluster.FailNode(0)
	cluster.FailNode(1)

	err := cluster.Put("key", "value")
	if err != nil {
		t.Fatalf("Put operation failed after node failures: %v", err)
	}

	value, err := cluster.Get("key")
	if err != nil {
		t.Fatalf("Get operation failed after node failures: %v", err)
	}

	if value != "value" {
		t.Fatalf("Expected 'value' for key 'key' but got '%s'", value)
	}

	// Recover the failed nodes.
	cluster.RecoverNode(0)
	cluster.RecoverNode(1)
}

// TestConcurrentOperations launches many concurrent put operations and then verifies that
// each key returns the correct value.
func TestConcurrentOperations(t *testing.T) {
	cluster := NewCluster(10, 5)
	var wg sync.WaitGroup
	numOps := 100

	// Concurrent Put operations.
	for i := 0; i < numOps; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			key := "key" + strconv.Itoa(i)
			value := "value" + strconv.Itoa(i)
			if err := cluster.Put(key, value); err != nil {
				t.Errorf("Put error for key %s: %v", key, err)
			}
		}(i)
	}
	wg.Wait()

	// Validate that each key returns the correct value.
	for i := 0; i < numOps; i++ {
		key := "key" + strconv.Itoa(i)
		expected := "value" + strconv.Itoa(i)
		value, err := cluster.Get(key)
		if err != nil {
			t.Errorf("Get error for key %s: %v", key, err)
		}
		if value != expected {
			t.Errorf("Expected value '%s' for key '%s', but got '%s'", expected, key, value)
		}
	}
}

// TestCausalConsistency ensures that causal relationships are maintained.
// Client A writes a value which Client B reads before issuing an update.
// Subsequent reads must reflect at least the update by Client B.
func TestCausalConsistency(t *testing.T) {
	cluster := NewCluster(5, 3)

	// Client A performs a write.
	err := cluster.Put("causal", "A")
	if err != nil {
		t.Fatalf("Client A Put operation failed: %v", err)
	}

	// Client B reads and must see "A".
	value, err := cluster.Get("causal")
	if err != nil {
		t.Fatalf("Client B Get operation failed: %v", err)
	}
	if value != "A" {
		t.Fatalf("Causal consistency error: expected 'A', got '%s'", value)
	}

	// Client B now writes an update that causally follows the previous read.
	err = cluster.Put("causal", "B")
	if err != nil {
		t.Fatalf("Client B second Put operation failed: %v", err)
	}

	// Subsequent reads must reflect "B" (or a later value if there were further updates).
	value, err = cluster.Get("causal")
	if err != nil {
		t.Fatalf("Subsequent Get operation failed: %v", err)
	}
	if value != "B" {
		t.Fatalf("Expected value 'B' after causal update, but got '%s'", value)
	}
}