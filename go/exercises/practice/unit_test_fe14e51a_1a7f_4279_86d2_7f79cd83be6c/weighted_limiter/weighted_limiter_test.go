package weighted_limiter

import (
	"sync"
	"testing"
	"time"
)

func TestNewRateLimiter(t *testing.T) {
	tests := []struct {
		name          string
		tiers         []BucketTier
		expectedError bool
	}{
		{
			name: "valid configuration",
			tiers: []BucketTier{
				{Capacity: 100, RefillRate: 10},
				{Capacity: 1000, RefillRate: 5},
			},
			expectedError: false,
		},
		{
			name:          "empty tiers",
			tiers:        []BucketTier{},
			expectedError: true,
		},
		{
			name: "invalid capacity",
			tiers: []BucketTier{
				{Capacity: 0, RefillRate: 10},
			},
			expectedError: true,
		},
		{
			name: "invalid refill rate",
			tiers: []BucketTier{
				{Capacity: 100, RefillRate: 0},
			},
			expectedError: true,
		},
		{
			name: "too many tiers",
			tiers: make([]BucketTier, 11),
			expectedError: true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			_, err := NewRateLimiter(tt.tiers)
			if (err != nil) != tt.expectedError {
				t.Errorf("NewRateLimiter() error = %v, expectedError %v", err, tt.expectedError)
			}
		})
	}
}

func TestAllowRequest(t *testing.T) {
	limiter, err := NewRateLimiter([]BucketTier{
		{Capacity: 100, RefillRate: 10},
		{Capacity: 1000, RefillRate: 5},
	})
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	tests := []struct {
		name        string
		clientID    string
		weight      int
		shouldAllow bool
	}{
		{
			name:        "valid request within limits",
			clientID:    "client1",
			weight:      50,
			shouldAllow: true,
		},
		{
			name:        "request exceeding first tier",
			clientID:    "client1",
			weight:      80,
			shouldAllow: true,
		},
		{
			name:        "request exceeding all tiers",
			clientID:    "client1",
			weight:      2000,
			shouldAllow: false,
		},
		{
			name:        "invalid weight",
			clientID:    "client1",
			weight:      0,
			shouldAllow: false,
		},
		{
			name:        "empty client ID",
			clientID:    "",
			weight:      10,
			shouldAllow: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			allowed := limiter.AllowRequest(tt.clientID, tt.weight)
			if allowed != tt.shouldAllow {
				t.Errorf("AllowRequest() = %v, want %v", allowed, tt.shouldAllow)
			}
		})
	}
}

func TestConcurrentRequests(t *testing.T) {
	limiter, err := NewRateLimiter([]BucketTier{
		{Capacity: 100, RefillRate: 10},
		{Capacity: 1000, RefillRate: 5},
	})
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	const (
		numGoroutines = 100
		numRequests   = 1000
	)

	var wg sync.WaitGroup
	results := make(chan bool, numGoroutines*numRequests)

	// Launch concurrent requests
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(clientID string) {
			defer wg.Done()
			for j := 0; j < numRequests; j++ {
				results <- limiter.AllowRequest(clientID, 1)
			}
		}("client" + string(rune('A'+i)))
	}

	// Wait for all goroutines to complete
	wg.Wait()
	close(results)

	// Count allowed vs denied requests
	allowed := 0
	denied := 0
	for result := range results {
		if result {
			allowed++
		} else {
			denied++
		}
	}

	// Verify that the total number of requests matches expected
	total := allowed + denied
	if total != numGoroutines*numRequests {
		t.Errorf("Got %d total requests, want %d", total, numGoroutines*numRequests)
	}
}

func TestBucketRefill(t *testing.T) {
	limiter, err := NewRateLimiter([]BucketTier{
		{Capacity: 10, RefillRate: 10}, // Refills 10 per second
	})
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}

	// Consume all capacity
	clientID := "test_client"
	if !limiter.AllowRequest(clientID, 10) {
		t.Fatal("Initial request should be allowed")
	}

	// Immediate request should fail
	if limiter.AllowRequest(clientID, 1) {
		t.Error("Request should be denied immediately after consuming all capacity")
	}

	// Wait for refill
	time.Sleep(1100 * time.Millisecond)

	// Should be able to consume again
	if !limiter.AllowRequest(clientID, 10) {
		t.Error("Request should be allowed after refill")
	}
}

func BenchmarkRateLimiter(b *testing.B) {
	limiter, err := NewRateLimiter([]BucketTier{
		{Capacity: 1000, RefillRate: 100},
		{Capacity: 10000, RefillRate: 50},
	})
	if err != nil {
		b.Fatalf("Failed to create rate limiter: %v", err)
	}

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			limiter.AllowRequest("benchmark_client", 1)
		}
	})
}