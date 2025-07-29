package range_store

import (
	"testing"
	"math/rand"
	"strconv"
	"time"
)

func TestPutAndGet(t *testing.T) {
	store := NewRangeStore(3, 2) // 3 nodes, replication factor 2
	key := uint64(12345)
	value := "test_value"

	err := store.Put(key, value)
	if err != nil {
		t.Fatalf("Put failed: %v", err)
	}

	retrieved, err := store.Get(key)
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}

	if retrieved != value {
		t.Errorf("Expected %q, got %q", value, retrieved)
	}
}

func TestRangeQuery(t *testing.T) {
	store := NewRangeStore(5, 3) // 5 nodes, replication factor 3
	r := rand.New(rand.NewSource(time.Now().UnixNano()))

	// Insert 1000 random key-value pairs
	expected := make(map[uint64]string)
	for i := 0; i < 1000; i++ {
		key := r.Uint64()
		value := "value_" + strconv.Itoa(i)
		expected[key] = value
		store.Put(key, value)
	}

	// Test full range query
	results, err := store.RangeQuery(0, ^uint64(0))
	if err != nil {
		t.Fatalf("RangeQuery failed: %v", err)
	}

	// Verify all inserted values are returned
	resultMap := make(map[uint64]string)
	for _, kv := range results {
		resultMap[kv.Key] = kv.Value
	}

	for key, expectedValue := range expected {
		if actualValue, exists := resultMap[key]; !exists || actualValue != expectedValue {
			t.Errorf("Missing or incorrect value for key %d", key)
		}
	}

	// Test partial range query
	start := uint64(1000)
	end := uint64(10000)
	partialResults, err := store.RangeQuery(start, end)
	if err != nil {
		t.Fatalf("RangeQuery failed: %v", err)
	}

	for _, kv := range partialResults {
		if kv.Key < start || kv.Key > end {
			t.Errorf("Key %d outside requested range [%d,%d]", kv.Key, start, end)
		}
		if expected[kv.Key] != kv.Value {
			t.Errorf("Incorrect value for key %d", kv.Key)
		}
	}
}

func TestNodeFailure(t *testing.T) {
	store := NewRangeStore(5, 3) // 5 nodes, replication factor 3
	key := uint64(54321)
	value := "survive_failure"

	err := store.Put(key, value)
	if err != nil {
		t.Fatalf("Put failed: %v", err)
	}

	// Simulate failure of 2 nodes (less than replication factor)
	store.nodes[0].failed = true
	store.nodes[1].failed = true

	retrieved, err := store.Get(key)
	if err != nil {
		t.Fatalf("Get failed after node failures: %v", err)
	}

	if retrieved != value {
		t.Errorf("Expected %q, got %q after node failures", value, retrieved)
	}
}

func TestConcurrentOperations(t *testing.T) {
	store := NewRangeStore(10, 3) // 10 nodes, replication factor 3
	done := make(chan bool)
	numWorkers := 100

	for i := 0; i < numWorkers; i++ {
		go func(workerID int) {
			for j := 0; j < 100; j++ {
				key := uint64(workerID*1000 + j)
				value := strconv.Itoa(workerID) + "_" + strconv.Itoa(j)
				store.Put(key, value)

				if j%10 == 0 {
					store.Get(key)
				}

				if j%20 == 0 {
					store.RangeQuery(uint64(workerID*1000), uint64(workerID*1000+100))
				}
			}
			done <- true
		}(i)
	}

	for i := 0; i < numWorkers; i++ {
		<-done
	}

	// Verify all values were stored correctly
	for i := 0; i < numWorkers; i++ {
		for j := 0; j < 100; j++ {
			key := uint64(i*1000 + j)
			expected := strconv.Itoa(i) + "_" + strconv.Itoa(j)
			actual, err := store.Get(key)
			if err != nil {
				t.Errorf("Get failed for key %d: %v", key, err)
			}
			if actual != expected {
				t.Errorf("For key %d, expected %q, got %q", key, expected, actual)
			}
		}
	}
}

func TestEdgeCases(t *testing.T) {
	store := NewRangeStore(1, 1) // Single node, no replication

	// Test empty range query
	results, err := store.RangeQuery(10, 5) // start > end
	if err != nil {
		t.Fatalf("RangeQuery with invalid range failed: %v", err)
	}
	if len(results) != 0 {
		t.Errorf("Expected empty results for invalid range, got %d items", len(results))
	}

	// Test non-existent key
	_, err = store.Get(999999)
	if err == nil {
		t.Error("Expected error for non-existent key")
	}

	// Test empty store range query
	results, err = store.RangeQuery(0, ^uint64(0))
	if err != nil {
		t.Fatalf("RangeQuery failed: %v", err)
	}
	if len(results) != 0 {
		t.Errorf("Expected empty results for empty store, got %d items", len(results))
	}
}