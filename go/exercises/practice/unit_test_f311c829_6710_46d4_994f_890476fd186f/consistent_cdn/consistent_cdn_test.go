package consistentcdn

import (
	"fmt"
	"sync"
	"testing"
)

func TestBasicOperations(t *testing.T) {
	cdn := NewCDN(1) // replication factor k=1

	// Add servers
	servers := []string{"server1", "server2", "server3", "server4"}
	for _, server := range servers {
		cdn.AddServer(server)
	}

	// Test basic key distribution
	key := "test_content_1"
	server := cdn.GetServerForKey(key)
	if server == "" {
		t.Error("Expected a server to be assigned for key")
	}

	// Test consistency
	server2 := cdn.GetServerForKey(key)
	if server != server2 {
		t.Error("Same key should map to same server")
	}
}

func TestServerRemoval(t *testing.T) {
	cdn := NewCDN(1)
	servers := []string{"server1", "server2", "server3"}
	for _, server := range servers {
		cdn.AddServer(server)
	}

	key := "test_content_1"
	originalServer := cdn.GetServerForKey(key)

	// Remove a different server
	for _, server := range servers {
		if server != originalServer {
			cdn.RemoveServer(server)
			break
		}
	}

	// Key should still map to the same server
	newServer := cdn.GetServerForKey(key)
	if originalServer != newServer {
		t.Error("Key mapping changed after removing unrelated server")
	}

	// Remove the server handling our key
	cdn.RemoveServer(originalServer)
	finalServer := cdn.GetServerForKey(key)
	if finalServer == originalServer {
		t.Error("Key still mapping to removed server")
	}
}

func TestReplication(t *testing.T) {
	k := 3
	cdn := NewCDN(k)
	servers := []string{"server1", "server2", "server3", "server4", "server5"}
	for _, server := range servers {
		cdn.AddServer(server)
	}

	key := "test_content_1"
	replicas := cdn.GetReplicasForKey(key)

	if len(replicas) != k {
		t.Errorf("Expected %d replicas, got %d", k, len(replicas))
	}

	// Check for uniqueness
	seen := make(map[string]bool)
	for _, server := range replicas {
		if seen[server] {
			t.Error("Duplicate server in replicas")
		}
		seen[server] = true
	}
}

func TestServerAvailability(t *testing.T) {
	cdn := NewCDN(2)
	servers := []string{"server1", "server2", "server3"}
	for _, server := range servers {
		cdn.AddServer(server)
	}

	key := "test_content_1"
	originalServer := cdn.GetServerForKey(key)
	cdn.SetServerAvailability(originalServer, false)

	newServer := cdn.GetServerForKey(key)
	if newServer == originalServer {
		t.Error("Key still mapping to unavailable server")
	}

	// Test replicas
	replicas := cdn.GetReplicasForKey(key)
	for _, server := range replicas {
		if server == originalServer {
			t.Error("Unavailable server included in replicas")
		}
	}
}

func TestConcurrency(t *testing.T) {
	cdn := NewCDN(2)
	servers := []string{"server1", "server2", "server3", "server4", "server5"}
	for _, server := range servers {
		cdn.AddServer(server)
	}

	var wg sync.WaitGroup
	concurrentOps := 100

	// Concurrent server operations
	wg.Add(concurrentOps * 3) // add, remove, availability changes
	for i := 0; i < concurrentOps; i++ {
		go func(i int) {
			defer wg.Done()
			cdn.AddServer(fmt.Sprintf("new_server_%d", i))
		}(i)
		go func(i int) {
			defer wg.Done()
			cdn.RemoveServer("server1") // It's ok if this fails sometimes
		}(i)
		go func(i int) {
			defer wg.Done()
			cdn.SetServerAvailability("server2", i%2 == 0)
		}(i)
	}

	// Concurrent key lookups
	wg.Add(concurrentOps)
	for i := 0; i < concurrentOps; i++ {
		go func(i int) {
			defer wg.Done()
			key := fmt.Sprintf("test_key_%d", i)
			_ = cdn.GetServerForKey(key)
			_ = cdn.GetReplicasForKey(key)
		}(i)
	}

	wg.Wait()
}

func TestLoadDistribution(t *testing.T) {
	cdn := NewCDN(1)
	servers := []string{"server1", "server2", "server3", "server4"}
	for _, server := range servers {
		cdn.AddServer(server)
	}

	// Generate many keys and check distribution
	keyCount := 10000
	distribution := make(map[string]int)
	for i := 0; i < keyCount; i++ {
		key := fmt.Sprintf("test_key_%d", i)
		server := cdn.GetServerForKey(key)
		distribution[server]++
	}

	// Check if distribution is relatively even
	average := keyCount / len(servers)
	threshold := float64(average) * 0.3 // Allow 30% deviation

	for server, count := range distribution {
		diff := float64(abs(count-average))
		if diff > threshold {
			t.Errorf("Uneven distribution for server %s: got %d keys, expected close to %d (threshold: %.2f)",
				server, count, average, threshold)
		}
	}
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}