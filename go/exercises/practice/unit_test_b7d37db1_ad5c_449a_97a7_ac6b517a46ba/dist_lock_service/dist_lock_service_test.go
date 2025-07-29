package dist_lock_service

import (
	"testing"
	"time"
)

func TestBasicLockUnlock(t *testing.T) {
	service := NewDistLockService()
	key := "resource_1"
	clientID := "client_A"

	// Test basic acquire and release
	if !service.AcquireLock(key, clientID, time.Second*5) {
		t.Error("Failed to acquire lock")
	}

	if !service.ReleaseLock(key, clientID) {
		t.Error("Failed to release lock")
	}
}

func TestMutualExclusion(t *testing.T) {
	service := NewDistLockService()
	key := "resource_2"
	clientA := "client_A"
	clientB := "client_B"

	// Client A acquires lock
	if !service.AcquireLock(key, clientA, time.Second*5) {
		t.Error("Client A failed to acquire lock")
	}

	// Client B should fail to acquire same lock
	if service.AcquireLock(key, clientB, time.Second*5) {
		t.Error("Client B acquired lock while it was held by Client A")
	}

	// After Client A releases, Client B should succeed
	if !service.ReleaseLock(key, clientA) {
		t.Error("Client A failed to release lock")
	}

	if !service.AcquireLock(key, clientB, time.Second*5) {
		t.Error("Client B failed to acquire lock after release")
	}
}

func TestLockExpiration(t *testing.T) {
	service := NewDistLockService()
	key := "resource_3"
	clientID := "client_A"

	// Acquire with short TTL
	if !service.AcquireLock(key, clientID, time.Millisecond*100) {
		t.Error("Failed to acquire lock")
	}

	// Wait for lock to expire
	time.Sleep(time.Millisecond * 150)

	// Should be able to acquire again
	if !service.AcquireLock(key, clientID, time.Second*5) {
		t.Error("Failed to acquire lock after expiration")
	}
}

func TestLockExtension(t *testing.T) {
	service := NewDistLockService()
	key := "resource_4"
	clientID := "client_A"

	// Acquire with short TTL
	if !service.AcquireLock(key, clientID, time.Millisecond*100) {
		t.Error("Failed to acquire lock")
	}

	// Extend lock
	if !service.ExtendLock(key, clientID, time.Second*5) {
		t.Error("Failed to extend lock")
	}

	// Wait for original TTL to expire
	time.Sleep(time.Millisecond * 150)

	// Should still be locked
	status, holder := service.Status(key)
	if !status || holder != clientID {
		t.Error("Lock expired despite extension")
	}
}

func TestStatusCheck(t *testing.T) {
	service := NewDistLockService()
	key := "resource_5"
	clientID := "client_A"

	// Initial status should be unlocked
	status, _ := service.Status(key)
	if status {
		t.Error("Lock should initially be unlocked")
	}

	// Acquire lock
	if !service.AcquireLock(key, clientID, time.Second*5) {
		t.Error("Failed to acquire lock")
	}

	// Verify status shows locked
	status, holder := service.Status(key)
	if !status || holder != clientID {
		t.Error("Status check failed for locked state")
	}

	// Release lock
	if !service.ReleaseLock(key, clientID) {
		t.Error("Failed to release lock")
	}

	// Verify status shows unlocked
	status, _ = service.Status(key)
	if status {
		t.Error("Status check failed for unlocked state")
	}
}

func TestReentrancy(t *testing.T) {
	service := NewDistLockService()
	key := "resource_6"
	clientID := "client_A"

	// First acquire
	if !service.AcquireLock(key, clientID, time.Second*5) {
		t.Error("Failed to acquire lock")
	}

	// Re-entrant acquire
	if !service.AcquireLock(key, clientID, time.Second*5) {
		t.Error("Failed to re-acquire lock")
	}

	// First release shouldn't actually free the lock
	if !service.ReleaseLock(key, clientID) {
		t.Error("Failed to release lock")
	}

	// Should still be locked
	status, holder := service.Status(key)
	if !status || holder != clientID {
		t.Error("Lock released prematurely")
	}

	// Second release should actually free the lock
	if !service.ReleaseLock(key, clientID) {
		t.Error("Failed to release lock")
	}

	// Should now be unlocked
	status, _ = service.Status(key)
	if status {
		t.Error("Lock not properly released")
	}
}

func TestFairness(t *testing.T) {
	service := NewDistLockService()
	key := "resource_7"
	clientA := "client_A"
	clientB := "client_B"

	// Client A acquires lock
	if !service.AcquireLock(key, clientA, time.Second*1) {
		t.Error("Client A failed to acquire lock")
	}

	// Client B attempts to acquire (should fail)
	if service.AcquireLock(key, clientB, time.Second*5) {
		t.Error("Client B acquired lock while it was held by Client A")
	}

	// Wait for Client A's lock to expire
	time.Sleep(time.Second * 1)

	// Client B should now be able to acquire
	if !service.AcquireLock(key, clientB, time.Second*5) {
		t.Error("Client B failed to acquire lock after Client A's lock expired")
	}
}