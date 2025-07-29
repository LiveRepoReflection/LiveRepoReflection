package tiered_ratelimit

import (
	"sync"
	"sync/atomic"
	"testing"
	"time"
)

// TestFreeTier checks that a free tier key is allowed 10 requests per minute.
func TestFreeTier(t *testing.T) {
	limiter := NewRateLimiter()
	key := "192.168.1.1"
	tier := "free"

	// Free tier allows 10 requests per minute.
	for i := 0; i < 10; i++ {
		allowed := limiter.Allow(key, tier)
		if !allowed {
			t.Errorf("Free tier: expected request %d to be allowed, but was rejected", i+1)
		}
	}

	// The 11th request should be rejected.
	if limiter.Allow(key, tier) {
		t.Error("Free tier: expected 11th request to be rejected")
	}
}

// TestBasicTier checks that a basic tier key is allowed 100 requests per minute.
func TestBasicTier(t *testing.T) {
	limiter := NewRateLimiter()
	key := "BASIC_API_KEY"
	tier := "basic"

	// Basic tier allows 100 requests per minute.
	for i := 0; i < 100; i++ {
		allowed := limiter.Allow(key, tier)
		if !allowed {
			t.Errorf("Basic tier: expected request %d to be allowed, but was rejected", i+1)
		}
	}

	// The 101st request should be rejected.
	if limiter.Allow(key, tier) {
		t.Error("Basic tier: expected 101st request to be rejected")
	}
}

// TestPremiumTier checks that a premium tier key is allowed 1000 requests per minute.
func TestPremiumTier(t *testing.T) {
	limiter := NewRateLimiter()
	key := "PREMIUM_API_KEY"
	tier := "premium"

	// Premium tier allows 1000 requests per minute.
	for i := 0; i < 1000; i++ {
		allowed := limiter.Allow(key, tier)
		if !allowed {
			t.Errorf("Premium tier: expected request %d to be allowed, but was rejected", i+1)
		}
	}

	// The 1001st request should be rejected.
	if limiter.Allow(key, tier) {
		t.Error("Premium tier: expected 1001st request to be rejected")
	}
}

// TestAdminTier checks that an admin tier key is never rate limited.
func TestAdminTier(t *testing.T) {
	limiter := NewRateLimiter()
	key := "ADMIN_API_KEY"
	tier := "admin"

	// Admin tier should never be rate limited.
	for i := 0; i < 2000; i++ {
		if !limiter.Allow(key, tier) {
			t.Errorf("Admin tier: expected request %d to be allowed, but was rejected", i+1)
		}
	}
}

// TestInvalidInput checks how the limiter handles invalid keys and tiers.
func TestInvalidInput(t *testing.T) {
	limiter := NewRateLimiter()

	// Test with an empty key.
	if limiter.Allow("", "free") {
		t.Error("Expected request with empty key to be rejected")
	}

	// Test with an invalid tier.
	if limiter.Allow("some_key", "unknown") {
		t.Error("Expected request with unknown tier to be rejected")
	}
}

// TestConcurrentAccess simulates concurrent requests to the limiter for the free tier.
func TestConcurrentAccess(t *testing.T) {
	limiter := NewRateLimiter()
	key := "192.168.1.2"
	tier := "free"
	
	var wg sync.WaitGroup
	var allowedCount int32

	// Launch 20 goroutines, each making 10 attempts.
	concurrency := 20
	attempts := 10

	wg.Add(concurrency)
	for i := 0; i < concurrency; i++ {
		go func() {
			defer wg.Done()
			for j := 0; j < attempts; j++ {
				if limiter.Allow(key, tier) {
					atomic.AddInt32(&allowedCount, 1)
				}
			}
		}()
	}
	wg.Wait()

	// The free tier only allows 10 requests in a minute.
	if allowedCount > 10 {
		t.Errorf("Concurrent free tier: expected at most 10 allowed requests, got %d", allowedCount)
	}
}

// TestDynamicUpdate simulates dynamic configuration updates by adjusting rate limits mid-stream.
func TestDynamicUpdate(t *testing.T) {
	limiter := NewRateLimiter()
	key := "DYNAMIC_API_KEY"
	tier := "basic"

	// Initially basic tier allows 100 requests.
	for i := 0; i < 100; i++ {
		if !limiter.Allow(key, tier) {
			t.Errorf("Dynamic update (before config change): expected request %d to be allowed", i+1)
		}
	}

	// Assume we have a method to update configuration dynamically.
	// Increase basic tier limit to 200.
	err := limiter.UpdateTierLimit(tier, 200)
	if err != nil {
		t.Errorf("Dynamic update: unexpected error during limit update: %v", err)
	}

	// Allow additional requests up to the new limit, total 200.
	for i := 0; i < 100; i++ {
		if !limiter.Allow(key, tier) {
			t.Errorf("Dynamic update (after config change): expected request %d to be allowed", i+101)
		}
	}

	// The 201st request should be rejected.
	if limiter.Allow(key, tier) {
		t.Error("Dynamic update: expected 201st request to be rejected after raising limit to 200")
	}
}

// TestMinuteBoundary ensures that the rate limiter correctly resets its counters at minute boundaries.
func TestMinuteBoundary(t *testing.T) {
	limiter := NewRateLimiter()
	key := "192.168.1.3"
	tier := "free"

	// Use all allowed requests.
	for i := 0; i < 10; i++ {
		if !limiter.Allow(key, tier) {
			t.Errorf("Minute boundary: expected request %d to be allowed", i+1)
		}
	}

	// Next request should be rejected.
	if limiter.Allow(key, tier) {
		t.Error("Minute boundary: expected request exceeding limit to be rejected")
	}

	// Wait for a minute to allow reset of counters.
	time.Sleep(61 * time.Second)

	// After the minute reset, the first request should be allowed again.
	if !limiter.Allow(key, tier) {
		t.Error("Minute boundary: expected request after minute reset to be allowed")
	}
}