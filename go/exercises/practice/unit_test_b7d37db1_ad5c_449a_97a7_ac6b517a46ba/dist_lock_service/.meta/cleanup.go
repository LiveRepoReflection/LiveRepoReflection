package dist_lock_service

import (
	"time"
)

func (s *DistLockService) StartCleanupRoutine(interval time.Duration) {
	ticker := time.NewTicker(interval)
	go func() {
		for range ticker.C {
			s.cleanupExpiredLocks()
		}
	}()
}