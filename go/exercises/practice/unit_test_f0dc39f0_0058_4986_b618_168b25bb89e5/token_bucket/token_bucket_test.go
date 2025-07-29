package tokenbucket

import (
	"sync"
	"testing"
	"time"
)

func TestSingleTenantAllows(t *testing.T) {
	for _, tc := range singleTenantTestCases {
		t.Run(tc.description, func(t *testing.T) {
			limiter := NewRateLimiter()
			limiter.SetLimit(tc.tenantID, tc.initialLimit.capacity, tc.initialLimit.refillRate)

			result := limiter.Allow(tc.tenantID, tc.tokens)
			if result != tc.shouldAllow {
				t.Errorf("Allow(%s, %d) = %v; want %v",
					tc.tenantID, tc.tokens, result, tc.shouldAllow)
			}
		})
	}
}

func TestMultiTenantAllows(t *testing.T) {
	for _, tc := range multiTenantTestCases {
		t.Run(tc.description, func(t *testing.T) {
			limiter := NewRateLimiter()
			
			// Setup tenant configs
			for tenantID, config := range tc.tenants {
				limiter.SetLimit(tenantID, config.capacity, config.refillRate)
			}

			// Run operations
			results := make([]bool, len(tc.operations))
			for i, op := range tc.operations {
				results[i] = limiter.Allow(op.tenantID, op.tokens)
			}

			// Verify results
			for i, want := range tc.expected {
				if results[i] != want {
					t.Errorf("Operation %d: got %v, want %v", i, results[i], want)
				}
			}
		})
	}
}

func TestConcurrentAccess(t *testing.T) {
	limiter := NewRateLimiter()
	tenantID := "tenant1"
	limiter.SetLimit(tenantID, 1000, 100.0)

	var wg sync.WaitGroup
	workers := 10
	requestsPerWorker := 100

	results := make([]bool, workers*requestsPerWorker)
	for w := 0; w < workers; w++ {
		wg.Add(1)
		go func(workerID int) {
			defer wg.Done()
			for i := 0; i < requestsPerWorker; i++ {
				idx := workerID*requestsPerWorker + i
				results[idx] = limiter.Allow(tenantID, 1)
			}
		}(w)
	}

	wg.Wait()

	// Count allowed requests
	allowed := 0
	for _, result := range results {
		if result {
			allowed++
		}
	}

	if allowed > 1000 {
		t.Errorf("Too many requests allowed: got %d, want <= 1000", allowed)
	}
}

func TestRefill(t *testing.T) {
	for _, tc := range refillTestCases {
		t.Run(tc.description, func(t *testing.T) {
			limiter := NewRateLimiter()
			tenantID := "test-tenant"
			limiter.SetLimit(tenantID, tc.initialConfig.capacity, tc.initialConfig.refillRate)

			// Use up all tokens
			limiter.Allow(tenantID, tc.initialConfig.capacity)

			// Wait for refill
			time.Sleep(time.Duration(tc.waitSeconds * float64(time.Second)))

			// Try to consume tokens
			result := limiter.Allow(tenantID, tc.requestedTokens)
			if result != tc.shouldAllow {
				t.Errorf("After waiting %.2f seconds: Allow(%d) = %v; want %v",
					tc.waitSeconds, tc.requestedTokens, result, tc.shouldAllow)
			}
		})
	}
}

func TestDynamicRateUpdate(t *testing.T) {
	limiter := NewRateLimiter()
	tenantID := "tenant1"

	// Initial setup
	limiter.SetLimit(tenantID, 10, 1.0)
	if !limiter.Allow(tenantID, 5) {
		t.Error("Initial request should be allowed")
	}

	// Update rate limit
	limiter.SetLimit(tenantID, 20, 2.0)
	
	// Wait for some tokens to accumulate
	time.Sleep(2 * time.Second)

	// Should allow more tokens now
	if !limiter.Allow(tenantID, 3) {
		t.Error("Request after rate update should be allowed")
	}
}

func BenchmarkAllowSingleTenant(b *testing.B) {
	limiter := NewRateLimiter()
	tenantID := "tenant1"
	limiter.SetLimit(tenantID, 1000000, 1000000.0)

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		limiter.Allow(tenantID, 1)
	}
}

func BenchmarkAllowMultipleTenants(b *testing.B) {
	limiter := NewRateLimiter()
	tenants := []string{"tenant1", "tenant2", "tenant3", "tenant4", "tenant5"}
	
	for _, tenant := range tenants {
		limiter.SetLimit(tenant, 1000000, 1000000.0)
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		tenantID := tenants[i%len(tenants)]
		limiter.Allow(tenantID, 1)
	}
}