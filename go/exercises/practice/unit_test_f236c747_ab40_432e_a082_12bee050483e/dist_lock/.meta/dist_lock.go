package distlock

import (
	"errors"
	"sync"
	"time"
)

var (
	errLockNotHeld = errors.New("lock not held")
	errInvalidLease = errors.New("invalid lease duration")
)

type lockInfo struct {
	holder    string
	expiresAt time.Time
}

type DistLock struct {
	locks      map[string]*lockInfo
	mu         sync.RWMutex
	instanceID string
}

func NewDistLock() *DistLock {
	return &DistLock{
		locks:      make(map[string]*lockInfo),
		instanceID: generateInstanceID(),
	}
}

func generateInstanceID() string {
	return time.Now().Format("20060102150405.000000000")
}

func (dl *DistLock) AcquireLock(resourceID string, leaseDuration time.Duration) (bool, error) {
	if leaseDuration <= 0 {
		return false, errInvalidLease
	}

	dl.mu.Lock()
	defer dl.mu.Unlock()

	now := time.Now()
	if info, exists := dl.locks[resourceID]; exists {
		if now.Before(info.expiresAt) {
			return false, nil
		}
	}

	dl.locks[resourceID] = &lockInfo{
		holder:    dl.instanceID,
		expiresAt: now.Add(leaseDuration),
	}

	go dl.scheduleCleanup(resourceID, leaseDuration)
	return true, nil
}

func (dl *DistLock) ReleaseLock(resourceID string) error {
	dl.mu.Lock()
	defer dl.mu.Unlock()

	info, exists := dl.locks[resourceID]
	if !exists || info.holder != dl.instanceID {
		return errLockNotHeld
	}

	delete(dl.locks, resourceID)
	return nil
}

func (dl *DistLock) ExtendLock(resourceID string, newLeaseDuration time.Duration) (bool, error) {
	if newLeaseDuration <= 0 {
		return false, errInvalidLease
	}

	dl.mu.Lock()
	defer dl.mu.Unlock()

	info, exists := dl.locks[resourceID]
	if !exists || info.holder != dl.instanceID {
		return false, nil
	}

	now := time.Now()
	if now.After(info.expiresAt) {
		delete(dl.locks, resourceID)
		return false, nil
	}

	info.expiresAt = now.Add(newLeaseDuration)
	go dl.scheduleCleanup(resourceID, newLeaseDuration)
	return true, nil
}

func (dl *DistLock) scheduleCleanup(resourceID string, duration time.Duration) {
	time.Sleep(duration)
	
	dl.mu.Lock()
	defer dl.mu.Unlock()

	info, exists := dl.locks[resourceID]
	if !exists {
		return
	}

	if time.Now().After(info.expiresAt) {
		delete(dl.locks, resourceID)
	}
}

// Additional helper methods for monitoring and debugging

func (dl *DistLock) GetLockStatus(resourceID string) (bool, time.Time, error) {
	dl.mu.RLock()
	defer dl.mu.RUnlock()

	info, exists := dl.locks[resourceID]
	if !exists {
		return false, time.Time{}, nil
	}

	return true, info.expiresAt, nil
}

func (dl *DistLock) GetActiveLocks() []string {
	dl.mu.RLock()
	defer dl.mu.RUnlock()

	activeResources := make([]string, 0, len(dl.locks))
	now := time.Now()

	for resourceID, info := range dl.locks {
		if now.Before(info.expiresAt) {
			activeResources = append(activeResources, resourceID)
		}
	}

	return activeResources
}

func (dl *DistLock) cleanup() {
	dl.mu.Lock()
	defer dl.mu.Unlock()

	now := time.Now()
	for resourceID, info := range dl.locks {
		if now.After(info.expiresAt) {
			delete(dl.locks, resourceID)
		}
	}
}