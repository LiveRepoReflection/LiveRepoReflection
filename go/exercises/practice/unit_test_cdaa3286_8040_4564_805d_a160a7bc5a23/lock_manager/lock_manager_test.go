package lock_manager

import (
	"testing"
	"time"
)

func TestLockManager_AcquireLock(t *testing.T) {
	lm := NewLockManager()

	// Test basic lock acquisition
	if !lm.AcquireLock("resource1", "client1", 1*time.Second) {
		t.Error("Failed to acquire lock")
	}

	// Test lock already held
	if lm.AcquireLock("resource1", "client2", 1*time.Second) {
		t.Error("Should not acquire lock already held")
	}

	// Test lock release
	if !lm.ReleaseLock("resource1", "client1") {
		t.Error("Failed to release lock")
	}

	// Test lock expiration
	lm.AcquireLock("resource2", "client1", 100*time.Millisecond)
	time.Sleep(150 * time.Millisecond)
	if !lm.AcquireLock("resource2", "client2", 1*time.Second) {
		t.Error("Expired lock should be available")
	}
}

func TestLockManager_Reentrancy(t *testing.T) {
	lm := NewLockManager()

	// Test reentrant lock
	if !lm.AcquireLock("resource1", "client1", 1*time.Second) {
		t.Error("Failed to acquire lock first time")
	}
	if !lm.AcquireLock("resource1", "client1", 1*time.Second) {
		t.Error("Failed to acquire lock second time (reentrant)")
	}

	// Should still be locked after one release
	lm.ReleaseLock("resource1", "client1")
	if lm.AcquireLock("resource1", "client2", 1*time.Second) {
		t.Error("Lock should still be held after one release")
	}

	// Should be available after all releases
	lm.ReleaseLock("resource1", "client1")
	if !lm.AcquireLock("resource1", "client2", 1*time.Second) {
		t.Error("Lock should be available after all releases")
	}
}

func TestLockManager_ExtendLock(t *testing.T) {
	lm := NewLockManager()

	// Test lock extension
	if !lm.AcquireLock("resource1", "client1", 100*time.Millisecond) {
		t.Error("Failed to acquire lock")
	}
	if !lm.ExtendLock("resource1", "client1", 1*time.Second) {
		t.Error("Failed to extend lock")
	}
	time.Sleep(150 * time.Millisecond)
	if lm.AcquireLock("resource1", "client2", 1*time.Second) {
		t.Error("Extended lock should still be held")
	}

	// Test extension by non-holder
	if lm.ExtendLock("resource1", "client2", 1*time.Second) {
		t.Error("Should not be able to extend lock not held")
	}
}

func TestLockManager_ConcurrentAccess(t *testing.T) {
	lm := NewLockManager()
	resource := "concurrentResource"
	iterations := 100
	successChan := make(chan bool, iterations)

	for i := 0; i < iterations; i++ {
		go func(id int) {
			clientID := string(rune(id))
			if lm.AcquireLock(resource, clientID, 10*time.Millisecond) {
				time.Sleep(1 * time.Millisecond)
				lm.ReleaseLock(resource, clientID)
				successChan <- true
			} else {
				successChan <- false
			}
		}(i)
	}

	successCount := 0
	for i := 0; i < iterations; i++ {
		if <-successChan {
			successCount++
		}
	}

	if successCount == 0 {
		t.Error("No locks were acquired in concurrent test")
	} else if successCount == iterations {
		t.Error("All locks were acquired, indicating no contention")
	}
}

func TestLockManager_ClientFailure(t *testing.T) {
	lm := NewLockManager()

	// Simulate client failure by not releasing lock
	lm.AcquireLock("resource1", "client1", 100*time.Millisecond)
	time.Sleep(150 * time.Millisecond)

	// Lock should be available after expiration
	if !lm.AcquireLock("resource1", "client2", 1*time.Second) {
		t.Error("Lock should be available after client failure")
	}
}