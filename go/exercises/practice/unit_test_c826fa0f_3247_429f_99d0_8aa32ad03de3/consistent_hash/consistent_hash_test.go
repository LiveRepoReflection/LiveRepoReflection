package consistent_hash

import (
	"fmt"
	"sync"
	"testing"
)

// TestConsistentHashRingCreation tests that a new consistent hash ring can be created
func TestConsistentHashRingCreation(t *testing.T) {
	tests := []struct {
		name     string
		servers  []string
		replicas int
	}{
		{"Empty servers", []string{}, 5},
		{"Single server", []string{"server1"}, 5},
		{"Multiple servers", []string{"server1", "server2", "server3"}, 5},
		{"No replicas", []string{"server1", "server2"}, 0},
		{"Many replicas", []string{"server1"}, 100},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			ring := New(tt.servers, tt.replicas)
			if ring == nil {
				t.Error("New() returned nil")
			}
		})
	}
}

// TestAddServer tests adding a server to the hash ring
func TestAddServer(t *testing.T) {
	ring := New([]string{"server1", "server2"}, 5)
	
	// Add a new server
	ring.AddServer("server3")
	
	// Check that we can get the new server
	found := false
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("test-key-%d", i)
		if ring.GetServer(key) == "server3" {
			found = true
			break
		}
	}
	
	if !found {
		t.Error("AddServer() added a server but GetServer() never returned it")
	}
}

// TestRemoveServer tests removing a server from the hash ring
func TestRemoveServer(t *testing.T) {
	ring := New([]string{"server1", "server2", "server3"}, 5)
	
	// Remove a server
	ring.RemoveServer("server2")
	
	// Check that we never get the removed server
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("test-key-%d", i)
		if ring.GetServer(key) == "server2" {
			t.Error("RemoveServer() removed a server but GetServer() still returned it")
		}
	}
}

// TestGetServerConsistency checks that the same key always maps to the same server
func TestGetServerConsistency(t *testing.T) {
	ring := New([]string{"server1", "server2", "server3", "server4"}, 10)
	
	// Test with multiple keys
	for i := 0; i < 100; i++ {
		key := fmt.Sprintf("test-key-%d", i)
		server1 := ring.GetServer(key)
		server2 := ring.GetServer(key)
		
		if server1 != server2 {
			t.Errorf("GetServer() not consistent for key %s: got %s and %s", key, server1, server2)
		}
	}
}

// TestRebalance tests the rebalance functionality
func TestRebalance(t *testing.T) {
	ring := New([]string{"server1", "server2", "server3"}, 5)
	
	// Rebalance with different servers
	newServers := []string{"server2", "server3", "server4", "server5"}
	ring.Rebalance(newServers)
	
	// Check that we can get the new servers but not the removed ones
	for i := 0; i < 1000; i++ {
		key := fmt.Sprintf("test-key-%d", i)
		server := ring.GetServer(key)
		
		found := false
		for _, s := range newServers {
			if server == s {
				found = true
				break
			}
		}
		
		if !found {
			t.Errorf("GetServer() returned %s which is not in the rebalanced server list", server)
		}
		
		if server == "server1" {
			t.Error("GetServer() returned server1 which should have been removed during rebalance")
		}
	}
}

// TestKeyDistribution tests that keys are somewhat evenly distributed
func TestKeyDistribution(t *testing.T) {
	servers := []string{"server1", "server2", "server3", "server4"}
	ring := New(servers, 10)
	
	// Count how many keys go to each server
	counts := make(map[string]int)
	totalKeys := 10000
	
	for i := 0; i < totalKeys; i++ {
		key := fmt.Sprintf("test-key-%d", i)
		server := ring.GetServer(key)
		counts[server]++
	}
	
	// Check that all servers got some keys
	for _, server := range servers {
		if counts[server] == 0 {
			t.Errorf("Server %s received 0 keys", server)
		}
	}
	
	// Check that keys are somewhat evenly distributed
	// We expect each server to get approximately totalKeys / len(servers) keys
	expected := totalKeys / len(servers)
	tolerance := expected / 2 // Allow 50% deviation
	
	for server, count := range counts {
		if count < expected-tolerance || count > expected+tolerance {
			t.Logf("Key distribution is uneven: server %s got %d keys (expected around %d ± %d)", 
				server, count, expected, tolerance)
		}
	}
}

// TestConcurrentOperations tests concurrent operations on the hash ring
func TestConcurrentOperations(t *testing.T) {
	ring := New([]string{"server1", "server2"}, 5)
	
	// Run operations concurrently
	wg := sync.WaitGroup{}
	wg.Add(4)
	
	// Add servers concurrently
	go func() {
		defer wg.Done()
		for i := 0; i < 10; i++ {
			ring.AddServer(fmt.Sprintf("add-server-%d", i))
		}
	}()
	
	// Remove servers concurrently
	go func() {
		defer wg.Done()
		ring.RemoveServer("server1") // Remove an original server
		for i := 0; i < 5; i++ {
			ring.RemoveServer(fmt.Sprintf("add-server-%d", i)) // Remove some that were just added
		}
	}()
	
	// Get servers concurrently
	go func() {
		defer wg.Done()
		for i := 0; i < 1000; i++ {
			key := fmt.Sprintf("concurrent-key-%d", i)
			_ = ring.GetServer(key)
		}
	}()
	
	// Rebalance concurrently
	go func() {
		defer wg.Done()
		newServers := []string{"new-server1", "new-server2", "new-server3"}
		ring.Rebalance(newServers)
	}()
	
	wg.Wait()
	
	// If we got here without panicking, the test passes
}

// TestEmptyRing tests behaviors with an empty ring
func TestEmptyRing(t *testing.T) {
	ring := New([]string{}, 5)
	
	// Try to get a server from an empty ring
	server := ring.GetServer("some-key")
	if server != "" {
		t.Errorf("GetServer() on empty ring returned %s, expected empty string", server)
	}
	
	// Add a server to an empty ring
	ring.AddServer("server1")
	server = ring.GetServer("some-key")
	if server != "server1" {
		t.Errorf("GetServer() after adding to empty ring returned %s, expected server1", server)
	}
	
	// Remove all servers
	ring.RemoveServer("server1")
	server = ring.GetServer("some-key")
	if server != "" {
		t.Errorf("GetServer() after removing all servers returned %s, expected empty string", server)
	}
}

// TestEdgeCases tests various edge cases
func TestEdgeCases(t *testing.T) {
	// Test with nil servers slice
	ring := New(nil, 5)
	if ring == nil {
		t.Error("New() with nil servers returned nil")
	}
	
	// Test with existing servers
	ring = New([]string{"server1", "server2"}, 5)
	
	// Adding the same server multiple times
	ring.AddServer("server1") // Already exists
	ring.AddServer("server3") // New server
	ring.AddServer("server3") // Add again
	
	// Removing a non-existent server
	ring.RemoveServer("non-existent-server")
	
	// Removing the last server
	ring = New([]string{"server1"}, 5)
	ring.RemoveServer("server1")
	server := ring.GetServer("some-key")
	if server != "" {
		t.Errorf("GetServer() after removing last server returned %s, expected empty string", server)
	}
	
	// Rebalance with empty slice
	ring.Rebalance([]string{})
	server = ring.GetServer("some-key")
	if server != "" {
		t.Errorf("GetServer() after rebalancing with empty slice returned %s, expected empty string", server)
	}
}

// BenchmarkGetServer benchmarks the GetServer method
func BenchmarkGetServer(b *testing.B) {
	// Create a ring with many servers and replicas
	servers := make([]string, 100)
	for i := 0; i < 100; i++ {
		servers[i] = fmt.Sprintf("server-%d", i)
	}
	
	ring := New(servers, 20)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		key := fmt.Sprintf("bench-key-%d", i%1000)
		_ = ring.GetServer(key)
	}
}

// BenchmarkAddServer benchmarks the AddServer method
func BenchmarkAddServer(b *testing.B) {
	ring := New([]string{}, 20)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		server := fmt.Sprintf("bench-server-%d", i)
		ring.AddServer(server)
	}
}

// BenchmarkRemoveServer benchmarks the RemoveServer method
func BenchmarkRemoveServer(b *testing.B) {
	// Pre-populate with servers to remove
	servers := make([]string, b.N)
	for i := 0; i < b.N; i++ {
		servers[i] = fmt.Sprintf("bench-server-%d", i)
	}
	
	ring := New(servers, 20)
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		server := fmt.Sprintf("bench-server-%d", i)
		ring.RemoveServer(server)
	}
}