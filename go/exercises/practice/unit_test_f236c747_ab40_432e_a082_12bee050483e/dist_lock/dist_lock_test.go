package distlock

import (
	"sync"
	"testing"
	"time"
)

type operationType int

const (
	acquire operationType = iota
	release
	extend
)

type operation struct {
	opType        operationType
	resourceID    string
	leaseDuration time.Duration
}

type result struct {
	success bool
	err     error
}

func TestDistLock(t *testing.T) {
	for _, tc := range testCases {
		t.Run(tc.description, func(t *testing.T) {
			lock := NewDistLock()
			
			for i, op := range tc.operations {
				var success bool
				var err error
				
				switch op.opType {
				case acquire:
					success, err = lock.AcquireLock(op.resourceID, op.leaseDuration)
				case release:
					err = lock.ReleaseLock(op.resourceID)
					success = err == nil
				case extend:
					success, err = lock.ExtendLock(op.resourceID, op.leaseDuration)
				}
				
				if success != tc.expectedResults[i].success {
					t.Errorf("Operation %d: expected success=%v, got=%v", i, tc.expectedResults[i].success, success)
				}
				if err != tc.expectedResults[i].err {
					t.Errorf("Operation %d: expected error=%v, got=%v", i, tc.expectedResults[i].err, err)
				}
			}
		})
	}
}

func TestConcurrentAccess(t *testing.T) {
	lock := NewDistLock()
	resourceID := "shared-resource"
	numGoroutines := 10
	
	var wg sync.WaitGroup
	successCount := 0
	var mu sync.Mutex
	
	for i := 0; i < numGoroutines; i++ {
		wg.Add(1)
		go func() {
			defer wg.Done()
			success, _ := lock.AcquireLock(resourceID, time.Second)
			if success {
				mu.Lock()
				successCount++
				mu.Unlock()
				time.Sleep(time.Millisecond * 100)
				lock.ReleaseLock(resourceID)
			}
		}()
	}
	
	wg.Wait()
	
	if successCount == 0 {
		t.Error("Expected at least one successful lock acquisition")
	}
	if successCount == numGoroutines {
		t.Error("All goroutines acquired the lock simultaneously, which shouldn't be possible")
	}
}

func TestLockExpiration(t *testing.T) {
	lock := NewDistLock()
	resourceID := "expiring-resource"
	
	success, err := lock.AcquireLock(resourceID, time.Millisecond*100)
	if !success || err != nil {
		t.Fatalf("Failed to acquire initial lock: success=%v, err=%v", success, err)
	}
	
	time.Sleep(time.Millisecond * 200)
	
	success, err = lock.AcquireLock(resourceID, time.Second)
	if !success || err != nil {
		t.Errorf("Failed to acquire lock after expiration: success=%v, err=%v", success, err)
	}
}

func BenchmarkLockOperations(b *testing.B) {
	lock := NewDistLock()
	resourceID := "bench-resource"
	
	b.RunParallel(func(pb *testing.PB) {
		for pb.Next() {
			success, _ := lock.AcquireLock(resourceID, time.Millisecond*100)
			if success {
				lock.ReleaseLock(resourceID)
			}
		}
	})
}