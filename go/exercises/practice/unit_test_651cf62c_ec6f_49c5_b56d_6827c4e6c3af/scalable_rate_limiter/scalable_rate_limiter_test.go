package scalable_rate_limiter

import (
	"sync"
	"testing"
	"time"
)

func TestBasicAllowance(t *testing.T) {
	limit := 3
	window := 100 * time.Millisecond
	rl := NewRateLimiter(limit, window)
	clientID := "client1"
	endpoint := "api1"

	// Allow exactly 'limit' requests
	for i := 0; i < limit; i++ {
		if allowed := rl.AllowRequest(clientID, endpoint); !allowed {
			t.Errorf("Expected request %d to be allowed", i+1)
		}
	}

	// Next request should be rejected
	if allowed := rl.AllowRequest(clientID, endpoint); allowed {
		t.Error("Expected request to be rejected after exceeding the limit")
	}
}

func TestWindowReset(t *testing.T) {
	limit := 2
	window := 200 * time.Millisecond
	rl := NewRateLimiter(limit, window)
	clientID := "client_window"
	endpoint := "api_window"

	// Exhaust the limit
	for i := 0; i < limit; i++ {
		if !rl.AllowRequest(clientID, endpoint) {
			t.Errorf("Expected request %d to be allowed", i+1)
		}
	}
	if rl.AllowRequest(clientID, endpoint) {
		t.Error("Expected request to be rejected once limit is reached")
	}

	// Wait for the window to reset
	time.Sleep(window + 50*time.Millisecond)
	if !rl.AllowRequest(clientID, endpoint) {
		t.Error("Expected request to be allowed after window reset")
	}
}

func TestMultipleClients(t *testing.T) {
	limit := 2
	window := 300 * time.Millisecond
	rl := NewRateLimiter(limit, window)
	clientIDs := []string{"clientA", "clientB", "clientC"}
	endpoint := "api_multi"

	for _, client := range clientIDs {
		for i := 0; i < limit; i++ {
			if !rl.AllowRequest(client, endpoint) {
				t.Errorf("Expected request %d for client %s to be allowed", i+1, client)
			}
		}
		if rl.AllowRequest(client, endpoint) {
			t.Errorf("Expected further request for client %s to be rejected after limit exceeded", client)
		}
	}
}

func TestConcurrency(t *testing.T) {
	limit := 100
	window := 200 * time.Millisecond
	rl := NewRateLimiter(limit, window)
	clientID := "concurrentClient"
	endpoint := "api_concurrent"

	var wg sync.WaitGroup
	var mu sync.Mutex
	allowedCount := 0

	totalRequests := 500
	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if rl.AllowRequest(clientID, endpoint) {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	if allowedCount != limit {
		t.Errorf("Expected %d allowed requests in concurrent scenario but got %d", limit, allowedCount)
	}
}

func TestEndpointSpecificLimits(t *testing.T) {
	// In this test, we simulate different endpoints being assigned different limits.
	// Assume that the implementation of NewRateLimiter uses a default global limit,
	// and the AllowRequest method interprets the endpoint to possibly override the limit.
	// For testing purposes, we call AllowRequest with different endpoints, assuming the
	// implementation handles these cases appropriately.
	globalLimit := 5
	window := 300 * time.Millisecond
	rl := NewRateLimiter(globalLimit, window)
	clientID := "client_endpoint"

	// Test for endpoint "api_free" with limit 5
	endpointFree := "api_free"
	for i := 0; i < 5; i++ {
		if !rl.AllowRequest(clientID, endpointFree) {
			t.Errorf("Expected request %d for endpoint %s to be allowed", i+1, endpointFree)
		}
	}
	if rl.AllowRequest(clientID, endpointFree) {
		t.Errorf("Expected request for endpoint %s to be rejected after limit is exceeded", endpointFree)
	}

	// Test for endpoint "api_premium" with assumed higher limit (e.g., 10)
	endpointPremium := "api_premium"
	// For simulation, allow 10 requests
	for i := 0; i < 10; i++ {
		if !rl.AllowRequest(clientID, endpointPremium) {
			t.Errorf("Expected request %d for endpoint %s to be allowed", i+1, endpointPremium)
		}
	}
	if rl.AllowRequest(clientID, endpointPremium) {
		t.Errorf("Expected request for endpoint %s to be rejected after limit is exceeded", endpointPremium)
	}
}