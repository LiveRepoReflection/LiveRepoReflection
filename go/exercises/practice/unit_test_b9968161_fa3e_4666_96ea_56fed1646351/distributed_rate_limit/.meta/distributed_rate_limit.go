package distributed_rate_limit

import (
	"errors"
	"os"
	"sync"
	"time"
)

type redisEntry struct {
	count     int
	expiresAt time.Time
}

var (
	redisStore = make(map[string]redisEntry)
	storeMutex sync.Mutex
)

// AllowRequest checks if a request from the given user should be allowed.
// It simulates Redis operations with an in-memory store and uses the environment
// variable "REDIS_ADDR" to simulate connection errors. The rate limiter allows
// at most N requests per T-second window per user. A call with T==0 flushes the user's key.
func AllowRequest(userID string, N int, T int) (bool, error) {
	redisAddr := os.Getenv("REDIS_ADDR")
	if redisAddr == "" {
		redisAddr = "127.0.0.1:6379"
	}
	if redisAddr != "127.0.0.1:6379" {
		return false, errors.New("Redis connection error")
	}
	if userID == "" {
		return false, nil
	}
	key := "rl:" + userID

	// If T==0, flush the key.
	if T == 0 {
		storeMutex.Lock()
		delete(redisStore, key)
		storeMutex.Unlock()
		return false, nil
	}

	// If N is 0, always disallow requests.
	if N == 0 {
		storeMutex.Lock()
		delete(redisStore, key)
		storeMutex.Unlock()
		return false, nil
	}

	now := time.Now()

	storeMutex.Lock()
	defer storeMutex.Unlock()

	entry, exists := redisStore[key]
	if exists && now.After(entry.expiresAt) {
		// The key has expired, remove it.
		delete(redisStore, key)
		exists = false
	}
	if !exists {
		redisStore[key] = redisEntry{
			count:     1,
			expiresAt: now.Add(time.Duration(T) * time.Second),
		}
		return true, nil
	} else {
		if entry.count >= N {
			return false, nil
		}
		entry.count++
		redisStore[key] = entry
		return true, nil
	}
}