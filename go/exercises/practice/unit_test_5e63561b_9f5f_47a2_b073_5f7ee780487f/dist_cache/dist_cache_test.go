package dist_cache

import (
	"fmt"
	"math/rand"
	"sync"
	"testing"
	"time"
)

func TestBasicOperations(t *testing.T) {
	cache := NewDistributedCache(3, 2) // 3 nodes, replication factor 2

	tests := []struct {
		key      string
		value    string
		wantErr  bool
		wantMiss bool
	}{
		{"key1", "value1", false, false},
		{"key2", "value2", false, false},
		{"key3", "value3", false, false},
	}

	for _, tt := range tests {
		t.Run(fmt.Sprintf("Put(%s)", tt.key), func(t *testing.T) {
			err := cache.Put(tt.key, tt.value)
			if (err != nil) != tt.wantErr {
				t.Errorf("Put() error = %v, wantErr %v", err, tt.wantErr)
			}
		})

		t.Run(fmt.Sprintf("Get(%s)", tt.key), func(t *testing.T) {
			got, exists := cache.Get(tt.key)
			if !exists && !tt.wantMiss {
				t.Errorf("Get() = missing, want hit")
			}
			if exists && got != tt.value {
				t.Errorf("Get() = %v, want %v", got, tt.value)
			}
		})
	}
}

func TestConcurrentOperations(t *testing.T) {
	cache := NewDistributedCache(5, 3) // 5 nodes, replication factor 3
	const numOps = 1000
	var wg sync.WaitGroup

	// Concurrent writes
	for i := 0; i < numOps; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			key := fmt.Sprintf("key%d", i)
			value := fmt.Sprintf("value%d", i)
			err := cache.Put(key, value)
			if err != nil {
				t.Errorf("Put(%s) error = %v", key, err)
			}
		}(i)
	}

	// Concurrent reads
	for i := 0; i < numOps; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			key := fmt.Sprintf("key%d", i)
			_, _ = cache.Get(key)
		}(i)
	}

	wg.Wait()
}

func TestNodeFailure(t *testing.T) {
	cache := NewDistributedCache(4, 2) // 4 nodes, replication factor 2

	// Put some data
	err := cache.Put("key1", "value1")
	if err != nil {
		t.Fatalf("Put() error = %v", err)
	}

	// Simulate node failure
	cache.SimulateNodeFailure(1) // Node index 1 fails

	// Should still be able to get data
	val, exists := cache.Get("key1")
	if !exists {
		t.Errorf("Get() after node failure = missing, want hit")
	}
	if val != "value1" {
		t.Errorf("Get() = %v, want %v", val, "value1")
	}
}

func TestEventualConsistency(t *testing.T) {
	cache := NewDistributedCache(3, 2) // 3 nodes, replication factor 2

	// Simulate network partition
	cache.SimulateNetworkPartition()

	// Write to different nodes
	err1 := cache.Put("key1", "value1")
	err2 := cache.Put("key1", "value2")

	if err1 != nil || err2 != nil {
		t.Fatalf("Put() errors = %v, %v", err1, err2)
	}

	// Wait for eventual consistency
	time.Sleep(100 * time.Millisecond)

	// Check if eventually consistent
	val, exists := cache.Get("key1")
	if !exists {
		t.Errorf("Get() = missing, want hit")
	}
	if val != "value1" && val != "value2" {
		t.Errorf("Get() = %v, want either %v or %v", val, "value1", "value2")
	}
}

func TestLargeDataHandling(t *testing.T) {
	cache := NewDistributedCache(3, 2)
	
	// Generate 1MB of random data
	largeValue := make([]byte, 1024*1024)
	rand.Read(largeValue)
	largeString := string(largeValue)

	err := cache.Put("largeKey", largeString)
	if err != nil {
		t.Fatalf("Put() error = %v", err)
	}

	val, exists := cache.Get("largeKey")
	if !exists {
		t.Errorf("Get() = missing, want hit")
	}
	if val != largeString {
		t.Errorf("Get() returned incorrect large value")
	}
}

func TestDataPartitioning(t *testing.T) {
	cache := NewDistributedCache(5, 2)

	// Test that keys are distributed across nodes
	keys := []string{"key1", "key2", "key3", "key4", "key5"}
	nodeAssignments := make(map[int]bool)

	for _, key := range keys {
		node := cache.GetResponsibleNode(key)
		nodeAssignments[node] = true
	}

	// Check if keys are distributed
	if len(nodeAssignments) < 2 {
		t.Error("Keys are not being distributed across nodes")
	}
}

func BenchmarkCacheOperations(b *testing.B) {
	cache := NewDistributedCache(5, 3)

	b.Run("Sequential Put", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			key := fmt.Sprintf("key%d", i)
			value := fmt.Sprintf("value%d", i)
			_ = cache.Put(key, value)
		}
	})

	b.Run("Sequential Get", func(b *testing.B) {
		for i := 0; i < b.N; i++ {
			key := fmt.Sprintf("key%d", i)
			_, _ = cache.Get(key)
		}
	})

	b.Run("Parallel Put", func(b *testing.B) {
		b.RunParallel(func(pb *testing.PB) {
			i := 0
			for pb.Next() {
				key := fmt.Sprintf("key%d", i)
				value := fmt.Sprintf("value%d", i)
				_ = cache.Put(key, value)
				i++
			}
		})
	})

	b.Run("Parallel Get", func(b *testing.B) {
		b.RunParallel(func(pb *testing.PB) {
			i := 0
			for pb.Next() {
				key := fmt.Sprintf("key%d", i)
				_, _ = cache.Get(key)
				i++
			}
		})
	})
}