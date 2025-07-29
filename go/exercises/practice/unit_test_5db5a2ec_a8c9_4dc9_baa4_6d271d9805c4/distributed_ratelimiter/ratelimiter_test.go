package ratelimiter

import (
	"testing"
	"time"
)

func TestRateLimiterBasic(t *testing.T) {
	rl := InitializeRateLimiter(60, 86400)
	
	err := rl.SetClientLimit("client1", 100)
	if err != nil {
		t.Fatalf("SetClientLimit failed: %v", err)
	}

	err = rl.SetResourceWeight("resource1", 10)
	if err != nil {
		t.Fatalf("SetResourceWeight failed: %v", err)
	}

	allowed, err := rl.Allow("client1", "resource1")
	if err != nil {
		t.Fatalf("Allow failed: %v", err)
	}
	if !allowed {
		t.Error("Expected request to be allowed")
	}
}

func TestRateLimiterExceedLimit(t *testing.T) {
	rl := InitializeRateLimiter(60, 86400)
	
	rl.SetClientLimit("client2", 15)
	rl.SetResourceWeight("resource2", 10)

	allowed, _ := rl.Allow("client2", "resource2")
	if !allowed {
		t.Error("First request should be allowed")
	}

	allowed, _ = rl.Allow("client2", "resource2")
	if allowed {
		t.Error("Second request should be denied")
	}
}

func TestRateLimiterConcurrent(t *testing.T) {
	rl := InitializeRateLimiter(60, 86400)
	rl.SetClientLimit("client3", 100)
	rl.SetResourceWeight("resource3", 1)

	results := make(chan bool, 100)
	for i := 0; i < 100; i++ {
		go func() {
			allowed, _ := rl.Allow("client3", "resource3")
			results <- allowed
		}()
	}

	allowedCount := 0
	for i := 0; i < 100; i++ {
		if <-results {
			allowedCount++
		}
	}

	if allowedCount != 100 {
		t.Errorf("Expected 100 allowed requests, got %d", allowedCount)
	}
}

func TestRateLimiterSlidingWindow(t *testing.T) {
	rl := InitializeRateLimiter(1, 86400)
	rl.SetClientLimit("client4", 10)
	rl.SetResourceWeight("resource4", 1)

	for i := 0; i < 10; i++ {
		allowed, _ := rl.Allow("client4", "resource4")
		if !allowed {
			t.Errorf("Request %d should be allowed", i+1)
		}
	}

	allowed, _ := rl.Allow("client4", "resource4")
	if allowed {
		t.Error("11th request should be denied")
	}

	time.Sleep(1 * time.Second)

	allowed, _ = rl.Allow("client4", "resource4")
	if !allowed {
		t.Error("Request after window should be allowed")
	}
}

func TestRateLimiterReset(t *testing.T) {
	rl := InitializeRateLimiter(60, 86400)
	rl.SetClientLimit("client5", 10)
	rl.SetResourceWeight("resource5", 5)

	allowed, _ := rl.Allow("client5", "resource5")
	if !allowed {
		t.Error("First request should be allowed")
	}

	rl.ResetClient("client5")

	allowed, _ = rl.Allow("client5", "resource5")
	if !allowed {
		t.Error("Request after reset should be allowed")
	}
}

func TestRateLimiterInvalidInput(t *testing.T) {
	rl := InitializeRateLimiter(60, 86400)

	err := rl.SetClientLimit("client6", -1)
	if err == nil {
		t.Error("Expected error for negative limit")
	}

	err = rl.SetResourceWeight("resource6", 0)
	if err == nil {
		t.Error("Expected error for zero weight")
	}

	_, err = rl.Allow("nonexistent", "resource")
	if err == nil {
		t.Error("Expected error for nonexistent client")
	}

	rl.SetClientLimit("client7", 10)
	_, err = rl.Allow("client7", "nonexistent")
	if err == nil {
		t.Error("Expected error for nonexistent resource")
	}
}