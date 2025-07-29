package concurrentkv

import (
	"fmt"
	"math/rand"
	"sync"
	"testing"
	"time"
)

func TestBasicOperations(t *testing.T) {
	store := New()

	// Test Put and Get
	store.Put("key1", "value1")
	if val, exists := store.Get("key1"); !exists || val != "value1" {
		t.Errorf("Expected value1, got %v, exists: %v", val, exists)
	}

	// Test non-existent key
	if val, exists := store.Get("nonexistent"); exists {
		t.Errorf("Expected no value for nonexistent key, got %v", val)
	}

	// Test Delete
	store.Delete("key1")
	if _, exists := store.Get("key1"); exists {
		t.Error("Key should not exist after deletion")
	}
}

func TestConcurrentOperations(t *testing.T) {
	store := New()
	var wg sync.WaitGroup
	numGoroutines := 100
	operationsPerGoroutine := 1000

	// Concurrent writes
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(routineID int) {
			defer wg.Done()
			for j := 0; j < operationsPerGoroutine; j++ {
				key := fmt.Sprintf("key-%d-%d", routineID, j)
				value := fmt.Sprintf("value-%d-%d", routineID, j)
				store.Put(key, value)
			}
		}(i)
	}

	// Concurrent reads and writes
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(routineID int) {
			defer wg.Done()
			for j := 0; j < operationsPerGoroutine; j++ {
				key := fmt.Sprintf("key-%d-%d", routineID, j)
				store.Get(key)
			}
		}(i)
	}

	wg.Wait()
}

func TestSnapshot(t *testing.T) {
	store := New()
	testData := map[string]string{
		"key1": "value1",
		"key2": "value2",
		"key3": "value3",
	}

	// Populate store
	for k, v := range testData {
		store.Put(k, v)
	}

	// Take snapshot
	snapshot := store.Snapshot()

	// Verify snapshot contents
	if len(snapshot) != len(testData) {
		t.Errorf("Expected snapshot size %d, got %d", len(testData), len(snapshot))
	}

	for k, v := range testData {
		if sv, exists := snapshot[k]; !exists || sv != v {
			t.Errorf("Snapshot mismatch for key %s: expected %s, got %s", k, v, sv)
		}
	}

	// Modify store after snapshot
	store.Put("key4", "value4")
	store.Delete("key1")

	// Verify snapshot remains unchanged
	if _, exists := snapshot["key4"]; exists {
		t.Error("Snapshot should not contain new key")
	}
	if _, exists := snapshot["key1"]; !exists {
		t.Error("Snapshot should still contain deleted key")
	}
}

func TestConcurrentSnapshotOperations(t *testing.T) {
	store := New()
	var wg sync.WaitGroup
	numOperations := 1000

	// Start continuous writes
	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := 0; i < numOperations; i++ {
			key := fmt.Sprintf("key-%d", i)
			value := fmt.Sprintf("value-%d", i)
			store.Put(key, value)
			time.Sleep(time.Microsecond)
		}
	}()

	// Take snapshots while writing
	wg.Add(1)
	go func() {
		defer wg.Done()
		for i := 0; i < 10; i++ {
			snapshot := store.Snapshot()
			if len(snapshot) < 0 {
				t.Error("Invalid snapshot size")
			}
			time.Sleep(time.Millisecond)
		}
	}()

	wg.Wait()
}

func TestLargeDataSet(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping large dataset test in short mode")
	}

	store := New()
	numEntries := 100000

	// Insert large number of entries
	for i := 0; i < numEntries; i++ {
		key := fmt.Sprintf("key-%d", i)
		value := fmt.Sprintf("value-%d", i)
		store.Put(key, value)
	}

	// Verify random access
	for i := 0; i < 1000; i++ {
		idx := rand.Intn(numEntries)
		key := fmt.Sprintf("key-%d", idx)
		expectedValue := fmt.Sprintf("value-%d", idx)
		if val, exists := store.Get(key); !exists || val != expectedValue {
			t.Errorf("Expected %s, got %s, exists: %v", expectedValue, val, exists)
		}
	}
}

func BenchmarkPut(b *testing.B) {
	store := New()
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key-%d", i)
		value := fmt.Sprintf("value-%d", i)
		store.Put(key, value)
	}
}

func BenchmarkGet(b *testing.B) {
	store := New()
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("key-%d", i)
		value := fmt.Sprintf("value-%d", i)
		store.Put(key, value)
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key-%d", i%1000)
		store.Get(key)
	}
}

func BenchmarkDelete(b *testing.B) {
	store := New()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key-%d", i)
		value := fmt.Sprintf("value-%d", i)
		store.Put(key, value)
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("key-%d", i)
		store.Delete(key)
	}
}

func BenchmarkSnapshot(b *testing.B) {
	store := New()
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("key-%d", i)
		value := fmt.Sprintf("value-%d", i)
		store.Put(key, value)
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		store.Snapshot()
	}
}

func BenchmarkConcurrentOperations(b *testing.B) {
	store := New()
	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		i := 0
		for pb.Next() {
			key := fmt.Sprintf("key-%d", i)
			value := fmt.Sprintf("value-%d", i)
			store.Put(key, value)
			store.Get(key)
			store.Delete(key)
			i++
		}
	})
}