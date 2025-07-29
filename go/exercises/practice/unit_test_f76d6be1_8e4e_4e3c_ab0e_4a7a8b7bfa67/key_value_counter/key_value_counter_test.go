package keyvaluecounter

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestBasicIncrementAndGet(t *testing.T) {
	counter := NewDistributedCounter(3) // Start with 3 nodes
	
	tests := []struct {
		key           string
		increments    int
		expectedCount int64
	}{
		{"key1", 1, 1},
		{"key2", 5, 5},
		{"key3", 100, 100},
		{"key1", 2, 3}, // Testing cumulative count
	}

	for _, tt := range tests {
		t.Run(fmt.Sprintf("key=%s_inc=%d", tt.key, tt.increments), func(t *testing.T) {
			for i := 0; i < tt.increments; i++ {
				err := counter.Increment(tt.key)
				if err != nil {
					t.Errorf("Increment failed: %v", err)
				}
			}

			count, err := counter.GetCount(tt.key)
			if err != nil {
				t.Errorf("GetCount failed: %v", err)
			}
			if count != tt.expectedCount {
				t.Errorf("Expected count %d, got %d", tt.expectedCount, count)
			}
		})
	}
}

func TestConcurrentIncrements(t *testing.T) {
	counter := NewDistributedCounter(5)
	const numGoroutines = 100
	const incrementsPerGoroutine = 1000
	
	var wg sync.WaitGroup
	key := "concurrent-test"

	wg.Add(numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		go func() {
			defer wg.Done()
			for j := 0; j < incrementsPerGoroutine; j++ {
				err := counter.Increment(key)
				if err != nil {
					t.Errorf("Concurrent increment failed: %v", err)
				}
			}
		}()
	}

	wg.Wait()

	count, err := counter.GetCount(key)
	if err != nil {
		t.Errorf("GetCount failed: %v", err)
	}

	expected := int64(numGoroutines * incrementsPerGoroutine)
	if count != expected {
		t.Errorf("Expected count %d, got %d", expected, count)
	}
}

func TestNodeFailure(t *testing.T) {
	counter := NewDistributedCounter(5)
	key := "failure-test"

	// Increment several times
	for i := 0; i < 10; i++ {
		err := counter.Increment(key)
		if err != nil {
			t.Errorf("Initial increment failed: %v", err)
		}
	}

	// Simulate node failure
	counter.SimulateNodeFailure(2) // Failing node 2

	// Should still be able to increment and get counts
	err := counter.Increment(key)
	if err != nil {
		t.Errorf("Increment after node failure failed: %v", err)
	}

	_, err = counter.GetCount(key)
	if err != nil {
		t.Errorf("GetCount after node failure failed: %v", err)
	}
}

func TestEventualConsistency(t *testing.T) {
	counter := NewDistributedCounter(3)
	key := "consistency-test"

	// Simulate network partition
	counter.SimulateNetworkPartition()

	// Perform increments during partition
	err := counter.Increment(key)
	if err != nil {
		t.Errorf("Increment during partition failed: %v", err)
	}

	// Wait for potential reconciliation
	time.Sleep(2 * time.Second)

	// Heal partition
	counter.HealNetworkPartition()

	// Wait for consistency
	time.Sleep(2 * time.Second)

	// Verify count is eventually consistent
	count1, err := counter.GetCount(key)
	if err != nil {
		t.Errorf("First GetCount failed: %v", err)
	}

	time.Sleep(1 * time.Second)

	count2, err := counter.GetCount(key)
	if err != nil {
		t.Errorf("Second GetCount failed: %v", err)
	}

	if count1 != count2 {
		t.Errorf("Counts not consistent: %d != %d", count1, count2)
	}
}

func TestScalability(t *testing.T) {
	counter := NewDistributedCounter(3)
	
	// Test adding nodes
	err := counter.AddNode()
	if err != nil {
		t.Errorf("Failed to add node: %v", err)
	}

	// Verify system still works with more nodes
	key := "scale-test"
	for i := 0; i < 100; i++ {
		err := counter.Increment(key)
		if err != nil {
			t.Errorf("Increment failed after scaling: %v", err)
		}
	}

	count, err := counter.GetCount(key)
	if err != nil {
		t.Errorf("GetCount failed after scaling: %v", err)
	}
	if count != 100 {
		t.Errorf("Expected count 100, got %d", count)
	}
}

func BenchmarkIncrement(b *testing.B) {
	counter := NewDistributedCounter(5)
	key := "bench-test"

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		err := counter.Increment(key)
		if err != nil {
			b.Errorf("Benchmark increment failed: %v", err)
		}
	}
}

func BenchmarkConcurrentIncrement(b *testing.B) {
	counter := NewDistributedCounter(5)
	key := "bench-concurrent"
	
	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			err := counter.Increment(key)
			if err != nil {
				b.Errorf("Parallel benchmark increment failed: %v", err)
			}
		}
	})
}

func BenchmarkGetCount(b *testing.B) {
	counter := NewDistributedCounter(5)
	key := "bench-get"

	// Pre-populate with some data
	for i := 0; i < 1000; i++ {
		counter.Increment(key)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_, err := counter.GetCount(key)
		if err != nil {
			b.Errorf("Benchmark get count failed: %v", err)
		}
	}
}