package lock_manager

import (
	"sync"
	"time"
)

type Lock struct {
	clientID      string
	expiration    time.Time
	reentryCount  int
}

type LockManager struct {
	locks    map[string]*Lock
	mutex    sync.RWMutex
	stopChan chan struct{}
}

func NewLockManager() *LockManager {
	lm := &LockManager{
		locks:    make(map[string]*Lock),
		stopChan: make(chan struct{}),
	}
	go lm.cleanupExpiredLocks()
	return lm
}

func (lm *LockManager) AcquireLock(resourceID string, clientID string, leaseDuration time.Duration) bool {
	lm.mutex.Lock()
	defer lm.mutex.Unlock()

	now := time.Now()
	expiration := now.Add(leaseDuration)

	if existingLock, exists := lm.locks[resourceID]; exists {
		if existingLock.clientID == clientID {
			// Reentrant lock
			existingLock.reentryCount++
			existingLock.expiration = expiration
			return true
		}
		if existingLock.expiration.After(now) {
			return false
		}
	}

	lm.locks[resourceID] = &Lock{
		clientID:     clientID,
		expiration:   expiration,
		reentryCount: 1,
	}
	return true
}

func (lm *LockManager) ReleaseLock(resourceID string, clientID string) bool {
	lm.mutex.Lock()
	defer lm.mutex.Unlock()

	lock, exists := lm.locks[resourceID]
	if !exists || lock.clientID != clientID {
		return false
	}

	lock.reentryCount--
	if lock.reentryCount <= 0 {
		delete(lm.locks, resourceID)
	}
	return true
}

func (lm *LockManager) ExtendLock(resourceID string, clientID string, newLeaseDuration time.Duration) bool {
	lm.mutex.Lock()
	defer lm.mutex.Unlock()

	lock, exists := lm.locks[resourceID]
	if !exists || lock.clientID != clientID {
		return false
	}

	lock.expiration = time.Now().Add(newLeaseDuration)
	return true
}

func (lm *LockManager) cleanupExpiredLocks() {
	ticker := time.NewTicker(1 * time.Second)
	defer ticker.Stop()

	for {
		select {
		case <-ticker.C:
			lm.mutex.Lock()
			now := time.Now()
			for resourceID, lock := range lm.locks {
				if lock.expiration.Before(now) {
					delete(lm.locks, resourceID)
				}
			}
			lm.mutex.Unlock()
		case <-lm.stopChan:
			return
		}
	}
}

func (lm *LockManager) Stop() {
	close(lm.stopChan)
}