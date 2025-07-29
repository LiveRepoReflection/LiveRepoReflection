package vectorstore

import (
	"reflect"
	"sort"
	"testing"
)

// TestBasicOperations tests simple Put and Get operations
func TestBasicOperations(t *testing.T) {
	store := NewVectorStore(3)
	
	// Store a value
	err := store.Put("key1", "value1", []int{1, 0, 0})
	if err != nil {
		t.Fatalf("Failed to put value: %v", err)
	}
	
	// Retrieve the value
	values, err := store.Get("key1")
	if err != nil {
		t.Fatalf("Failed to get value: %v", err)
	}
	
	if len(values) != 1 {
		t.Fatalf("Expected 1 value, got %d", len(values))
	}
	
	if values[0].Value != "value1" {
		t.Errorf("Expected value1, got %s", values[0].Value)
	}
	
	if !reflect.DeepEqual(values[0].VectorClock, []int{1, 0, 0}) {
		t.Errorf("Expected vector clock [1, 0, 0], got %v", values[0].VectorClock)
	}
}

// TestPutWithInvalidVectorClock tests handling of invalid vector clocks
func TestPutWithInvalidVectorClock(t *testing.T) {
	store := NewVectorStore(3)
	
	// Test with a nil vector clock
	err := store.Put("key1", "value1", nil)
	if err == nil {
		t.Error("Expected error for nil vector clock, got none")
	}
	
	// Test with a vector clock of incorrect length
	err = store.Put("key1", "value1", []int{1, 0})
	if err == nil {
		t.Error("Expected error for vector clock with wrong length, got none")
	}
}

// TestConcurrentUpdates tests handling of concurrent updates
func TestConcurrentUpdates(t *testing.T) {
	store := NewVectorStore(3)
	
	// Store two concurrent updates
	err := store.Put("x", "value1", []int{1, 0, 0})
	if err != nil {
		t.Fatalf("Failed to put value1: %v", err)
	}
	
	err = store.Put("x", "value2", []int{0, 1, 0})
	if err != nil {
		t.Fatalf("Failed to put value2: %v", err)
	}
	
	// Retrieve the values - should get both
	values, err := store.Get("x")
	if err != nil {
		t.Fatalf("Failed to get values: %v", err)
	}
	
	if len(values) != 2 {
		t.Fatalf("Expected 2 values, got %d", len(values))
	}
	
	// Sort values to ensure consistent test results
	sort.Slice(values, func(i, j int) bool {
		return values[i].Value < values[j].Value
	})
	
	if values[0].Value != "value1" || values[1].Value != "value2" {
		t.Errorf("Expected values 'value1' and 'value2', got %s and %s", values[0].Value, values[1].Value)
	}
	
	if !reflect.DeepEqual(values[0].VectorClock, []int{1, 0, 0}) || !reflect.DeepEqual(values[1].VectorClock, []int{0, 1, 0}) {
		t.Errorf("Incorrect vector clocks: %v and %v", values[0].VectorClock, values[1].VectorClock)
	}
}

// TestSupersedingUpdate tests that newer updates supersede older ones
func TestSupersedingUpdate(t *testing.T) {
	store := NewVectorStore(3)
	
	// Store an initial value
	err := store.Put("x", "value1", []int{1, 0, 0})
	if err != nil {
		t.Fatalf("Failed to put value1: %v", err)
	}
	
	// Store a concurrent value
	err = store.Put("x", "value2", []int{0, 1, 0})
	if err != nil {
		t.Fatalf("Failed to put value2: %v", err)
	}
	
	// Store a superseding value that includes both previous updates
	err = store.Put("x", "value3", []int{2, 1, 0})
	if err != nil {
		t.Fatalf("Failed to put value3: %v", err)
	}
	
	// Retrieve the value - should only get the latest one
	values, err := store.Get("x")
	if err != nil {
		t.Fatalf("Failed to get values: %v", err)
	}
	
	if len(values) != 1 {
		t.Fatalf("Expected 1 value, got %d", len(values))
	}
	
	if values[0].Value != "value3" {
		t.Errorf("Expected 'value3', got %s", values[0].Value)
	}
	
	if !reflect.DeepEqual(values[0].VectorClock, []int{2, 1, 0}) {
		t.Errorf("Expected vector clock [2, 1, 0], got %v", values[0].VectorClock)
	}
}

// TestGetNonExistentKey tests behavior when getting a non-existent key
func TestGetNonExistentKey(t *testing.T) {
	store := NewVectorStore(3)
	
	values, err := store.Get("nonexistent")
	if err != nil {
		t.Fatalf("Expected no error for non-existent key, got: %v", err)
	}
	
	if len(values) != 0 {
		t.Errorf("Expected empty result for non-existent key, got %d values", len(values))
	}
}

// TestComplexConflictResolution tests a more complex scenario with multiple updates
func TestComplexConflictResolution(t *testing.T) {
	store := NewVectorStore(3)
	
	// Initial updates from different nodes
	err := store.Put("key", "value1", []int{1, 0, 0})
	if err != nil {
		t.Fatalf("Failed to put value1: %v", err)
	}
	
	err = store.Put("key", "value2", []int{0, 1, 0})
	if err != nil {
		t.Fatalf("Failed to put value2: %v", err)
	}
	
	err = store.Put("key", "value3", []int{0, 0, 1})
	if err != nil {
		t.Fatalf("Failed to put value3: %v", err)
	}
	
	// Node 0 and 1 sync and create a new update
	err = store.Put("key", "value4", []int{1, 1, 0})
	if err != nil {
		t.Fatalf("Failed to put value4: %v", err)
	}
	
	// Node 1 and 2 sync and create a new update
	err = store.Put("key", "value5", []int{0, 2, 1})
	if err != nil {
		t.Fatalf("Failed to put value5: %v", err)
	}
	
	// Get values - should return value4 and value5 as they're concurrent
	values, err := store.Get("key")
	if err != nil {
		t.Fatalf("Failed to get values: %v", err)
	}
	
	if len(values) != 2 {
		t.Fatalf("Expected 2 values, got %d", len(values))
	}
	
	// Sort values to ensure consistent test results
	sort.Slice(values, func(i, j int) bool {
		return values[i].Value < values[j].Value
	})
	
	// Final update that supersedes all
	err = store.Put("key", "valueFinal", []int{2, 2, 1})
	if err != nil {
		t.Fatalf("Failed to put valueFinal: %v", err)
	}
	
	// Get values - should return only valueFinal
	values, err = store.Get("key")
	if err != nil {
		t.Fatalf("Failed to get values: %v", err)
	}
	
	if len(values) != 1 {
		t.Fatalf("Expected 1 value, got %d", len(values))
	}
	
	if values[0].Value != "valueFinal" {
		t.Errorf("Expected 'valueFinal', got %s", values[0].Value)
	}
	
	if !reflect.DeepEqual(values[0].VectorClock, []int{2, 2, 1}) {
		t.Errorf("Expected vector clock [2, 2, 1], got %v", values[0].VectorClock)
	}
}

// TestConcurrentOperations tests that multiple operations can be performed concurrently
func TestConcurrentOperations(t *testing.T) {
	store := NewVectorStore(3)
	done := make(chan bool)
	
	// Perform many operations concurrently
	for i := 0; i < 100; i++ {
		go func(idx int) {
			key := "concurrent"
			value := "value"
			vectorClock := []int{idx % 3, 0, 0}
			
			err := store.Put(key, value+string(rune('0'+idx%10)), vectorClock)
			if err != nil {
				t.Errorf("Failed to put concurrent value: %v", err)
			}
			
			_, err = store.Get(key)
			if err != nil {
				t.Errorf("Failed to get concurrent value: %v", err)
			}
			
			done <- true
		}(i)
	}
	
	// Wait for all operations to complete
	for i := 0; i < 100; i++ {
		<-done
	}
}

// TestMultipleKeys tests operations on multiple keys
func TestMultipleKeys(t *testing.T) {
	store := NewVectorStore(3)
	
	// Add values with different keys
	for i := 0; i < 10; i++ {
		key := "key" + string(rune('0'+i))
		value := "value" + string(rune('0'+i))
		vectorClock := []int{i % 3, (i+1) % 3, (i+2) % 3}
		
		err := store.Put(key, value, vectorClock)
		if err != nil {
			t.Fatalf("Failed to put value for %s: %v", key, err)
		}
	}
	
	// Verify all keys are present
	for i := 0; i < 10; i++ {
		key := "key" + string(rune('0'+i))
		values, err := store.Get(key)
		if err != nil {
			t.Fatalf("Failed to get value for %s: %v", key, err)
		}
		
		if len(values) != 1 {
			t.Fatalf("Expected 1 value for %s, got %d", key, len(values))
		}
		
		expectedValue := "value" + string(rune('0'+i))
		if values[0].Value != expectedValue {
			t.Errorf("Expected %s, got %s", expectedValue, values[0].Value)
		}
	}
}