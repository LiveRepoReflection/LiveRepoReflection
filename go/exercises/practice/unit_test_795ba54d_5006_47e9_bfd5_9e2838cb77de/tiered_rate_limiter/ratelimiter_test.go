package ratelimiter

import (
	"context"
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestRateLimiter_Basic(t *testing.T) {
	// Create a new rate limiter
	limiter, err := NewRateLimiter(context.Background())
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}
	defer limiter.Close()

	// Test Free tier
	userID := "user1"
	tier := "Free"
	
	// Should allow 5 requests
	for i := 0; i < 5; i++ {
		allowed := limiter.Allow(userID, tier)
		if !allowed {
			t.Errorf("Request %d should be allowed for Free tier", i+1)
		}
	}
	
	// 6th request should be rejected
	allowed := limiter.Allow(userID, tier)
	if allowed {
		t.Errorf("Request 6 should be rejected for Free tier")
	}
}

func TestRateLimiter_AllTiers(t *testing.T) {
	limiter, err := NewRateLimiter(context.Background())
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}
	defer limiter.Close()

	tests := []struct {
		tier     string
		userID   string
		limit    int
		expected bool
	}{
		{"Free", "free_user", 5, true},
		{"Standard", "standard_user", 20, true},
		{"Premium", "premium_user", 100, true},
	}

	for _, tc := range tests {
		t.Run(fmt.Sprintf("Tier_%s", tc.tier), func(t *testing.T) {
			// Allow requests up to the limit
			for i := 0; i < tc.limit; i++ {
				allowed := limiter.Allow(tc.userID, tc.tier)
				if !allowed {
					t.Errorf("Request %d should be allowed for %s tier", i+1, tc.tier)
				}
			}
			
			// Next request should be rejected
			allowed := limiter.Allow(tc.userID, tc.tier)
			if allowed {
				t.Errorf("Request %d should be rejected for %s tier", tc.limit+1, tc.tier)
			}
		})
	}
}

func TestRateLimiter_SlidingWindow(t *testing.T) {
	limiter, err := NewRateLimiter(context.Background())
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}
	defer limiter.Close()

	userID := "sliding_user"
	tier := "Free"
	
	// Use all 5 requests
	for i := 0; i < 5; i++ {
		allowed := limiter.Allow(userID, tier)
		if !allowed {
			t.Errorf("Request %d should be allowed for Free tier", i+1)
		}
	}
	
	// 6th request should be rejected
	allowed := limiter.Allow(userID, tier)
	if allowed {
		t.Errorf("Request 6 should be rejected for Free tier")
	}
	
	// Wait for sliding window to move (61 seconds to ensure we're past the minute)
	t.Log("Waiting for sliding window to move...")
	time.Sleep(61 * time.Second)
	
	// Should be able to make requests again
	for i := 0; i < 5; i++ {
		allowed := limiter.Allow(userID, tier)
		if !allowed {
			t.Errorf("Request %d should be allowed after window reset", i+1)
		}
	}
}

func TestRateLimiter_Concurrent(t *testing.T) {
	if testing.Short() {
		t.Skip("Skipping concurrent test in short mode")
	}

	limiter, err := NewRateLimiter(context.Background())
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}
	defer limiter.Close()

	// Test concurrent access
	const numGoroutines = 100
	const numRequests = 5
	userID := "concurrent_user"
	tier := "Free"
	
	var wg sync.WaitGroup
	var allowedCount int64
	var mu sync.Mutex
	
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			allowed := limiter.Allow(userID, tier)
			if allowed {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
		}(i)
	}
	
	wg.Wait()
	
	if allowedCount > int64(numRequests) {
		t.Errorf("Expected at most %d requests to be allowed, but got %d", numRequests, allowedCount)
	}
}

func TestRateLimiter_DifferentUsers(t *testing.T) {
	limiter, err := NewRateLimiter(context.Background())
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}
	defer limiter.Close()

	// Different users should have separate rate limits
	for i := 0; i < 10; i++ {
		userID := fmt.Sprintf("user%d", i)
		tier := "Free"
		
		// Each user should be allowed 5 requests
		for j := 0; j < 5; j++ {
			allowed := limiter.Allow(userID, tier)
			if !allowed {
				t.Errorf("Request %d should be allowed for user %s", j+1, userID)
			}
		}
		
		// 6th request should be rejected for each user
		allowed := limiter.Allow(userID, tier)
		if allowed {
			t.Errorf("Request 6 should be rejected for user %s", userID)
		}
	}
}

func TestRateLimiter_InvalidTier(t *testing.T) {
	limiter, err := NewRateLimiter(context.Background())
	if err != nil {
		t.Fatalf("Failed to create rate limiter: %v", err)
	}
	defer limiter.Close()

	// Test with invalid tier
	userID := "invalid_tier_user"
	tier := "InvalidTier"
	
	allowed := limiter.Allow(userID, tier)
	if allowed {
		t.Errorf("Request with invalid tier should be rejected")
	}
}

func BenchmarkRateLimiter(b *testing.B) {
	limiter, err := NewRateLimiter(context.Background())
	if err != nil {
		b.Fatalf("Failed to create rate limiter: %v", err)
	}
	defer limiter.Close()

	// Prepare user IDs
	userIDs := make([]string, 1000)
	for i := range userIDs {
		userIDs[i] = fmt.Sprintf("bench_user_%d", i)
	}

	tiers := []string{"Free", "Standard", "Premium"}
	
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		userID := userIDs[i%len(userIDs)]
		tier := tiers[i%len(tiers)]
		_ = limiter.Allow(userID, tier)
	}
}

// Optional: Mock for distributed environments
type MockDistributedStorage struct {
	data map[string]int
	mu   sync.RWMutex
}

func NewMockDistributedStorage() *MockDistributedStorage {
	return &MockDistributedStorage{
		data: make(map[string]int),
	}
}

func (m *MockDistributedStorage) Increment(key string) (int, error) {
	m.mu.Lock()
	defer m.mu.Unlock()
	m.data[key]++
	return m.data[key], nil
}

func (m *MockDistributedStorage) Get(key string) (int, error) {
	m.mu.RLock()
	defer m.mu.RUnlock()
	return m.data[key], nil
}

func TestRateLimiter_WithMockDistributedStorage(t *testing.T) {
	// This test would connect your rate limiter with a mock distributed storage
	// Implementation depends on your actual rate limiter design
	t.Skip("Implement this test based on your distributed storage implementation")
}