package dynamic_throttle

import (
	"sync"
	"testing"
	"time"
)

func TestRateLimiter_AllowRequest(t *testing.T) {
	rl := NewRateLimiter(100, time.Minute) // 100 requests per minute

	t.Run("single client under limit", func(t *testing.T) {
		clientID := "client1"
		for i := 0; i < 100; i++ {
			if !rl.AllowRequest(clientID, 0) {
				t.Errorf("Request %d should be allowed", i+1)
			}
		}
	})

	t.Run("single client over limit", func(t *testing.T) {
		clientID := "client2"
		// First 100 should pass
		for i := 0; i < 100; i++ {
			rl.AllowRequest(clientID, 0)
		}
		// Next request should fail
		if rl.AllowRequest(clientID, 0) {
			t.Error("Request 101 should be rejected")
		}
	})

	t.Run("multiple clients independently", func(t *testing.T) {
		client1 := "client3"
		client2 := "client4"

		for i := 0; i < 50; i++ {
			if !rl.AllowRequest(client1, 0) || !rl.AllowRequest(client2, 0) {
				t.Error("Requests should be allowed for both clients")
			}
		}
	})

	t.Run("window reset", func(t *testing.T) {
		clientID := "client5"
		// Exhaust limit
		for i := 0; i < 100; i++ {
			rl.AllowRequest(clientID, 0)
		}
		// Fast forward time
		rl.nowFunc = func() time.Time {
			return time.Now().Add(time.Minute + time.Second)
		}
		defer func() { rl.nowFunc = time.Now }()

		if !rl.AllowRequest(clientID, 0) {
			t.Error("Request should be allowed after window reset")
		}
	})
}

func TestRateLimiter_ConcurrentAccess(t *testing.T) {
	rl := NewRateLimiter(1000, time.Minute)
	clientID := "concurrent_client"
	var wg sync.WaitGroup

	for i := 0; i < 10; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			for j := 0; j < 100; j++ {
				rl.AllowRequest(clientID, 0)
			}
		}()
	}
	wg.Wait()

	if allowed := rl.AllowRequest(clientID, 0); allowed {
		t.Error("Request should be rejected after concurrent limit exhaustion")
	}
}

func TestDynamicThrottling(t *testing.T) {
	rl := NewRateLimiter(100, time.Minute)

	t.Run("no throttling under threshold", func(t *testing.T) {
		rl.UpdateSystemLoad(50) // 50% load
		if rl.currentMaxRequests != 100 {
			t.Errorf("Expected max requests 100, got %d", rl.currentMaxRequests)
		}
	})

	t.Run("throttling activates over threshold", func(t *testing.T) {
		rl.UpdateSystemLoad(85) // 85% load should trigger throttling
		if rl.currentMaxRequests >= 100 {
			t.Error("Expected reduced max requests when system load is high")
		}
	})

	t.Run("throttling recovers when load decreases", func(t *testing.T) {
		rl.UpdateSystemLoad(30) // 30% load should recover
		if rl.currentMaxRequests != 100 {
			t.Error("Expected max requests to return to original value")
		}
	})

	t.Run("throttling affects rate limiting", func(t *testing.T) {
		clientID := "throttle_client"
		rl.UpdateSystemLoad(90) // Trigger throttling
		throttledMax := rl.currentMaxRequests

		// Use up throttled limit
		for i := 0; i < throttledMax; i++ {
			rl.AllowRequest(clientID, 90)
		}
		if rl.AllowRequest(clientID, 90) {
			t.Error("Request should be rejected after hitting throttled limit")
		}
	})
}

func TestEdgeCases(t *testing.T) {
	t.Run("zero window duration", func(t *testing.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Error("Expected panic with zero window duration")
			}
		}()
		NewRateLimiter(10, 0)
	})

	t.Run("zero max requests", func(t *testing.T) {
		rl := NewRateLimiter(0, time.Minute)
		if rl.AllowRequest("client", 0) {
			t.Error("Request should always be rejected with zero max requests")
		}
	})

	t.Run("empty client ID", func(t *testing.T) {
		rl := NewRateLimiter(10, time.Minute)
		if rl.AllowRequest("", 0) {
			t.Error("Request with empty client ID should be rejected")
		}
	})
}