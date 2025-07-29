package rate_limit_dist

import (
	"context"
	"sync"
	"testing"
	"time"
)

func TestRateLimiter_Allow(t *testing.T) {
	rl := NewRateLimiter(NewInMemoryStore())

	tests := []struct {
		name       string
		clientID   string
		endpoint   string
		limit      int
		window     time.Duration
		requests   int
		wantAllowed int
		wantErr    bool
	}{
		{
			name:       "basic rate limit",
			clientID:   "client1",
			endpoint:   "/api",
			limit:      10,
			window:     time.Minute,
			requests:   15,
			wantAllowed: 10,
			wantErr:    false,
		},
		{
			name:       "different clients",
			clientID:   "client2",
			endpoint:   "/api",
			limit:      5,
			window:     time.Minute,
			requests:   6,
			wantAllowed: 5,
			wantErr:    false,
		},
		{
			name:       "different endpoints",
			clientID:   "client1",
			endpoint:   "/api/v2",
			limit:      3,
			window:     time.Minute,
			requests:   4,
			wantAllowed: 3,
			wantErr:    false,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			err := rl.SetLimit(context.Background(), tt.clientID, tt.endpoint, tt.limit, tt.window)
			if err != nil {
				t.Fatalf("SetLimit() error = %v", err)
			}

			var allowed int
			for i := 0; i < tt.requests; i++ {
				res, err := rl.Allow(context.Background(), tt.clientID, tt.endpoint)
				if err != nil {
					if !tt.wantErr {
						t.Errorf("Allow() unexpected error = %v", err)
					}
					continue
				}
				if res.Allowed {
					allowed++
				}
			}

			if allowed != tt.wantAllowed {
				t.Errorf("Allow() allowed = %v, want %v", allowed, tt.wantAllowed)
			}
		})
	}
}

func TestRateLimiter_ConcurrentAccess(t *testing.T) {
	rl := NewRateLimiter(NewInMemoryStore())
	clientID := "concurrent_client"
	endpoint := "/api"
	limit := 100
	window := time.Minute

	err := rl.SetLimit(context.Background(), clientID, endpoint, limit, window)
	if err != nil {
		t.Fatalf("SetLimit() error = %v", err)
	}

	var wg sync.WaitGroup
	var allowed int
	var mu sync.Mutex

	for i := 0; i < 150; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			res, err := rl.Allow(context.Background(), clientID, endpoint)
			if err != nil {
				t.Errorf("Allow() error = %v", err)
				return
			}
			if res.Allowed {
				mu.Lock()
				allowed++
				mu.Unlock()
			}
		}()
	}

	wg.Wait()

	if allowed > limit {
		t.Errorf("Concurrent access exceeded limit: got %d, want max %d", allowed, limit)
	}
}

func TestRateLimiter_WindowExpiration(t *testing.T) {
	rl := NewRateLimiter(NewInMemoryStore())
	clientID := "window_client"
	endpoint := "/api"
	limit := 5
	window := 2 * time.Second

	err := rl.SetLimit(context.Background(), clientID, endpoint, limit, window)
	if err != nil {
		t.Fatalf("SetLimit() error = %v", err)
	}

	// Exhaust the limit
	for i := 0; i < limit; i++ {
		_, err := rl.Allow(context.Background(), clientID, endpoint)
		if err != nil {
			t.Fatalf("Allow() error = %v", err)
		}
	}

	// Should be rate limited now
	res, err := rl.Allow(context.Background(), clientID, endpoint)
	if err != nil {
		t.Fatalf("Allow() error = %v", err)
	}
	if res.Allowed {
		t.Error("Expected to be rate limited")
	}

	// Wait for window to expire
	time.Sleep(window + 100*time.Millisecond)

	// Should be allowed again
	res, err = rl.Allow(context.Background(), clientID, endpoint)
	if err != nil {
		t.Fatalf("Allow() error = %v", err)
	}
	if !res.Allowed {
		t.Error("Expected to be allowed after window expiration")
	}
}

func TestRateLimiter_DynamicLimitChanges(t *testing.T) {
	rl := NewRateLimiter(NewInMemoryStore())
	clientID := "dynamic_client"
	endpoint := "/api"

	// Set initial limit
	err := rl.SetLimit(context.Background(), clientID, endpoint, 5, time.Minute)
	if err != nil {
		t.Fatalf("SetLimit() error = %v", err)
	}

	// Use 3 requests
	for i := 0; i < 3; i++ {
		_, err := rl.Allow(context.Background(), clientID, endpoint)
		if err != nil {
			t.Fatalf("Allow() error = %v", err)
		}
	}

	// Increase limit
	err = rl.SetLimit(context.Background(), clientID, endpoint, 10, time.Minute)
	if err != nil {
		t.Fatalf("SetLimit() error = %v", err)
	}

	// Should be able to make 7 more requests (3 already used, new limit is 10)
	for i := 0; i < 7; i++ {
		res, err := rl.Allow(context.Background(), clientID, endpoint)
		if err != nil {
			t.Fatalf("Allow() error = %v", err)
		}
		if !res.Allowed {
			t.Errorf("Expected request %d to be allowed", i+4)
		}
	}

	// Next request should be denied
	res, err := rl.Allow(context.Background(), clientID, endpoint)
	if err != nil {
		t.Fatalf("Allow() error = %v", err)
	}
	if res.Allowed {
		t.Error("Expected to be rate limited after dynamic limit change")
	}
}