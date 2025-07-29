package ratelimit

import (
	"context"
	"fmt"
	"math/rand"
	"sync"
	"testing"
	"time"
)

func TestBasicRateLimiting(t *testing.T) {
	limiter, err := NewDistributedRateLimiter([]string{"localhost:5001"}, 1)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	clientID := "test-client"
	allowed, err := limiter.Allow(context.Background(), clientID)
	if err != nil || !allowed {
		t.Errorf("First request should be allowed")
	}

	allowed, err = limiter.Allow(context.Background(), clientID)
	if err != nil || allowed {
		t.Errorf("Second request within 1s should be denied")
	}
}

func TestConcurrentRequests(t *testing.T) {
	limiter, err := NewDistributedRateLimiter([]string{"localhost:5001", "localhost:5002"}, 2)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	var wg sync.WaitGroup
	clientID := "concurrent-client"
	allowedCount := 0
	deniedCount := 0
	var mu sync.Mutex

	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			allowed, err := limiter.Allow(context.Background(), clientID)
			if err != nil {
				t.Errorf("Unexpected error: %v", err)
				return
			}
			mu.Lock()
			if allowed {
				allowedCount++
			} else {
				deniedCount++
			}
			mu.Unlock()
		}()
	}

	wg.Wait()

	if allowedCount != 2 {
		t.Errorf("Expected exactly 2 requests to be allowed, got %d", allowedCount)
	}
	if deniedCount != 8 {
		t.Errorf("Expected exactly 8 requests to be denied, got %d", deniedCount)
	}
}

func TestNodeFailure(t *testing.T) {
	nodes := []string{
		"localhost:5001",
		"localhost:5002",
		"localhost:5003",
		"localhost:5004",
		"localhost:5005",
	}
	
	limiter, err := NewDistributedRateLimiter(nodes, 3)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	// Simulate node failures
	limiter.SimulateNodeFailure("localhost:5001")
	limiter.SimulateNodeFailure("localhost:5002")

	clientID := "failure-test-client"
	allowed, err := limiter.Allow(context.Background(), clientID)
	if err != nil {
		t.Errorf("Expected request to succeed with reduced quorum, got error: %v", err)
	}
	if !allowed {
		t.Error("Request should be allowed with reduced quorum")
	}
}

func TestAdaptiveQuorum(t *testing.T) {
	nodes := []string{
		"localhost:5001",
		"localhost:5002",
		"localhost:5003",
		"localhost:5004",
	}
	
	limiter, err := NewDistributedRateLimiter(nodes, 2)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	tests := []struct {
		name          string
		failureCount  int
		expectQuorum  int
		expectSuccess bool
	}{
		{"All nodes healthy", 0, 3, true},
		{"One node failed", 1, 3, true},
		{"Most nodes failed", 3, 1, true},
		{"All nodes failed", 4, 0, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			// Reset all nodes
			limiter.ResetNodes()
			
			// Simulate failures
			for i := 0; i < tt.failureCount; i++ {
				limiter.SimulateNodeFailure(nodes[i])
			}

			clientID := fmt.Sprintf("adaptive-test-%d", rand.Int())
			allowed, err := limiter.Allow(context.Background(), clientID)
			
			if tt.expectSuccess {
				if err != nil {
					t.Errorf("Expected success, got error: %v", err)
				}
				if !allowed {
					t.Error("Expected request to be allowed")
				}
			} else {
				if err == nil {
					t.Error("Expected error, got nil")
				}
			}
		})
	}
}

func TestEventualConsistency(t *testing.T) {
	nodes := []string{
		"localhost:5001",
		"localhost:5002",
		"localhost:5003",
	}
	
	limiter, err := NewDistributedRateLimiter(nodes, 5)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	clientID := "consistency-test"
	
	// Make requests with network delays
	var wg sync.WaitGroup
	for i := 0; i < 3; i++ {
		wg.Add(1)
		go func(nodeIdx int) {
			defer wg.Done()
			time.Sleep(time.Duration(rand.Intn(100)) * time.Millisecond)
			_, _ = limiter.Allow(context.Background(), clientID)
		}(i)
	}

	wg.Wait()
	time.Sleep(2 * time.Second) // Allow time for convergence

	// Verify consistency across nodes
	counts := limiter.GetNodeCounters(clientID)
	firstCount := counts[0]
	for i := 1; i < len(counts); i++ {
		if counts[i] != firstCount {
			t.Errorf("Inconsistent counts across nodes: node 0: %d, node %d: %d", 
				firstCount, i, counts[i])
		}
	}
}

func TestSlidingWindow(t *testing.T) {
	limiter, err := NewDistributedRateLimiter([]string{"localhost:5001"}, 1)
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	clientID := "sliding-window-test"
	
	// First request should succeed
	allowed, err := limiter.Allow(context.Background(), clientID)
	if err != nil || !allowed {
		t.Error("First request should be allowed")
	}

	// Request immediately after should fail
	allowed, err = limiter.Allow(context.Background(), clientID)
	if err != nil || allowed {
		t.Error("Immediate second request should be denied")
	}

	// Wait for slightly less than window
	time.Sleep(900 * time.Millisecond)
	allowed, err = limiter.Allow(context.Background(), clientID)
	if err != nil || allowed {
		t.Error("Request before window expires should be denied")
	}

	// Wait for window to fully expire
	time.Sleep(200 * time.Millisecond)
	allowed, err = limiter.Allow(context.Background(), clientID)
	if err != nil || !allowed {
		t.Error("Request after window expires should be allowed")
	}
}

func BenchmarkRateLimiter(b *testing.B) {
	limiter, err := NewDistributedRateLimiter([]string{
		"localhost:5001",
		"localhost:5002",
		"localhost:5003",
	}, 1000)
	if err != nil {
		b.Fatalf("Failed to create rate limiter: %v", err)
	}

	ctx := context.Background()
	clientIDs := make([]string, 100)
	for i := range clientIDs {
		clientIDs[i] = fmt.Sprintf("bench-client-%d", i)
	}

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			clientID := clientIDs[rand.Intn(len(clientIDs))]
			_, _ = limiter.Allow(ctx, clientID)
		}
	})
}