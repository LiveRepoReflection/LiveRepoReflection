package tenant_limiter

import (
	"context"
	"fmt"
	"math/rand"
	"sync"
	"testing"
	"time"
)

func TestAllowBasicFunctionality(t *testing.T) {
	// Reset any global state that might affect the test
	// This is implementation-specific and may need to be adjusted

	tests := []struct {
		name       string
		tenantID   string
		rateLimit  int
		window     int
		calls      int
		wantAllows int
	}{
		{
			name:       "single request within limit",
			tenantID:   "tenant1",
			rateLimit:  5,
			window:     60,
			calls:      1,
			wantAllows: 1,
		},
		{
			name:       "multiple requests within limit",
			tenantID:   "tenant2",
			rateLimit:  5,
			window:     60,
			calls:      3,
			wantAllows: 3,
		},
		{
			name:       "requests at limit",
			tenantID:   "tenant3",
			rateLimit:  5,
			window:     60,
			calls:      5,
			wantAllows: 5,
		},
		{
			name:       "requests exceeding limit",
			tenantID:   "tenant4",
			rateLimit:  5,
			window:     60,
			calls:      10,
			wantAllows: 5,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			allows := 0
			for i := 0; i < tt.calls; i++ {
				if Allow(tt.tenantID, tt.rateLimit, tt.window) {
					allows++
				}
			}

			if allows != tt.wantAllows {
				t.Errorf("Got %d allows, want %d", allows, tt.wantAllows)
			}
		})
	}
}

func TestAllowConcurrency(t *testing.T) {
	const (
		tenantID   = "concurrent-tenant"
		rateLimit  = 1000
		window     = 60
		goroutines = 100
		callsPerGoroutine = 20
	)

	var wg sync.WaitGroup
	var allowed int32
	var mu sync.Mutex

	// Launch concurrent goroutines
	for i := 0; i < goroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			localAllowed := 0

			for j := 0; j < callsPerGoroutine; j++ {
				if Allow(tenantID, rateLimit, window) {
					localAllowed++
				}
			}

			mu.Lock()
			allowed += int32(localAllowed)
			mu.Unlock()
		}()
	}

	wg.Wait()

	// Check if the total number of allowed requests is within the rate limit
	if allowed > int32(rateLimit) {
		t.Errorf("Rate limit exceeded: got %d allowed requests, want at most %d", allowed, rateLimit)
	}
}

func TestAllowMultipleTenants(t *testing.T) {
	tenants := []struct {
		id        string
		rateLimit int
		window    int
	}{
		{"tenant-a", 5, 60},
		{"tenant-b", 10, 60},
		{"tenant-c", 15, 60},
	}

	// Make requests for each tenant
	for _, tenant := range tenants {
		allowed := 0
		exceeded := 0

		// Make more requests than the rate limit
		for i := 0; i < tenant.rateLimit*2; i++ {
			if Allow(tenant.id, tenant.rateLimit, tenant.window) {
				allowed++
			} else {
				exceeded++
			}
		}

		// Check if the number of allowed requests matches the rate limit
		if allowed != tenant.rateLimit {
			t.Errorf("Tenant %s: got %d allowed, want %d", tenant.id, allowed, tenant.rateLimit)
		}

		// Check if the number of exceeded requests is as expected
		expectedExceeded := tenant.rateLimit
		if exceeded != expectedExceeded {
			t.Errorf("Tenant %s: got %d exceeded, want %d", tenant.id, exceeded, expectedExceeded)
		}
	}
}

func TestAllowEdgeCases(t *testing.T) {
	tests := []struct {
		name      string
		tenantID  string
		rateLimit int
		window    int
		want      bool
	}{
		{
			name:      "zero rate limit",
			tenantID:  "edge-tenant-1",
			rateLimit: 0,
			window:    60,
			want:      false,
		},
		{
			name:      "negative rate limit",
			tenantID:  "edge-tenant-2",
			rateLimit: -5,
			window:    60,
			want:      false,
		},
		{
			name:      "zero window",
			tenantID:  "edge-tenant-3",
			rateLimit: 5,
			window:    0,
			want:      false,
		},
		{
			name:      "negative window",
			tenantID:  "edge-tenant-4",
			rateLimit: 5,
			window:    -60,
			want:      false,
		},
		{
			name:      "empty tenant ID",
			tenantID:  "",
			rateLimit: 5,
			window:    60,
			want:      true, // Assuming empty tenant IDs are valid
		},
		{
			name:      "very large values",
			tenantID:  "edge-tenant-5",
			rateLimit: 1000000,
			window:    86400, // 1 day
			want:      true,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := Allow(tt.tenantID, tt.rateLimit, tt.window)
			if got != tt.want {
				t.Errorf("Allow(%q, %d, %d) = %v, want %v", tt.tenantID, tt.rateLimit, tt.window, got, tt.want)
			}
		})
	}
}

func TestAllowWindowReset(t *testing.T) {
	// This test is more complex and may need to be adjusted based on implementation
	// It attempts to test if the window correctly resets
	
	tenantID := "window-reset-tenant"
	rateLimit := 5
	window := 1 // 1 second window for quicker testing

	// First, exhaust the limit
	for i := 0; i < rateLimit; i++ {
		if !Allow(tenantID, rateLimit, window) {
			t.Fatalf("Expected request %d to be allowed", i+1)
		}
	}

	// Next request should be denied
	if Allow(tenantID, rateLimit, window) {
		t.Errorf("Expected request to be denied after limit exhausted")
	}

	// Wait for the window to expire
	time.Sleep(time.Duration(window+1) * time.Second)

	// After window expires, should be allowed again
	if !Allow(tenantID, rateLimit, window) {
		t.Errorf("Expected request to be allowed after window reset")
	}
}

func TestAllowTimeGracefulness(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping time-based test in short mode")
	}

	tenantID := "grace-tenant"
	rateLimit := 3
	window := 2 // 2 seconds

	// Use up the rate limit
	for i := 0; i < rateLimit; i++ {
		if !Allow(tenantID, rateLimit, window) {
			t.Fatalf("Expected request %d to be allowed", i+1)
		}
	}

	// This should be denied
	if Allow(tenantID, rateLimit, window) {
		t.Error("Expected request to be denied")
	}

	// Wait for part of the window (but not the whole window)
	time.Sleep(time.Second)

	// Should still be denied
	if Allow(tenantID, rateLimit, window) {
		t.Error("Expected request to be denied before window reset")
	}

	// Wait for the rest of the window to expire
	time.Sleep(time.Second * 2)

	// Should be allowed now
	if !Allow(tenantID, rateLimit, window) {
		t.Error("Expected request to be allowed after window reset")
	}
}

func TestHighVolumeSpikes(t *testing.T) {
	if testing.Short() {
		t.Skip("skipping high volume test in short mode")
	}

	// Test scenario with sudden traffic spikes
	const (
		tenantID        = "spike-tenant"
		rateLimit       = 500
		window          = 5 // seconds
		requestsPerSpike = 200
		numSpikes       = 5
	)

	var wg sync.WaitGroup
	ctx, cancel := context.WithTimeout(context.Background(), time.Duration(window*2)*time.Second)
	defer cancel()

	// Launch spikes of traffic
	for i := 0; i < numSpikes; i++ {
		wg.Add(1)
		go func(spikeNum int) {
			defer wg.Done()
			
			allowed := 0
			denied := 0
			
			// Create a spike of traffic
			for j := 0; j < requestsPerSpike; j++ {
				select {
				case <-ctx.Done():
					return
				default:
					if Allow(tenantID, rateLimit, window) {
						allowed++
					} else {
						denied++
					}
					
					// Add some randomness to simulate real traffic
					time.Sleep(time.Duration(rand.Intn(5)) * time.Millisecond)
				}
			}
			
			t.Logf("Spike %d: allowed=%d, denied=%d", spikeNum, allowed, denied)
		}(i)
		
		// Add small delay between spikes
		time.Sleep(time.Duration(50+rand.Intn(50)) * time.Millisecond)
	}

	wg.Wait()
	
	// After all spikes, verify one more request to ensure rate limiting worked
	totalAllowed := 0
	for i := 0; i < rateLimit*2; i++ {
		if Allow(tenantID, rateLimit, window) {
			totalAllowed++
		}
	}
	
	// Check if the number of allowed requests doesn't greatly exceed the rate limit
	// Allow some margin for sliding window implementations
	marginFactor := 1.1 // 10% margin
	if float64(totalAllowed) > float64(rateLimit)*marginFactor {
		t.Errorf("Rate limit significantly exceeded: got %d allowed requests, expected around %d", 
			totalAllowed, rateLimit)
	}
}

func BenchmarkAllow(b *testing.B) {
	// Define different tenant profiles
	tenants := []struct {
		id        string
		rateLimit int
		window    int
	}{
		{"bench-tenant-1", 10, 60},
		{"bench-tenant-2", 100, 60},
		{"bench-tenant-3", 1000, 60},
		{"bench-tenant-4", 10000, 60},
	}

	for _, tenant := range tenants {
		b.Run(fmt.Sprintf("RateLimit_%d", tenant.rateLimit), func(b *testing.B) {
			b.ResetTimer()
			for i := 0; i < b.N; i++ {
				Allow(tenant.id, tenant.rateLimit, tenant.window)
			}
		})
	}

	// Test with many distinct tenants
	b.Run("ManyTenants", func(b *testing.B) {
		b.ResetTimer()
		for i := 0; i < b.N; i++ {
			tenantID := fmt.Sprintf("bench-tenant-%d", i%1000)
			Allow(tenantID, 100, 60)
		}
	})
}

func BenchmarkAllowParallel(b *testing.B) {
	b.Run("Parallel_10Tenants", func(b *testing.B) {
		b.RunParallel(func(pb *testing.PB) {
			// Each goroutine gets its own tenant ID from a small pool
			tenantID := fmt.Sprintf("parallel-tenant-%d", rand.Intn(10))
			for pb.Next() {
				Allow(tenantID, 1000, 60)
			}
		})
	})

	b.Run("Parallel_1000Tenants", func(b *testing.B) {
		b.RunParallel(func(pb *testing.PB) {
			// Each goroutine gets its own tenant ID from a larger pool
			tenantID := fmt.Sprintf("parallel-tenant-%d", rand.Intn(1000))
			for pb.Next() {
				Allow(tenantID, 1000, 60)
			}
		})
	})
}