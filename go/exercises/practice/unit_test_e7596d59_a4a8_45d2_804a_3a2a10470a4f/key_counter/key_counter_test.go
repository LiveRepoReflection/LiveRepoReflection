package key_counter

import (
	"reflect"
	"sync"
	"testing"
)

// Assume the existence of the following types and constructor in the implementation:
//
// type KeyCount struct {
// 	Key   string
// 	Count int
// }
//
// // NewKeyCounter creates and returns a new instance of the key-counter service.
// func NewKeyCounter() KeyCounterService
//
// // KeyCounterService defines the required operations.
// type KeyCounterService interface {
// 	Increment(key string, value int) error
// 	Get(key string) (int, error)
// 	TopK(k int) ([]KeyCount, error)
// }

func TestIncrementAndGet(t *testing.T) {
	kc := NewKeyCounter()
	// Test single increment.
	if err := kc.Increment("apple", 5); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}
	count, err := kc.Get("apple")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	if count != 5 {
		t.Fatalf("expected count 5 for 'apple', got %d", count)
	}
	// Test multiple increments on the same key.
	if err := kc.Increment("apple", 3); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}
	count, err = kc.Get("apple")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	if count != 8 {
		t.Fatalf("expected count 8 for 'apple', got %d", count)
	}
}

func TestTopK(t *testing.T) {
	kc := NewKeyCounter()
	// Insert multiple keys with different counts.
	if err := kc.Increment("apple", 8); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}
	if err := kc.Increment("banana", 12); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}
	if err := kc.Increment("cherry", 12); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}
	if err := kc.Increment("date", 7); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}

	// When two keys have the same count, they should be sorted lexicographically.
	top2, err := kc.TopK(2)
	if err != nil {
		t.Fatalf("TopK failed: %v", err)
	}
	expected := []KeyCount{
		{Key: "banana", Count: 12},
		{Key: "cherry", Count: 12},
	}
	if !reflect.DeepEqual(top2, expected) {
		t.Fatalf("expected TopK %v, got %v", expected, top2)
	}

	// Test when k is larger than the number of keys.
	top10, err := kc.TopK(10)
	if err != nil {
		t.Fatalf("TopK failed: %v", err)
	}
	if len(top10) != 4 {
		t.Fatalf("expected TopK length 4, got %d", len(top10))
	}
}

func TestNonExistentKey(t *testing.T) {
	kc := NewKeyCounter()
	// Test Get on a non-existent key.
	count, err := kc.Get("nonexistent")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	if count != 0 {
		t.Fatalf("expected default count 0 for 'nonexistent', got %d", count)
	}
	// Test TopK on an empty key-counter.
	top, err := kc.TopK(1)
	if err != nil {
		t.Fatalf("TopK failed: %v", err)
	}
	if len(top) != 0 {
		t.Fatalf("expected empty TopK for an empty counter, got %v", top)
	}
}

func TestConcurrentIncrements(t *testing.T) {
	kc := NewKeyCounter()
	var wg sync.WaitGroup
	numGoroutines := 10
	iterations := 1000

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < iterations; j++ {
				if err := kc.Increment("concurrent", 1); err != nil {
					t.Errorf("Concurrent Increment failed: %v", err)
				}
			}
		}()
	}
	wg.Wait()

	count, err := kc.Get("concurrent")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	expected := numGoroutines * iterations
	if count != expected {
		t.Fatalf("expected count %d for 'concurrent', got %d", expected, count)
	}
}

func TestEdgeCases(t *testing.T) {
	kc := NewKeyCounter()
	// Increment by zero should not change the count.
	if err := kc.Increment("zero", 0); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}
	count, err := kc.Get("zero")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	if count != 0 {
		t.Fatalf("expected count 0 for 'zero' after zero increment, got %d", count)
	}

	// Test negative increment.
	if err := kc.Increment("negative", -5); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}
	count, err = kc.Get("negative")
	if err != nil {
		t.Fatalf("Get failed: %v", err)
	}
	if count != -5 {
		t.Fatalf("expected count -5 for 'negative', got %d", count)
	}

	// Test TopK when k is larger than the total number of keys.
	if err := kc.Increment("key1", 10); err != nil {
		t.Fatalf("Increment failed: %v", err)
	}
	topK, err := kc.TopK(10)
	if err != nil {
		t.Fatalf("TopK failed: %v", err)
	}
	// Expected keys: "negative", "apple" (if not used from other tests), "key1", "zero".
	if len(topK) < 1 {
		t.Fatalf("expected at least one key in TopK, got %d", len(topK))
	}
}