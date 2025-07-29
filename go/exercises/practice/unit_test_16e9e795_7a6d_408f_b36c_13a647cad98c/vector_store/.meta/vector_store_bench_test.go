package vectorstore

import (
	"fmt"
	"sync"
	"testing"
)

// BenchmarkPut measures the performance of Put operations
func BenchmarkPut(b *testing.B) {
	store := NewVectorStore(3)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key%d", i%100)
		value := fmt.Sprintf("value%d", i)
		vectorClock := []int{i % 3, (i / 3) % 3, (i / 9) % 3}
		
		_ = store.Put(key, value, vectorClock)
	}
}

// BenchmarkGet measures the performance of Get operations
func BenchmarkGet(b *testing.B) {
	store := NewVectorStore(3)
	
	// Pre-populate the store with data
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("key%d", i%100)
		value := fmt.Sprintf("value%d", i)
		vectorClock := []int{i % 3, (i / 3) % 3, (i / 9) % 3}
		
		_ = store.Put(key, value, vectorClock)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key%d", i%100)
		_, _ = store.Get(key)
	}
}

// BenchmarkConcurrentOperations measures performance of concurrent operations
func BenchmarkConcurrentOperations(b *testing.B) {
	store := NewVectorStore(3)
	
	// Run b.N operations spread across multiple goroutines
	b.ResetTimer()
	var wg sync.WaitGroup
	
	numGoroutines := 10
	operationsPerGoroutine := b.N / numGoroutines
	
	for g := 0; g < numGoroutines; g++ {
		wg.Add(1)
		go func(offset int) {
			defer wg.Done()
			
			for i := 0; i < operationsPerGoroutine; i++ {
				index := offset*operationsPerGoroutine + i
				
				// Alternate between reads and writes
				if i%2 == 0 {
					key := fmt.Sprintf("key%d", index%100)
					value := fmt.Sprintf("value%d", index)
					vectorClock := []int{index % 3, (index / 3) % 3, (index / 9) % 3}
					
					_ = store.Put(key, value, vectorClock)
				} else {
					key := fmt.Sprintf("key%d", index%100)
					_, _ = store.Get(key)
				}
			}
		}(g)
	}
	
	wg.Wait()
}

// BenchmarkConflictResolution measures the performance of the conflict resolution logic
func BenchmarkConflictResolution(b *testing.B) {
	store := NewVectorStore(5) // Use more nodes to create more complex conflict scenarios
	key := "conflictKey"
	
	// Pre-populate with a few versions to create conflicts
	initialVectorClocks := [][]int{
		{1, 0, 0, 0, 0},
		{0, 1, 0, 0, 0},
		{0, 0, 1, 0, 0},
	}
	
	for i, vc := range initialVectorClocks {
		value := fmt.Sprintf("initial%d", i)
		_ = store.Put(key, value, vc)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		// Create vector clocks that will conflict with existing ones
		nodeIndex := i % 5
		vectorClock := make([]int, 5)
		vectorClock[nodeIndex] = 1
		
		value := fmt.Sprintf("value%d", i)
		_ = store.Put(key, value, vectorClock)
	}
}

// BenchmarkLargeDataset measures performance with a large number of keys
func BenchmarkLargeDataset(b *testing.B) {
	store := NewVectorStore(3)
	
	// Pre-populate with many keys
	for i := 0; i < 10000; i++ {
		key := fmt.Sprintf("key%d", i)
		value := fmt.Sprintf("value%d", i)
		vectorClock := []int{i % 3, (i / 3) % 3, (i / 9) % 3}
		
		_ = store.Put(key, value, vectorClock)
	}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		if i%10 == 0 {
			// 10% of operations are writes
			key := fmt.Sprintf("key%d", i%10000)
			value := fmt.Sprintf("newvalue%d", i)
			vectorClock := []int{1, 1, 1}
			_ = store.Put(key, value, vectorClock)
		} else {
			// 90% of operations are reads
			key := fmt.Sprintf("key%d", i%10000)
			_, _ = store.Get(key)
		}
	}
}