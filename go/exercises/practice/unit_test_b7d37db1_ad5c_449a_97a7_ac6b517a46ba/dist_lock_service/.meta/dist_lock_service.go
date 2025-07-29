package dist_lock_service

import (
	"sync"
	"time"
)

type Lock struct {
	clientID    string
	expiresAt   time.Time
	reentryCount int
}

type DistLockService struct {
	mu    sync.RWMutex
	locks map[string]*Lock
}

func NewDistLockService() *DistLockService {
	return &DistLockService{
		locks: make(map[string]*Lock),
	}
}

func (s *DistLockService) AcquireLock(key string, clientID string, ttl time.Duration) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now()
	lock, exists := s.locks[key]

	if exists {
		if lock.clientID == clientID {
			// Reentrant lock
			lock.reentryCount++
			lock.expiresAt = now.Add(ttl)
			return true
		}
		if lock.expiresAt.After(now) {
			return false
		}
	}

	s.locks[key] = &Lock{
		clientID:    clientID,
		expiresAt:   now.Add(ttl),
		reentryCount: 0,
	}
	return true
}

func (s *DistLockService) ReleaseLock(key string, clientID string) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	lock, exists := s.locks[key]
	if !exists || lock.clientID != clientID {
		return false
	}

	if lock.reentryCount > 0 {
		lock.reentryCount--
		return true
	}

	delete(s.locks, key)
	return true
}

func (s *DistLockService) ExtendLock(key string, clientID string, newTTL time.Duration) bool {
	s.mu.Lock()
	defer s.mu.Unlock()

	lock, exists := s.locks[key]
	if !exists || lock.clientID != clientID {
		return false
	}

	lock.expiresAt = time.Now().Add(newTTL)
	return true
}

func (s *DistLockService) Status(key string) (bool, string) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	lock, exists := s.locks[key]
	if !exists || time.Now().After(lock.expiresAt) {
		return false, ""
	}
	return true, lock.clientID
}

func (s *DistLockService) cleanupExpiredLocks() {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now()
	for key, lock := range s.locks {
		if now.After(lock.expiresAt) {
			delete(s.locks, key)
		}
	}
}