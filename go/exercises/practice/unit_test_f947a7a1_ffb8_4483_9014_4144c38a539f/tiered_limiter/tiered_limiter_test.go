package tiered_limiter

import (
	"sync"
	"testing"
	"time"
)

type mockRateLimitStore struct {
	limits map[string]struct {
		limit    int
		duration time.Duration
	}
}

func (m *mockRateLimitStore) GetRateLimit(tier string) (int, time.Duration, error) {
	limit := m.limits[tier]
	return limit.limit, limit.duration, nil
}

func TestRateLimiter_Allow(t *testing.T) {
	store := &mockRateLimitStore{
		limits: map[string]struct {
			limit    int
			duration time.Duration
		}{
			"free":    {5, time.Minute},
			"basic":   {10, time.Minute},
			"premium": {20, time.Minute},
		},
	}

	rl := NewRateLimiter(store)

	tests := []struct {
		name     string
		userID   string
		tier     string
		requests int
		want     bool
	}{
		{"free user under limit", "user1", "free", 4, true},
		{"free user at limit", "user2", "free", 5, true},
		{"free user over limit", "user3", "free", 6, false},
		{"basic user under limit", "user4", "basic", 9, true},
		{"basic user at limit", "user5", "basic", 10, true},
		{"basic user over limit", "user6", "basic", 11, false},
		{"premium user under limit", "user7", "premium", 19, true},
		{"premium user at limit", "user8", "premium", 20, true},
		{"premium user over limit", "user9", "premium", 21, false},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			for i := 0; i < tt.requests; i++ {
				got := rl.Allow(tt.userID, tt.tier)
				if i < tt.requests-1 && !got {
					t.Errorf("Allow() = %v, want true for request %d", got, i+1)
				}
				if i == tt.requests-1 && got != tt.want {
					t.Errorf("Allow() = %v, want %v for final request", got, tt.want)
				}
			}
		})
	}
}

func TestRateLimiter_TimeWindow(t *testing.T) {
	store := &mockRateLimitStore{
		limits: map[string]struct {
			limit    int
			duration time.Duration
		}{
			"test": {2, 500 * time.Millisecond},
		},
	}

	rl := NewRateLimiter(store)

	// First two requests should pass
	if !rl.Allow("user1", "test") {
		t.Error("Allow() = false, want true for first request")
	}
	if !rl.Allow("user1", "test") {
		t.Error("Allow() = false, want true for second request")
	}
	if rl.Allow("user1", "test") {
		t.Error("Allow() = true, want false for third request")
	}

	// After time window expires, should allow again
	time.Sleep(600 * time.Millisecond)
	if !rl.Allow("user1", "test") {
		t.Error("Allow() = false, want true after time window reset")
	}
}

func TestRateLimiter_ConcurrentAccess(t *testing.T) {
	store := &mockRateLimitStore{
		limits: map[string]struct {
			limit    int
			duration time.Duration
		}{
			"concurrent": {1000, time.Minute},
		},
	}

	rl := NewRateLimiter(store)
	var wg sync.WaitGroup
	userID := "concurrent_user"
	tier := "concurrent"

	// Simulate 1000 concurrent requests
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if !rl.Allow(userID, tier) {
				t.Error("Allow() = false in concurrent access")
			}
		}()
	}
	wg.Wait()

	// Next request should be rejected
	if rl.Allow(userID, tier) {
		t.Error("Allow() = true, want false after limit reached")
	}
}

func TestRateLimiter_TierUpdates(t *testing.T) {
	store := &mockRateLimitStore{
		limits: map[string]struct {
			limit    int
			duration time.Duration
		}{
			"updatable": {5, time.Minute},
		},
	}

	rl := NewRateLimiter(store)
	userID := "update_user"
	tier := "updatable"

	// Use up the initial limit
	for i := 0; i < 5; i++ {
		if !rl.Allow(userID, tier) {
			t.Errorf("Allow() = false on request %d", i+1)
		}
	}

	// Update the tier limit
	store.limits[tier] = struct {
		limit    int
		duration time.Duration
	}{10, time.Minute}

	// Should now allow more requests
	for i := 0; i < 5; i++ {
		if !rl.Allow(userID, tier) {
			t.Errorf("Allow() = false after update on request %d", i+1)
		}
	}

	// Should reject after new limit
	if rl.Allow(userID, tier) {
		t.Error("Allow() = true, want false after new limit reached")
	}
}