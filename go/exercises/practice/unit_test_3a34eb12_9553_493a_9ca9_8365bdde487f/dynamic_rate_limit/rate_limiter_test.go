package dynamic_rate_limit

import (
	"testing"
	"time"
)

func TestAllow(t *testing.T) {
	rl := NewRateLimiter()

	// Test basic rate limiting
	clientID := "client1"
	rl.SetRateLimit(clientID, 10, 1) // 10 requests per second

	for i := 0; i < 10; i++ {
		if !rl.Allow(clientID, 1) {
			t.Errorf("Request %d should be allowed", i+1)
		}
	}

	if rl.Allow(clientID, 1) {
		t.Error("11th request should be denied")
	}

	// Test after window expires
	time.Sleep(1100 * time.Millisecond)
	if !rl.Allow(clientID, 1) {
		t.Error("Request should be allowed after window reset")
	}
}

func TestRequestCost(t *testing.T) {
	rl := NewRateLimiter()
	clientID := "client2"
	rl.SetRateLimit(clientID, 10, 1)

	if !rl.Allow(clientID, 5) {
		t.Error("Request with cost 5 should be allowed")
	}

	if !rl.Allow(clientID, 5) {
		t.Error("Second request with cost 5 should be allowed")
	}

	if rl.Allow(clientID, 1) {
		t.Error("Third request should be denied (total cost 11 > 10)")
	}
}

func TestSetRateLimit(t *testing.T) {
	rl := NewRateLimiter()
	clientID := "client3"

	// Test invalid limits
	if err := rl.SetRateLimit(clientID, -1, 1); err == nil {
		t.Error("Should reject negative limit")
	}

	if err := rl.SetRateLimit(clientID, 10, 0); err == nil {
		t.Error("Should reject zero window")
	}

	// Test valid limit change
	if err := rl.SetRateLimit(clientID, 5, 1); err != nil {
		t.Errorf("Valid limit should be accepted: %v", err)
	}

	for i := 0; i < 5; i++ {
		if !rl.Allow(clientID, 1) {
			t.Errorf("Request %d should be allowed", i+1)
		}
	}

	if rl.Allow(clientID, 1) {
		t.Error("6th request should be denied with new limit")
	}
}

func TestGetRateLimit(t *testing.T) {
	rl := NewRateLimiter()
	clientID := "client4"

	// Test default limit
	limit, window, err := rl.GetRateLimit(clientID)
	if err != nil {
		t.Errorf("Should not error for unknown client: %v", err)
	}
	if limit != 0 || window != 0 {
		t.Errorf("Expected default limit (0,0), got (%d,%d)", limit, window)
	}

	// Test set and get
	rl.SetRateLimit(clientID, 20, 5)
	limit, window, err = rl.GetRateLimit(clientID)
	if err != nil {
		t.Errorf("Should not error for known client: %v", err)
	}
	if limit != 20 || window != 5 {
		t.Errorf("Expected limit (20,5), got (%d,%d)", limit, window)
	}
}

func TestConcurrentAccess(t *testing.T) {
	rl := NewRateLimiter()
	clientID := "client5"
	rl.SetRateLimit(clientID, 1000, 1)

	done := make(chan bool)
	for i := 0; i < 10; i++ {
		go func() {
			for j := 0; j < 100; j++ {
				rl.Allow(clientID, 1)
			}
			done <- true
		}()
	}

	for i := 0; i < 10; i++ {
		<-done
	}

	// After 1000 requests, next should be denied
	if rl.Allow(clientID, 1) {
		t.Error("Request should be denied after 1000 concurrent requests")
	}
}

func TestInvalidClient(t *testing.T) {
	rl := NewRateLimiter()

	// Empty client ID
	if rl.Allow("", 1) {
		t.Error("Should reject empty client ID")
	}

	// Invalid request cost
	if rl.Allow("client6", 0) {
		t.Error("Should reject zero cost request")
	}
	if rl.Allow("client6", -1) {
		t.Error("Should reject negative cost request")
	}
}