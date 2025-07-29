package dist_lock_mgr

import (
	"fmt"
	"sync"
	"testing"
	"time"
)

func TestAcquireAndRelease(t *testing.T) {
	lm := NewLockManager()
	err := lm.AcquireLock("client1", "resource1", 2*time.Second)
	if err != nil {
		t.Fatalf("AcquireLock failed: %v", err)
	}
	err = lm.ReleaseLock("client1", "resource1")
	if err != nil {
		t.Fatalf("ReleaseLock failed: %v", err)
	}
}

func TestBlockingAcquisition(t *testing.T) {
	lm := NewLockManager()

	// Client1 acquires the lock on resource2.
	err := lm.AcquireLock("client1", "resource2", 3*time.Second)
	if err != nil {
		t.Fatalf("Initial AcquireLock failed: %v", err)
	}

	done := make(chan bool)
	// Start a goroutine for client2 trying to acquire the same lock.
	go func() {
		err := lm.AcquireLock("client2", "resource2", 3*time.Second)
		if err != nil {
			t.Errorf("Concurrent AcquireLock failed: %v", err)
			done <- false
			return
		}
		// Once acquired, release the lock.
		if err := lm.ReleaseLock("client2", "resource2"); err != nil {
			t.Errorf("ReleaseLock by client2 failed: %v", err)
			done <- false
			return
		}
		done <- true
	}()

	// Wait 1 second then release the lock from client1.
	time.Sleep(1 * time.Second)
	if err := lm.ReleaseLock("client1", "resource2"); err != nil {
		t.Fatalf("ReleaseLock by client1 failed: %v", err)
	}

	select {
	case ok := <-done:
		if !ok {
			t.Fatal("Concurrent lock acquisition failed in goroutine")
		}
	case <-time.After(5 * time.Second):
		t.Fatal("Blocking acquisition timed out")
	}
}

func TestReentrancy(t *testing.T) {
	lm := NewLockManager()

	// Client3 acquires the lock on resource3 twice (reentrant acquisition).
	if err := lm.AcquireLock("client3", "resource3", 3*time.Second); err != nil {
		t.Fatalf("First AcquireLock failed: %v", err)
	}
	if err := lm.AcquireLock("client3", "resource3", 3*time.Second); err != nil {
		t.Fatalf("Reentrant AcquireLock failed: %v", err)
	}

	// Release once; the lock should still be held by client3.
	if err := lm.ReleaseLock("client3", "resource3"); err != nil {
		t.Fatalf("First ReleaseLock failed: %v", err)
	}

	// Start a goroutine for client4 trying to acquire the same lock.
	done := make(chan error)
	go func() {
		err := lm.AcquireLock("client4", "resource3", 2*time.Second)
		done <- err
	}()

	// Wait briefly to ensure client4 is blocked.
	select {
	case err := <-done:
		if err == nil {
			t.Fatal("Lock acquired by non-holder during reentrant hold")
		}
	case <-time.After(1 * time.Second):
		// Expected: client4 should still be waiting.
	}

	// Fully release the lock from client3.
	if err := lm.ReleaseLock("client3", "resource3"); err != nil {
		t.Fatalf("Final ReleaseLock failed: %v", err)
	}

	// Now client4 should be able to acquire the lock.
	if err := lm.AcquireLock("client4", "resource3", 2*time.Second); err != nil {
		t.Fatalf("AcquireLock by client4 after complete release failed: %v", err)
	}
	if err := lm.ReleaseLock("client4", "resource3"); err != nil {
		t.Fatalf("ReleaseLock by client4 failed: %v", err)
	}
}

func TestReleaseByNonHolder(t *testing.T) {
	lm := NewLockManager()

	// Client5 acquires the lock on resource4.
	if err := lm.AcquireLock("client5", "resource4", 2*time.Second); err != nil {
		t.Fatalf("AcquireLock failed: %v", err)
	}

	// Attempt to release the lock from client6 who does not hold it.
	if err := lm.ReleaseLock("client6", "resource4"); err == nil {
		t.Fatal("ReleaseLock by non-holder did not return an error")
	}

	// Client5 releases the lock.
	if err := lm.ReleaseLock("client5", "resource4"); err != nil {
		t.Fatalf("Proper ReleaseLock failed: %v", err)
	}
}

func TestLockTimeout(t *testing.T) {
	lm := NewLockManager()

	// Client7 acquires the lock on resource5 with a short timeout.
	if err := lm.AcquireLock("client7", "resource5", 1*time.Second); err != nil {
		t.Fatalf("AcquireLock failed: %v", err)
	}

	// Wait for the timeout to occur.
	time.Sleep(2 * time.Second)

	// Client8 should now be able to acquire the lock after auto-release.
	if err := lm.AcquireLock("client8", "resource5", 2*time.Second); err != nil {
		t.Fatalf("Lock not auto-released after timeout: %v", err)
	}
	if err := lm.ReleaseLock("client8", "resource5"); err != nil {
		t.Fatalf("ReleaseLock by client8 failed: %v", err)
	}
}

func TestConcurrentAcquisitions(t *testing.T) {
	lm := NewLockManager()
	const numClients = 10
	resource := "resource6"
	var acquiredClient string
	var mu sync.Mutex
	wg := sync.WaitGroup{}
	wg.Add(numClients)

	for i := 0; i < numClients; i++ {
		clientID := fmt.Sprintf("client_conc_%d", i)
		go func(cid string) {
			defer wg.Done()
			err := lm.AcquireLock(cid, resource, 3*time.Second)
			if err != nil {
				return
			}
			mu.Lock()
			if acquiredClient == "" {
				acquiredClient = cid
			}
			mu.Unlock()
			// Hold the lock for a short duration.
			time.Sleep(500 * time.Millisecond)
			_ = lm.ReleaseLock(cid, resource)
		}(clientID)
	}
	wg.Wait()

	if acquiredClient == "" {
		t.Fatal("No client was able to acquire the lock in concurrent acquisition test")
	}
}