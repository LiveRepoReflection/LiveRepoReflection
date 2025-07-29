package distributed_ratelimit

import (
	"sync"
	"testing"
	"time"
)

func TestAllowRequest_SingleRateLimit(t *testing.T) {
	clientID := "client1"
	rateLimit := RateLimit{
		Requests: 5,
		Window:   time.Second,
	}
	now := time.Now()

	// First 5 requests should be allowed
	for i := 0; i < 5; i++ {
		allowed := AllowRequest(clientID, []RateLimit{rateLimit}, now)
		if !allowed {
			t.Errorf("Expected request %d to be allowed, but it was disallowed", i+1)
		}
	}

	// 6th request at the same time should be disallowed
	if AllowRequest(clientID, []RateLimit{rateLimit}, now) {
		t.Errorf("Expected 6th request to be disallowed due to rate limit, but it was allowed")
	}
}

func TestAllowRequest_MultipleRateLimits(t *testing.T) {
	clientID := "client2"
	// Two rate limits: one allows 10 requests per 2 seconds and another allows 3 requests per second.
	// The strictest limit (3 per second) should be enforced.
	rateLimits := []RateLimit{
		{Requests: 10, Window: 2 * time.Second},
		{Requests: 3, Window: time.Second},
	}
	now := time.Now()

	// First 3 requests should be allowed
	for i := 0; i < 3; i++ {
		allowed := AllowRequest(clientID, rateLimits, now)
		if !allowed {
			t.Errorf("Expected request %d to be allowed, but it was disallowed", i+1)
		}
	}

	// 4th request should be disallowed as it exceeds the strictest limit
	if AllowRequest(clientID, rateLimits, now) {
		t.Errorf("Expected 4th request to be disallowed due to strict rate limit, but it was allowed")
	}
}

func TestAllowRequest_WindowReset(t *testing.T) {
	clientID := "client3"
	rateLimit := RateLimit{
		Requests: 2,
		Window:   500 * time.Millisecond,
	}
	now := time.Now()

	// Send two requests in the same window; both should be allowed.
	if !AllowRequest(clientID, []RateLimit{rateLimit}, now) {
		t.Errorf("Expected first request to be allowed")
	}
	if !AllowRequest(clientID, []RateLimit{rateLimit}, now) {
		t.Errorf("Expected second request to be allowed")
	}
	// Third request in the same window should be disallowed.
	if AllowRequest(clientID, []RateLimit{rateLimit}, now) {
		t.Errorf("Expected third request to be disallowed in the same window")
	}

	// Advance time past the window and expect the request to be allowed.
	later := now.Add(600 * time.Millisecond)
	if !AllowRequest(clientID, []RateLimit{rateLimit}, later) {
		t.Errorf("Expected request after window reset to be allowed")
	}
}

func TestAllowRequest_Concurrent(t *testing.T) {
	clientID := "client4"
	rateLimit := RateLimit{
		Requests: 100,
		Window:   time.Second,
	}
	now := time.Now()

	var wg sync.WaitGroup
	var allowedCount int
	var mu sync.Mutex
	totalRequests := 200

	// Simulate multiple concurrent requests.
	for i := 0; i < totalRequests; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if AllowRequest(clientID, []RateLimit{rateLimit}, now) {
				mu.Lock()
				allowedCount++
				mu.Unlock()
			}
		}()
	}
	wg.Wait()

	if allowedCount != 100 {
		t.Errorf("Expected exactly 100 allowed requests in concurrent scenario, got %d", allowedCount)
	}
}