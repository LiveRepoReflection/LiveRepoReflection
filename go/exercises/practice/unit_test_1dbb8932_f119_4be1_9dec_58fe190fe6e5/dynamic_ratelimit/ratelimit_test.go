package ratelimit

import (
	"sync"
	"testing"
	"time"
)

func TestAllow(t *testing.T) {
	rl := NewRateLimiter()

	// Test basic rate limiting
	bucket := "test_bucket"
	rl.CreateBucket(bucket, 10, 5) // 10 req/s, burst of 5

	// First 5 requests should be allowed (burst)
	for i := 0; i < 5; i++ {
		if !rl.Allow(bucket) {
			t.Errorf("Request %d should be allowed (burst)", i+1)
		}
	}

	// Next request should be rejected (burst exhausted)
	if rl.Allow(bucket) {
		t.Error("Request should be rejected after burst")
	}

	// After 100ms, should allow 1 more request (10 req/s = 1 every 100ms)
	time.Sleep(100 * time.Millisecond)
	if !rl.Allow(bucket) {
		t.Error("Request should be allowed after token refill")
	}
}

func TestCreateUpdateDeleteBucket(t *testing.T) {
	rl := NewRateLimiter()

	// Test bucket creation
	bucket := "test_bucket"
	err := rl.CreateBucket(bucket, 10, 5)
	if err != nil {
		t.Errorf("CreateBucket failed: %v", err)
	}

	// Test updating bucket
	err = rl.UpdateBucket(bucket, 20, 10)
	if err != nil {
		t.Errorf("UpdateBucket failed: %v", err)
	}

	// Test deleting bucket
	err = rl.DeleteBucket(bucket)
	if err != nil {
		t.Errorf("DeleteBucket failed: %v", err)
	}

	// Test operations on non-existent bucket
	if rl.Allow("nonexistent") {
		t.Error("Allow should fail for non-existent bucket")
	}

	err = rl.UpdateBucket("nonexistent", 1, 1)
	if err == nil {
		t.Error("UpdateBucket should fail for non-existent bucket")
	}

	err = rl.DeleteBucket("nonexistent")
	if err == nil {
		t.Error("DeleteBucket should fail for non-existent bucket")
	}
}

func TestConcurrentAccess(t *testing.T) {
	rl := NewRateLimiter()
	bucket := "concurrent_bucket"
	rl.CreateBucket(bucket, 1000, 1000) // High limit for concurrent testing

	var wg sync.WaitGroup
	successCount := 0
	var mu sync.Mutex

	// Launch 1000 concurrent requests
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			if rl.Allow(bucket) {
				mu.Lock()
				successCount++
				mu.Unlock()
			}
		}()
	}

	wg.Wait()

	if successCount != 1000 {
		t.Errorf("Expected 1000 successful requests, got %d", successCount)
	}
}

func TestEdgeCases(t *testing.T) {
	rl := NewRateLimiter()

	// Test invalid bucket creation
	err := rl.CreateBucket("", 10, 5)
	if err == nil {
		t.Error("Should reject empty bucket ID")
	}

	err = rl.CreateBucket("valid", 0, 5)
	if err == nil {
		t.Error("Should reject zero rate limit")
	}

	err = rl.CreateBucket("valid", 10, 0)
	if err == nil {
		t.Error("Should reject zero burst size")
	}

	// Test duplicate bucket creation
	err = rl.CreateBucket("duplicate", 10, 5)
	if err != nil {
		t.Errorf("First CreateBucket failed: %v", err)
	}
	err = rl.CreateBucket("duplicate", 10, 5)
	if err == nil {
		t.Error("Should reject duplicate bucket creation")
	}
}

func BenchmarkAllow(b *testing.B) {
	rl := NewRateLimiter()
	bucket := "benchmark_bucket"
	rl.CreateBucket(bucket, 1000000, 1000000) // Very high limit for benchmarking

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		rl.Allow(bucket)
	}
}

func BenchmarkConcurrentAllow(b *testing.B) {
	rl := NewRateLimiter()
	bucket := "concurrent_benchmark"
	rl.CreateBucket(bucket, 1000000, 1000000)

	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			rl.Allow(bucket)
		}
	})
}