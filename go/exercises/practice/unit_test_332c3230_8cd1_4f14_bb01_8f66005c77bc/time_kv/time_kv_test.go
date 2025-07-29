package time_kv

import (
	"sync"
	"testing"
	"time"
)

func TestSetAndGet(t *testing.T) {
	store := NewTimeKVStore()
	now := time.Now().UnixMilli()

	store.Set("key1", "value1", now)
	if val := store.Get("key1", now); val != "value1" {
		t.Errorf("Get() = %v, want %v", val, "value1")
	}

	store.Set("key1", "value2", now+100)
	if val := store.Get("key1", now+100); val != "value2" {
		t.Errorf("Get() = %v, want %v", val, "value2")
	}

	if val := store.Get("key1", now+50); val != "value1" {
		t.Errorf("Get() = %v, want %v", val, "value1")
	}

	if val := store.Get("nonexistent", now); val != "" {
		t.Errorf("Get() = %v, want %v", val, "")
	}
}

func TestConflictResolution(t *testing.T) {
	store := NewTimeKVStore()
	now := time.Now().UnixMilli()

	store.SetWithNodeID("key1", "value1", now, 1)
	store.SetWithNodeID("key1", "value2", now, 2)

	if val := store.Get("key1", now); val != "value2" {
		t.Errorf("Get() = %v, want %v (higher node ID should win)", val, "value2")
	}
}

func TestMultiGet(t *testing.T) {
	store := NewTimeKVStore()
	now := time.Now().UnixMilli()

	store.Set("key1", "value1", now)
	store.Set("key2", "value2", now)
	store.Set("key3", "value3", now+100)

	result := store.MultiGet([]string{"key1", "key2", "key3", "nonexistent"}, now+50)
	expected := map[string]string{
		"key1": "value1",
		"key2": "value2",
		"key3": "",
	}

	for k, v := range expected {
		if result[k] != v {
			t.Errorf("MultiGet()[%s] = %v, want %v", k, result[k], v)
		}
	}
}

func TestRangeGet(t *testing.T) {
	store := NewTimeKVStore()
	now := time.Now().UnixMilli()

	store.Set("key1", "value1", now)
	store.Set("key1", "value2", now+100)
	store.Set("key1", "value3", now+200)
	store.Set("key1", "value4", now+300)

	results := store.RangeGet("key1", now+50, now+250)
	expected := []TimeValue{
		{Value: "value2", Timestamp: now + 100},
		{Value: "value3", Timestamp: now + 200},
	}

	if len(results) != len(expected) {
		t.Fatalf("RangeGet() returned %d items, want %d", len(results), len(expected))
	}

	for i, tv := range expected {
		if results[i] != tv {
			t.Errorf("RangeGet()[%d] = %v, want %v", i, results[i], tv)
		}
	}
}

func TestConcurrentAccess(t *testing.T) {
	store := NewTimeKVStore()
	now := time.Now().UnixMilli()
	var wg sync.WaitGroup

	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(nodeID int) {
			defer wg.Done()
			store.SetWithNodeID("concurrent", "value", now, nodeID)
		}(i)
	}

	wg.Wait()

	if val := store.Get("concurrent", now); val != "value" {
		t.Errorf("Get() after concurrent writes = %v, want %v", val, "value")
	}
}

func TestEdgeCases(t *testing.T) {
	store := NewTimeKVStore()

	// Empty key
	store.Set("", "empty", 0)
	if val := store.Get("", 0); val != "empty" {
		t.Errorf("Get() empty key = %v, want %v", val, "empty")
	}

	// Negative timestamp
	store.Set("neg", "value", -100)
	if val := store.Get("neg", -100); val != "value" {
		t.Errorf("Get() negative timestamp = %v, want %v", val, "value")
	}

	// Empty MultiGet
	if result := store.MultiGet([]string{}, 0); len(result) != 0 {
		t.Errorf("MultiGet() empty keys = %v, want empty map", result)
	}

	// Empty RangeGet
	if result := store.RangeGet("nonexistent", 0, 100); len(result) != 0 {
		t.Errorf("RangeGet() nonexistent key = %v, want empty slice", result)
	}
}