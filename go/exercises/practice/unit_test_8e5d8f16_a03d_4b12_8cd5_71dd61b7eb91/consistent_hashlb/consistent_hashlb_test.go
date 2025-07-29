package consistent_hashlb

import (
	"fmt"
	"sync"
	"testing"
)

type mockServer struct {
	address string
	load    int
}

func TestNewLoadBalancer(t *testing.T) {
	tests := []struct {
		name           string
		ringSize       uint64
		virtualNodes   int
		expectedError  bool
	}{
		{"valid configuration", 1024, 10, false},
		{"zero ring size", 0, 10, true},
		{"negative virtual nodes", 1024, -1, true},
		{"zero virtual nodes", 1024, 0, true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			lb, err := NewLoadBalancer(tt.ringSize, tt.virtualNodes)
			if tt.expectedError {
				if err == nil {
					t.Errorf("expected error but got none")
				}
			} else {
				if err != nil {
					t.Errorf("unexpected error: %v", err)
				}
				if lb == nil {
					t.Error("expected non-nil load balancer")
				}
			}
		})
	}
}

func TestAddServer(t *testing.T) {
	lb, err := NewLoadBalancer(1024, 10)
	if err != nil {
		t.Fatalf("failed to create load balancer: %v", err)
	}

	tests := []struct {
		name          string
		serverAddress string
		expectedError bool
	}{
		{"valid server", "server1:8080", false},
		{"empty address", "", true},
		{"duplicate server", "server1:8080", true},
		{"invalid address format", "invalid:addr:8080", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := lb.AddServer(tt.serverAddress)
			if tt.expectedError {
				if err == nil {
					t.Errorf("expected error but got none")
				}
			} else {
				if err != nil {
					t.Errorf("unexpected error: %v", err)
				}
			}
		})
	}
}

func TestRemoveServer(t *testing.T) {
	lb, _ := NewLoadBalancer(1024, 10)
	serverAddr := "server1:8080"
	
	// Add a server first
	err := lb.AddServer(serverAddr)
	if err != nil {
		t.Fatalf("failed to add server: %v", err)
	}

	tests := []struct {
		name          string
		serverAddress string
		expectedError bool
	}{
		{"existing server", serverAddr, false},
		{"non-existing server", "server2:8080", true},
		{"empty address", "", true},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := lb.RemoveServer(tt.serverAddress)
			if tt.expectedError {
				if err == nil {
					t.Errorf("expected error but got none")
				}
			} else {
				if err != nil {
					t.Errorf("unexpected error: %v", err)
				}
			}
		})
	}
}

func TestGetServer(t *testing.T) {
	lb, _ := NewLoadBalancer(1024, 10)
	servers := []string{
		"server1:8080",
		"server2:8080",
		"server3:8080",
	}

	// Add servers
	for _, server := range servers {
		err := lb.AddServer(server)
		if err != nil {
			t.Fatalf("failed to add server %s: %v", server, err)
		}
	}

	// Test consistent hashing property
	keys := []string{"key1", "key2", "key3", "key4"}
	results := make(map[string]string)

	// First round of getting servers
	for _, key := range keys {
		server, err := lb.GetServer(key)
		if err != nil {
			t.Fatalf("failed to get server for key %s: %v", key, err)
		}
		results[key] = server
	}

	// Remove a server
	err := lb.RemoveServer(servers[1])
	if err != nil {
		t.Fatalf("failed to remove server: %v", err)
	}

	// Second round - check consistency
	for _, key := range keys {
		server, err := lb.GetServer(key)
		if err != nil {
			t.Fatalf("failed to get server for key %s after removal: %v", key, err)
		}
		
		// If the key was previously mapped to the removed server,
		// it should now map to a different one
		if results[key] == servers[1] {
			if server == servers[1] {
				t.Errorf("key %s still maps to removed server %s", key, server)
			}
		} else {
			// If the key wasn't mapped to the removed server,
			// it should still map to the same server
			if server != results[key] {
				t.Errorf("inconsistent hashing: key %s mapped to %s, now maps to %s",
					key, results[key], server)
			}
		}
	}
}

func TestConcurrency(t *testing.T) {
	lb, _ := NewLoadBalancer(1024, 10)
	var wg sync.WaitGroup
	
	// Concurrent server additions
	for i := 0; i < 100; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			serverAddr := fmt.Sprintf("server%d:8080", id)
			_ = lb.AddServer(serverAddr)
		}(i)
	}

	// Concurrent requests
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			key := fmt.Sprintf("key%d", id)
			_, _ = lb.GetServer(key)
		}(i)
	}

	// Concurrent server removals
	for i := 0; i < 50; i++ {
		wg.Add(1)
		go func(id int) {
			defer wg.Done()
			serverAddr := fmt.Sprintf("server%d:8080", id)
			_ = lb.RemoveServer(serverAddr)
		}(i)
	}

	wg.Wait()
}

func TestLoadDistribution(t *testing.T) {
	lb, _ := NewLoadBalancer(1024, 10)
	servers := []string{
		"server1:8080",
		"server2:8080",
		"server3:8080",
	}

	for _, server := range servers {
		err := lb.AddServer(server)
		if err != nil {
			t.Fatalf("failed to add server %s: %v", server, err)
		}
	}

	distribution := make(map[string]int)
	totalRequests := 10000

	for i := 0; i < totalRequests; i++ {
		key := fmt.Sprintf("key%d", i)
		server, err := lb.GetServer(key)
		if err != nil {
			t.Fatalf("failed to get server for key %s: %v", key, err)
		}
		distribution[server]++
	}

	// Check if load is reasonably distributed
	expectedAvg := totalRequests / len(servers)
	tolerance := float64(expectedAvg) * 0.2 // 20% tolerance

	for server, count := range distribution {
		diff := float64(abs(count - expectedAvg))
		if diff > tolerance {
			t.Errorf("uneven distribution for %s: got %d requests, expected %d ±%.0f",
				server, count, expectedAvg, tolerance)
		}
	}
}

func abs(x int) int {
	if x < 0 {
		return -x
	}
	return x
}