package consistentcache

import (
	"sync"
	"testing"
	"time"
)

type CacheOperation struct {
	op    string
	key   string
	value string
}

type CacheResult struct {
	value  string
	exists bool
}

func TestDistributedCache(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			// Initialize cache cluster with 3 nodes
			cache := NewCacheCluster(3)

			// Execute operations
			results := make([]CacheResult, 0, len(tc.operations))
			for _, op := range tc.operations {
				switch op.op {
				case "Set":
					cache.Set(op.key, op.value)
					results = append(results, CacheResult{value: "", exists: true})
				case "Get":
					val, exists := cache.Get(op.key)
					results = append(results, CacheResult{value: val, exists: exists})
				case "Delete":
					cache.Delete(op.key)
					results = append(results, CacheResult{value: "", exists: true})
				}
			}

			// Verify results
			if len(results) != len(tc.expected) {
				t.Fatalf("Got %d results, want %d", len(results), len(tc.expected))
			}

			for i, result := range results {
				expected := tc.expected[i]
				if result.exists != expected.exists || result.value != expected.value {
					t.Errorf("Operation %d: got {value: %q, exists: %v}, want {value: %q, exists: %v}",
						i, result.value, result.exists, expected.value, expected.exists)
				}
			}
		})
	}
}

func TestConcurrentOperations(t *testing.T) {
	cache := NewCacheCluster(3)
	const numOperations = 1000
	var wg sync.WaitGroup

	// Concurrent Sets
	wg.Add(numOperations)
	for i := 0; i < numOperations; i++ {
		go func(i int) {
			defer wg.Done()
			key := string(rune(i % 100))
			cache.Set(key, "value")
		}(i)
	}
	wg.Wait()

	// Concurrent Gets
	wg.Add(numOperations)
	for i := 0; i < numOperations; i++ {
		go func(i int) {
			defer wg.Done()
			key := string(rune(i % 100))
			_, _ = cache.Get(key)
		}(i)
	}
	wg.Wait()
}

func TestEventualConsistency(t *testing.T) {
	cache := NewCacheCluster(3)
	
	// Set a value and wait for propagation
	cache.Set("key", "value")
	time.Sleep(100 * time.Millisecond)

	// Check if the value is consistent across all nodes
	for i := 0; i < 3; i++ {
		val, exists := cache.Get("key")
		if !exists || val != "value" {
			t.Errorf("Node %d: got {value: %q, exists: %v}, want {value: %q, exists: %v}",
				i, val, exists, "value", true)
		}
	}
}

func BenchmarkCacheOperations(b *testing.B) {
	cache := NewCacheCluster(3)

	b.Run("Set", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			cache.Set("key", "value")
		}
	})

	b.Run("Get", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			cache.Get("key")
		}
	})

	b.Run("Delete", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			cache.Delete("key")
		}
	})
}
