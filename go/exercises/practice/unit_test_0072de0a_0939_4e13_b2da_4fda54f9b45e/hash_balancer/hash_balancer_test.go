package hash_balancer

import (
	"math/rand"
	"strconv"
	"testing"
	"time"
)

// helper function to generate a list of keys
func generateKeys(n int) []string {
	keys := make([]string, n)
	for i := 0; i < n; i++ {
		keys[i] = "key_" + strconv.Itoa(i)
	}
	return keys
}

func TestSingleServer(t *testing.T) {
	// Create load balancer with a certain replica count
	lb := NewConsistentHashLoadBalancer(100)
	// Add a single server
	serverID := "server-1"
	lb.AddServer(serverID)

	// Test that for a range of keys, GetServerForKey always returns the same server
	keys := generateKeys(50)
	for _, key := range keys {
		got := lb.GetServerForKey(key)
		if got != serverID {
			t.Errorf("GetServerForKey(%q) = %q; want %q", key, got, serverID)
		}
	}
}

func TestMultipleServersDistribution(t *testing.T) {
	lb := NewConsistentHashLoadBalancer(100)
	servers := []string{"server-1", "server-2", "server-3", "server-4", "server-5"}
	for _, server := range servers {
		lb.AddServer(server)
	}

	keys := generateKeys(1000)
	serverSet := make(map[string]bool)
	for _, key := range keys {
		s := lb.GetServerForKey(key)
		found := false
		for _, server := range servers {
			if s == server {
				found = true
				break
			}
		}
		if !found {
			t.Errorf("GetServerForKey(%q) returned unexpected server %q", key, s)
		}
		serverSet[s] = true
	}

	// Check that all servers have been hit at least once (distribution)
	if len(serverSet) < len(servers) {
		t.Errorf("Expected at least %d servers to receive keys; got %d", len(servers), len(serverSet))
	}
}

func TestAddAndRemoveServer(t *testing.T) {
	lb := NewConsistentHashLoadBalancer(100)
	servers := []string{"server-1", "server-2", "server-3"}
	for _, server := range servers {
		lb.AddServer(server)
	}

	// Generate keys and map the initial distribution
	keys := generateKeys(500)
	initialMapping := make(map[string]string)
	for _, key := range keys {
		initialMapping[key] = lb.GetServerForKey(key)
	}

	// Remove one server
	removedServer := "server-2"
	lb.RemoveServer(removedServer)

	// For keys that were mapped to the removed server, check they are remapped to a different server.
	// For others, the mapping might remain the same.
	for _, key := range keys {
		orig := initialMapping[key]
		newMapping := lb.GetServerForKey(key)
		if orig == removedServer {
			if newMapping == removedServer || newMapping == "" {
				t.Errorf("After removal, key %q mapped to removed server %q", key, newMapping)
			}
		}
	}
}

func TestKeyDistribution(t *testing.T) {
	lb := NewConsistentHashLoadBalancer(100)
	servers := []string{"server-1", "server-2", "server-3", "server-4"}
	for _, server := range servers {
		lb.AddServer(server)
	}

	// Simulate assigning keys by repeatedly calling GetServerForKey.
	keys := generateKeys(1000)
	for _, key := range keys {
		// Call GetServerForKey to simulate key assignment.
		_ = lb.GetServerForKey(key)
	}

	// Get distribution and sum the counts.
	distribution := lb.GetKeyDistribution()
	total := 0
	for server, count := range distribution {
		if count < 0 {
			t.Errorf("Invalid count %d for server %q", count, server)
		}
		total += count
	}
	if total != len(keys) {
		t.Errorf("Total keys distributed = %d; want %d", total, len(keys))
	}
}

func TestConsistency(t *testing.T) {
	lb := NewConsistentHashLoadBalancer(100)
	servers := []string{"server-1", "server-2", "server-3"}
	for _, server := range servers {
		lb.AddServer(server)
	}

	keys := generateKeys(200)
	// Check that repeated calls to GetServerForKey return the same server unless topology changes
	for _, key := range keys {
		first := lb.GetServerForKey(key)
		second := lb.GetServerForKey(key)
		if first != second {
			t.Errorf("Inconsistent mapping for key %q: got %q and then %q", key, first, second)
		}
	}

	// After adding a new server, some keys should change, but others may remain the same.
	originalMapping := make(map[string]string)
	for _, key := range keys {
		originalMapping[key] = lb.GetServerForKey(key)
	}
	lb.AddServer("server-4")
	changedCount := 0
	for _, key := range keys {
		if lb.GetServerForKey(key) != originalMapping[key] {
			changedCount++
		}
	}

	// With consistent hashing, adding a server should not remap all keys. We expect only a fraction
	// of keys to change. We simply ensure that not all keys are remapped.
	if changedCount == len(keys) {
		t.Errorf("All keys were remapped after adding a server; expected only a subset to change")
	}
}

func TestStress(t *testing.T) {
	lb := NewConsistentHashLoadBalancer(150)
	// Add a reasonable number of servers
	numServers := 50
	for i := 0; i < numServers; i++ {
		lb.AddServer("server-" + strconv.Itoa(i))
	}

	// Generate a large number of keys
	numKeys := 10000
	keys := generateKeys(numKeys)

	// Randomize keys order to simulate realistic load
	rand.Seed(time.Now().UnixNano())
	rand.Shuffle(len(keys), func(i, j int) {
		keys[i], keys[j] = keys[j], keys[i]
	})

	// Check that every key can be mapped to an existing server
	for _, key := range keys {
		server := lb.GetServerForKey(key)
		if server == "" {
			t.Errorf("Key %q did not return any server", key)
		}
	}
}