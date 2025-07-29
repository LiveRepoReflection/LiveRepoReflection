package cache_invalidation

import (
	"sync"
	"testing"
	"time"
)

// TestCacheSetAndGet verifies that a cache server can store and retrieve data.
func TestCacheSetAndGet(t *testing.T) {
	server := NewCacheServer("server1")
	server.Set("user123", "data1")
	val, ok := server.Get("user123")
	if !ok {
		t.Fatalf("expected key 'user123' to exist")
	}
	if val != "data1" {
		t.Fatalf("expected value 'data1' for key 'user123', got %v", val)
	}
}

// TestInvalidation verifies that an invalidation message removes the appropriate key
// from a single cache server.
func TestInvalidation(t *testing.T) {
	server := NewCacheServer("server1")
	server.Set("user123", "data1")
	msg := InvalidationMessage{
		Key:       "user123",
		Timestamp: time.Now().UnixNano(),
	}
	server.Invalidate(msg)
	_, ok := server.Get("user123")
	if ok {
		t.Fatalf("expected key 'user123' to be invalidated and removed")
	}
}

// TestDistributedInvalidation verifies that a broadcast invalidation message
// properly invalidates data on multiple cache servers.
func TestDistributedInvalidation(t *testing.T) {
	server1 := NewCacheServer("server1")
	server2 := NewCacheServer("server2")

	// All servers set the same key with the same value.
	server1.Set("user123", "data1")
	server2.Set("user123", "data1")

	msg := InvalidationMessage{
		Key:       "user123",
		Timestamp: time.Now().UnixNano(),
	}
	servers := []*CacheServer{server1, server2}
	var wg sync.WaitGroup
	for _, srv := range servers {
		wg.Add(1)
		go func(s *CacheServer) {
			defer wg.Done()
			s.Invalidate(msg)
		}(srv)
	}
	wg.Wait()

	_, ok1 := server1.Get("user123")
	_, ok2 := server2.Get("user123")
	if ok1 || ok2 {
		t.Fatalf("expected key 'user123' to be invalidated on all servers")
	}
}

// TestInvalidationOrdering tests that when invalidation messages are processed out of order,
// the system retains the value if an older invalidation arrives after a more recent update.
func TestInvalidationOrdering(t *testing.T) {
	server := NewCacheServer("server1")
	// Set initial value with version 100 using SetWithVersion (if implemented).
	server.SetWithVersion("user123", "data1", 100)

	// Send an older invalidation message with timestamp 90.
	msgOld := InvalidationMessage{
		Key:       "user123",
		Timestamp: 90,
	}
	server.Invalidate(msgOld)
	val, ok := server.Get("user123")
	if !ok || val != "data1" {
		t.Fatalf("older invalidation should not remove the current key; got value: %v, exists: %v", val, ok)
	}

	// Send a newer invalidation message with timestamp 110.
	msgNew := InvalidationMessage{
		Key:       "user123",
		Timestamp: 110,
	}
	server.Invalidate(msgNew)
	_, ok = server.Get("user123")
	if ok {
		t.Fatalf("newer invalidation should remove the key 'user123'")
	}
}

// TestConcurrentInvalidations tests the system under concurrent invalidation messages.
func TestConcurrentInvalidations(t *testing.T) {
	server := NewCacheServer("server1")
	key := "resource456"
	// Set the key initially.
	server.Set(key, "initial_data")

	// Create a list of invalidation messages with increasing timestamps.
	var messages []InvalidationMessage
	baseTime := time.Now().UnixNano()
	for i := 0; i < 100; i++ {
		messages = append(messages, InvalidationMessage{
			Key:       key,
			Timestamp: baseTime + int64(i),
		})
	}

	// Shuffle the messages to simulate concurrent and out-of-order arrival.
	var wg sync.WaitGroup
	for _, msg := range messages {
		wg.Add(1)
		go func(m InvalidationMessage) {
			defer wg.Done()
			// Sleep a tiny random duration to simulate network delays.
			time.Sleep(time.Duration(m.Timestamp%10) * time.Microsecond)
			server.Invalidate(m)
		}(msg)
	}
	wg.Wait()

	_, ok := server.Get(key)
	if ok {
		t.Fatalf("expected key '%s' to be invalidated concurrently", key)
	}
}