package ratelimiter

import (
	"sync"
	"testing"
	"time"
)

func TestRateLimiterBasicFunctionality(t *testing.T) {
	tests := []struct {
		name           string
		clientID       string
		requestLimit   int
		timeWindowSec  int
		requestCount   int
		expectedAllow  int
		expectedReject int
	}{
		{
			name:           "Basic rate limit not exceeded",
			clientID:       "client1",
			requestLimit:   5,
			timeWindowSec:  1,
			requestCount:   3,
			expectedAllow:  3,
			expectedReject: 0,
		},
		{
			name:           "Basic rate limit exactly at limit",
			clientID:       "client2",
			requestLimit:   5,
			timeWindowSec:  1,
			requestCount:   5,
			expectedAllow:  5,
			expectedReject: 0,
		},
		{
			name:           "Basic rate limit exceeded",
			clientID:       "client3",
			requestLimit:   5,
			timeWindowSec:  1,
			requestCount:   7,
			expectedAllow:  5,
			expectedReject: 2,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			limiter := NewRateLimiter()
			err := limiter.SetLimit(tt.clientID, tt.requestLimit, tt.timeWindowSec)
			if err != nil {
				t.Fatalf("Failed to set limit: %v", err)
			}

			allowed := 0
			rejected := 0

			for i := 0; i < tt.requestCount; i++ {
				if limiter.Allow(tt.clientID) {
					allowed++
				} else {
					rejected++
				}
			}

			if allowed != tt.expectedAllow {
				t.Errorf("Expected %d allowed requests, got %d", tt.expectedAllow, allowed)
			}
			if rejected != tt.expectedReject {
				t.Errorf("Expected %d rejected requests, got %d", tt.expectedReject, rejected)
			}
		})
	}
}

func TestRateLimiterConcurrency(t *testing.T) {
	limiter := NewRateLimiter()
	clientID := "concurrent_client"
	requestLimit := 1000
	timeWindowSec := 1

	err := limiter.SetLimit(clientID, requestLimit, timeWindowSec)
	if err != nil {
		t.Fatalf("Failed to set limit: %v", err)
	}

	var wg sync.WaitGroup
	numGoroutines := 100
	requestsPerGoroutine := 20

	allowedCount := int32(0)
	rejectedCount := int32(0)

	var mu sync.Mutex

	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < requestsPerGoroutine; j++ {
				if limiter.Allow(clientID) {
					mu.Lock()
					allowedCount++
					mu.Unlock()
				} else {
					mu.Lock()
					rejectedCount++
					mu.Unlock()
				}
			}
		}()
	}

	wg.Wait()

	totalRequests := numGoroutines * requestsPerGoroutine
	if int(allowedCount) > requestLimit {
		t.Errorf("Allowed requests (%d) exceeded the limit (%d)", allowedCount, requestLimit)
	}
	if int(allowedCount+rejectedCount) != totalRequests {
		t.Errorf("Total requests processed (%d) != total requests sent (%d)", allowedCount+rejectedCount, totalRequests)
	}
}

func TestRateLimiterTimeWindow(t *testing.T) {
	limiter := NewRateLimiter()
	clientID := "time_window_client"
	requestLimit := 5
	timeWindowSec := 1

	err := limiter.SetLimit(clientID, requestLimit, timeWindowSec)
	if err != nil {
		t.Fatalf("Failed to set limit: %v", err)
	}

	// Use all requests
	for i := 0; i < requestLimit; i++ {
		if !limiter.Allow(clientID) {
			t.Errorf("Request %d should have been allowed", i+1)
		}
	}

	// Next request should be rejected
	if limiter.Allow(clientID) {
		t.Error("Request should have been rejected")
	}

	// Wait for time window to pass
	time.Sleep(time.Duration(timeWindowSec) * time.Second)

	// Should be allowed again
	if !limiter.Allow(clientID) {
		t.Error("Request should have been allowed after time window reset")
	}
}

func TestRateLimiterDynamicUpdates(t *testing.T) {
	limiter := NewRateLimiter()
	clientID := "dynamic_client"
	initialLimit := 5
	timeWindowSec := 1

	// Set initial limit
	err := limiter.SetLimit(clientID, initialLimit, timeWindowSec)
	if err != nil {
		t.Fatalf("Failed to set initial limit: %v", err)
	}

	// Use some requests
	for i := 0; i < 3; i++ {
		if !limiter.Allow(clientID) {
			t.Errorf("Request %d should have been allowed", i+1)
		}
	}

	// Update limit to a lower value
	newLimit := 2
	err = limiter.SetLimit(clientID, newLimit, timeWindowSec)
	if err != nil {
		t.Fatalf("Failed to update limit: %v", err)
	}

	// Should be rejected as we've already used more than the new limit
	if limiter.Allow(clientID) {
		t.Error("Request should have been rejected after limit update")
	}

	// Wait for time window to pass
	time.Sleep(time.Duration(timeWindowSec) * time.Second)

	// Should work with new limit
	for i := 0; i < newLimit; i++ {
		if !limiter.Allow(clientID) {
			t.Errorf("Request %d should have been allowed with new limit", i+1)
		}
	}
	if limiter.Allow(clientID) {
		t.Error("Request should have been rejected with new limit")
	}
}

func BenchmarkRateLimiter(b *testing.B) {
	limiter := NewRateLimiter()
	clientID := "bench_client"
	requestLimit := 1000000
	timeWindowSec := 1

	err := limiter.SetLimit(clientID, requestLimit, timeWindowSec)
	if err != nil {
		b.Fatalf("Failed to set limit: %v", err)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		limiter.Allow(clientID)
	}
}