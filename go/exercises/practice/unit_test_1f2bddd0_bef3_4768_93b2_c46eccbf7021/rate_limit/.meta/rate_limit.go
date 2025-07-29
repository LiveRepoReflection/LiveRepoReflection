package rate_limit

import (
	"errors"
	"sync"
	"time"
)

var (
	ErrClosed       = errors.New("rate limiter is closed")
	ErrNotSupported = errors.New("storage type not supported")
)

type RateLimiterConfig struct {
	Limit          int
	Window         time.Duration
	StorageType    string
	StorageAddress string
}

type counter struct {
	count int
	start time.Time
}

type RateLimiter struct {
	config   RateLimiterConfig
	counters map[string]*counter
	mutex    sync.Mutex
	closed   bool
}

func NewRateLimiter(config RateLimiterConfig) (*RateLimiter, error) {
	if config.Limit <= 0 || config.Window <= 0 {
		return nil, errors.New("invalid configuration: Limit and Window must be positive")
	}

	if config.StorageType != "inmemory" {
		return nil, ErrNotSupported
	}

	rl := &RateLimiter{
		config:   config,
		counters: make(map[string]*counter),
		closed:   false,
	}
	return rl, nil
}

func (rl *RateLimiter) Allow(key string) (bool, error) {
	rl.mutex.Lock()
	defer rl.mutex.Unlock()

	if rl.closed {
		return false, ErrClosed
	}

	now := time.Now()
	cnt, exists := rl.counters[key]
	if !exists || now.Sub(cnt.start) >= rl.config.Window {
		cnt = &counter{
			count: 0,
			start: now,
		}
		rl.counters[key] = cnt
	}

	if cnt.count < rl.config.Limit {
		cnt.count++
		return true, nil
	}
	return false, nil
}

func (rl *RateLimiter) Reset(key string) error {
	rl.mutex.Lock()
	defer rl.mutex.Unlock()

	if rl.closed {
		return ErrClosed
	}

	delete(rl.counters, key)
	return nil
}

func (rl *RateLimiter) Close() error {
	rl.mutex.Lock()
	defer rl.mutex.Unlock()

	if rl.closed {
		return ErrClosed
	}

	rl.closed = true
	rl.counters = nil
	return nil
}