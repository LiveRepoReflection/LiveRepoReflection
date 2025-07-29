package ratelimits

import (
	"sync"
	"testing"
	"time"
)

func TestRateLimiter(t *testing.T) {
	tests := []struct {
		name           string
		userID         string
		userTier       int
		requests       int
		interval       time.Duration
		expectedAllow  int
		expectedDeny   int
		concurrent     bool
		sleepDuration  time.Duration
	}{
		{
			name:           "Basic rate limiting",
			userID:         "user1",
			userTier:       1,
			requests:       10,
			interval:       time.Second,
			expectedAllow:  5,  // Tier 1 allows 5 requests per second
			expectedDeny:   5,
			concurrent:     false,
			sleepDuration:  0,
		},
		{
			name:           "Higher tier user",
			userID:         "user2",
			userTier:       2,
			requests:       20,
			interval:       time.Second,
			expectedAllow:  10, // Tier 2 allows 10 requests per second
			expectedDeny:   10,
			concurrent:     false,
			sleepDuration:  0,
		},
		{
			name:           "Concurrent requests",
			userID:         "user3",
			userTier:       1,
			requests:       100,
			interval:       time.Second,
			expectedAllow:  5,  // Should still only allow 5 even with concurrent requests
			expectedDeny:   95,
			concurrent:     true,
			sleepDuration:  0,
		},
		{
			name:           "Grace period test",
			userID:         "user4",
			userTier:       1,
			requests:       10,
			interval:       time.Second,
			expectedAllow:  5,
			expectedDeny:   5,
			concurrent:     false,
			sleepDuration:  time.Second, // Wait for grace period
		},
		{
			name:           "Very high tier user",
			userID:         "user5",
			userTier:       5,
			requests:       50,
			interval:       time.Second,
			expectedAllow:  25, // Tier 5 allows 25 requests per second
			expectedDeny:   25,
			concurrent:     false,
			sleepDuration:  0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			limiter := NewRateLimiter()
			
			var allowed, denied int
			var wg sync.WaitGroup
			var mu sync.Mutex

			makeRequest := func() {
				result := limiter.AllowRequest(tt.userID, time.Now().UnixNano(), tt.userTier)
				mu.Lock()
				if result {
					allowed++
				} else {
					denied++
				}
				mu.Unlock()
				wg.Done()
			}

			for i := 0; i < tt.requests; i++ {
				wg.Add(1)
				if tt.concurrent {
					go makeRequest()
				} else {
					makeRequest()
				}

				if tt.sleepDuration > 0 && i == tt.requests/2 {
					time.Sleep(tt.sleepDuration)
				}
			}

			wg.Wait()

			if allowed != tt.expectedAllow {
				t.Errorf("Expected %d allowed requests, got %d", tt.expectedAllow, allowed)
			}
			if denied != tt.expectedDeny {
				t.Errorf("Expected %d denied requests, got %d", tt.expectedDeny, denied)
			}
		})
	}
}

func TestRateLimiterEdgeCases(t *testing.T) {
	tests := []struct {
		name          string
		userID        string
		timestamp     int64
		userTier      int
		expectAllowed bool
	}{
		{
			name:          "Empty user ID",
			userID:        "",
			timestamp:     time.Now().UnixNano(),
			userTier:      1,
			expectAllowed: false,
		},
		{
			name:          "Invalid tier",
			userID:        "user1",
			timestamp:     time.Now().UnixNano(),
			userTier:      -1,
			expectAllowed: false,
		},
		{
			name:          "Past timestamp",
			userID:        "user1",
			timestamp:     time.Now().Add(-24 * time.Hour).UnixNano(),
			userTier:      1,
			expectAllowed: false,
		},
		{
			name:          "Future timestamp",
			userID:        "user1",
			timestamp:     time.Now().Add(24 * time.Hour).UnixNano(),
			userTier:      1,
			expectAllowed: false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			limiter := NewRateLimiter()
			result := limiter.AllowRequest(tt.userID, tt.timestamp, tt.userTier)
			if result != tt.expectAllowed {
				t.Errorf("Expected AllowRequest to return %v, got %v", tt.expectAllowed, result)
			}
		})
	}
}

func BenchmarkRateLimiter(b *testing.B) {
	limiter := NewRateLimiter()
	userID := "benchmark-user"
	timestamp := time.Now().UnixNano()
	userTier := 1

	b.ResetTimer()
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			limiter.AllowRequest(userID, timestamp, userTier)
		}
	})
}