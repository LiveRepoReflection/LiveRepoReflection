package consistentstore

import (
	"bytes"
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestBasicOperations(t *testing.T) {
	store := NewStore()
	serverID := "server1"
	err := store.AddServer(serverID)
	if err != nil {
		t.Fatalf("Failed to add server: %v", err)
	}

	key := []byte("test-key")
	value := []byte("test-value")

	// Test Put
	if err := store.Put(key, value); err != nil {
		t.Fatalf("Failed to put key-value: %v", err)
	}

	// Test Get
	retrieved, err := store.Get(key)
	if err != nil {
		t.Fatalf("Failed to get value: %v", err)
	}
	if !bytes.Equal(retrieved, value) {
		t.Errorf("Got wrong value. Expected %v, got %v", value, retrieved)
	}

	// Test Remove
	if err := store.Remove(key); err != nil {
		t.Fatalf("Failed to remove key: %v", err)
	}

	// Verify key is removed
	_, err = store.Get(key)
	if err == nil {
		t.Error("Expected error when getting removed key")
	}
}

func TestServerOperations(t *testing.T) {
	store := NewStore()
	
	// Add multiple servers
	servers := []string{"server1", "server2", "server3"}
	for _, server := range servers {
		if err := store.AddServer(server); err != nil {
			t.Fatalf("Failed to add server %s: %v", server, err)
		}
	}

	// Add some data
	testData := map[string]string{
		"key1": "value1",
		"key2": "value2",
		"key3": "value3",
	}

	for k, v := range testData {
		err := store.Put([]byte(k), []byte(v))
		if err != nil {
			t.Fatalf("Failed to put key %s: %v", k, err)
		}
	}

	// Remove a server and verify data is still accessible
	if err := store.RemoveServer("server2"); err != nil {
		t.Fatalf("Failed to remove server: %v", err)
	}

	// Verify all data is still accessible
	for k, v := range testData {
		got, err := store.Get([]byte(k))
		if err != nil {
			t.Errorf("Failed to get key %s after server removal: %v", k, err)
			continue
		}
		if !bytes.Equal(got, []byte(v)) {
			t.Errorf("Wrong value for key %s after server removal. Expected %s, got %s", k, v, string(got))
		}
	}
}

func TestConcurrency(t *testing.T) {
	store := NewStore()
	if err := store.AddServer("server1"); err != nil {
		t.Fatalf("Failed to add server: %v", err)
	}

	var wg sync.WaitGroup
	concurrentOps := 100

	// Concurrent puts
	for i := 0; i < concurrentOps; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			key := []byte(fmt.Sprintf("key-%d", i))
			value := []byte(fmt.Sprintf("value-%d", i))
			err := store.Put(key, value)
			if err != nil {
				t.Errorf("Concurrent put failed: %v", err)
			}
		}(i)
	}

	wg.Wait()

	// Verify all values
	for i := 0; i < concurrentOps; i++ {
		key := []byte(fmt.Sprintf("key-%d", i))
		expectedValue := []byte(fmt.Sprintf("value-%d", i))
		got, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get key %s: %v", key, err)
			continue
		}
		if !bytes.Equal(got, expectedValue) {
			t.Errorf("Wrong value for key %s. Expected %s, got %s", key, expectedValue, got)
		}
	}
}

func TestReplication(t *testing.T) {
	store := NewStore()
	servers := []string{"server1", "server2", "server3", "server4"}
	
	// Add servers
	for _, server := range servers {
		if err := store.AddServer(server); err != nil {
			t.Fatalf("Failed to add server %s: %v", server, err)
		}
	}

	key := []byte("replicated-key")
	value := []byte("replicated-value")

	// Put with replication
	if err := store.Put(key, value); err != nil {
		t.Fatalf("Failed to put replicated value: %v", err)
	}

	// Remove a server and verify data is still accessible
	if err := store.RemoveServer(servers[0]); err != nil {
		t.Fatalf("Failed to remove server: %v", err)
	}

	// Data should still be accessible due to replication
	got, err := store.Get(key)
	if err != nil {
		t.Fatalf("Failed to get replicated value after server removal: %v", err)
	}
	if !bytes.Equal(got, value) {
		t.Errorf("Wrong replicated value. Expected %s, got %s", value, got)
	}
}

func TestLoadBalancing(t *testing.T) {
	store := NewStore()
	servers := []string{"server1", "server2", "server3", "server4"}
	
	// Add servers
	for _, server := range servers {
		if err := store.AddServer(server); err != nil {
			t.Fatalf("Failed to add server %s: %v", server, err)
		}
	}

	// Add many keys
	keyCount := 1000
	for i := 0; i < keyCount; i++ {
		key := []byte(fmt.Sprintf("key-%d", i))
		value := []byte(fmt.Sprintf("value-%d", i))
		if err := store.Put(key, value); err != nil {
			t.Fatalf("Failed to put key %s: %v", key, err)
		}
	}

	// Verify distribution (this is a simple check, real implementation would need more sophisticated verification)
	time.Sleep(100 * time.Millisecond) // Allow time for distribution

	for i := 0; i < keyCount; i++ {
		key := []byte(fmt.Sprintf("key-%d", i))
		_, err := store.Get(key)
		if err != nil {
			t.Errorf("Failed to get key %s: %v", key, err)
		}
	}
}

func TestErrorCases(t *testing.T) {
	store := NewStore()

	// Test operations before adding any servers
	key := []byte("test-key")
	value := []byte("test-value")
	
	if err := store.Put(key, value); err == nil {
		t.Error("Expected error when putting to store with no servers")
	}

	if _, err := store.Get(key); err == nil {
		t.Error("Expected error when getting from store with no servers")
	}

	// Test adding duplicate server
	serverID := "server1"
	if err := store.AddServer(serverID); err != nil {
		t.Fatalf("Failed to add server: %v", err)
	}

	if err := store.AddServer(serverID); err == nil {
		t.Error("Expected error when adding duplicate server")
	}

	// Test removing non-existent server
	if err := store.RemoveServer("non-existent-server"); err == nil {
		t.Error("Expected error when removing non-existent server")
	}

	// Test nil key/value
	if err := store.Put(nil, value); err == nil {
		t.Error("Expected error when putting nil key")
	}

	if err := store.Put(key, nil); err == nil {
		t.Error("Expected error when putting nil value")
	}
}

func BenchmarkPut(b *testing.B) {
	store := NewStore()
	if err := store.AddServer("server1"); err != nil {
		b.Fatalf("Failed to add server: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := []byte(fmt.Sprintf("bench-key-%d", i))
		value := []byte(fmt.Sprintf("bench-value-%d", i))
		if err := store.Put(key, value); err != nil {
			b.Fatalf("Benchmark Put failed: %v", err)
		}
	}
}

func BenchmarkGet(b *testing.B) {
	store := NewStore()
	if err := store.AddServer("server1"); err != nil {
		b.Fatalf("Failed to add server: %v", err)
	}

	key := []byte("bench-key")
	value := []byte("bench-value")
	if err := store.Put(key, value); err != nil {
		b.Fatalf("Failed to put benchmark value: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		if _, err := store.Get(key); err != nil {
			b.Fatalf("Benchmark Get failed: %v", err)
		}
	}
}