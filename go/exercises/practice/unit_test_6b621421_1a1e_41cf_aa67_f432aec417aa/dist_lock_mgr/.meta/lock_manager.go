package dist_lock_mgr

import (
	"errors"
	"sync"
	"time"
)

type waitingRequest struct {
	client string
	lease  time.Duration
	notify chan error
}

type LockEntry struct {
	owner       string
	reentrancy  int
	lease       time.Duration
	expiration  time.Time
	timer       *time.Timer
	waiting     []waitingRequest
}

type LockManager struct {
	mu    sync.Mutex
	locks map[string]*LockEntry
}

// NewLockManager creates a new instance of LockManager.
func NewLockManager() *LockManager {
	return &LockManager{
		locks: make(map[string]*LockEntry),
	}
}

// AcquireLock tries to acquire the lock on a resource for a given client with a lease duration.
// If the resource is already locked by the same client, it supports reentrancy.
// If the resource is locked by another client, this call will block until the lock is released.
func (lm *LockManager) AcquireLock(client, resource string, lease time.Duration) error {
	lm.mu.Lock()
	// If the resource is not locked, create a new lock entry.
	if entry, exists := lm.locks[resource]; !exists {
		newEntry := &LockEntry{
			owner:      client,
			reentrancy: 1,
			lease:      lease,
			expiration: time.Now().Add(lease),
			waiting:    []waitingRequest{},
		}
		newEntry.timer = time.AfterFunc(lease, func() {
			lm.expireLock(resource)
		})
		lm.locks[resource] = newEntry
		lm.mu.Unlock()
		return nil
	} else {
		// If the same client already holds the lock, allow reentrancy.
		if entry.owner == client {
			entry.reentrancy++
			entry.lease = lease
			entry.expiration = time.Now().Add(lease)
			// Reset the timer.
			if entry.timer != nil {
				entry.timer.Stop()
			}
			entry.timer = time.AfterFunc(lease, func() {
				lm.expireLock(resource)
			})
			lm.mu.Unlock()
			return nil
		}
		// The resource is held by another client; queue this request.
		req := waitingRequest{
			client: client,
			lease:  lease,
			notify: make(chan error, 1),
		}
		entry.waiting = append(entry.waiting, req)
		lm.mu.Unlock()

		// Wait until notified that the lock is granted.
		err := <-req.notify
		return err
	}
}

// ReleaseLock releases the lock on a resource held by a given client.
// It returns an error if the client does not hold the lock.
func (lm *LockManager) ReleaseLock(client, resource string) error {
	lm.mu.Lock()
	entry, exists := lm.locks[resource]
	if !exists {
		lm.mu.Unlock()
		return errors.New("lock not held")
	}
	if entry.owner != client {
		lm.mu.Unlock()
		return errors.New("client does not hold the lock")
	}
	// Handle reentrant locks: only fully release when count reaches zero.
	entry.reentrancy--
	if entry.reentrancy > 0 {
		// Update expiration since the client is still holding the lock.
		entry.expiration = time.Now().Add(entry.lease)
		if entry.timer != nil {
			entry.timer.Stop()
		}
		entry.timer = time.AfterFunc(entry.lease, func() {
			lm.expireLock(resource)
		})
		lm.mu.Unlock()
		return nil
	}
	// Fully release the lock.
	if entry.timer != nil {
		entry.timer.Stop()
	}
	// Assign the lock to the next waiting client if available.
	if len(entry.waiting) > 0 {
		nextReq := entry.waiting[0]
		entry.waiting = entry.waiting[1:]
		entry.owner = nextReq.client
		entry.reentrancy = 1
		entry.lease = nextReq.lease
		entry.expiration = time.Now().Add(nextReq.lease)
		entry.timer = time.AfterFunc(nextReq.lease, func() {
			lm.expireLock(resource)
		})
		// Notify the next waiting request that the lock has been acquired.
		nextReq.notify <- nil
		lm.mu.Unlock()
		return nil
	}
	// No waiting requests; remove the lock entry.
	delete(lm.locks, resource)
	lm.mu.Unlock()
	return nil
}

// expireLock is called when a lock's lease expires.
// It auto-releases the lock and grants it to the next waiting request if available.
func (lm *LockManager) expireLock(resource string) {
	lm.mu.Lock()
	entry, exists := lm.locks[resource]
	if !exists {
		lm.mu.Unlock()
		return
	}
	// Check if the lock has indeed expired.
	if time.Now().Before(entry.expiration) {
		lm.mu.Unlock()
		return
	}
	// Stop the timer.
	if entry.timer != nil {
		entry.timer.Stop()
	}
	// Auto-release the lock regardless of reentrancy count.
	// Notify the current owner indirectly by simply expiring the lock.
	// Assign the lock to the next waiting client if present.
	if len(entry.waiting) > 0 {
		nextReq := entry.waiting[0]
		entry.waiting = entry.waiting[1:]
		entry.owner = nextReq.client
		entry.reentrancy = 1
		entry.lease = nextReq.lease
		entry.expiration = time.Now().Add(nextReq.lease)
		entry.timer = time.AfterFunc(nextReq.lease, func() {
			lm.expireLock(resource)
		})
		// Notify the next waiting client.
		nextReq.notify <- nil
		lm.mu.Unlock()
		return
	}
	// No waiting requests; remove the lock entry.
	delete(lm.locks, resource)
	lm.mu.Unlock()
}