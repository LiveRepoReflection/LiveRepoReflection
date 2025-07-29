package ratelimit

import (
	"container/list"
	"sync"
	"time"
)

type timeWindow struct {
	mu        sync.Mutex
	requests  *list.List
	duration  time.Duration
	maxCount  int
}

func newTimeWindow(duration time.Duration, maxCount int) *timeWindow {
	return &timeWindow{
		requests: list.New(),
		duration: duration,
		maxCount: maxCount,
	}
}

func (w *timeWindow) tryAcquire() bool {
	w.mu.Lock()
	defer w.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-w.duration)

	// Remove expired entries
	for e := w.requests.Front(); e != nil; {
		if timestamp := e.Value.(time.Time); timestamp.Before(windowStart) {
			next := e.Next()
			w.requests.Remove(e)
			e = next
		} else {
			break
		}
	}

	// Check if we can add a new request
	if w.requests.Len() >= w.maxCount {
		return false
	}

	w.requests.PushBack(now)
	return true
}

func (w *timeWindow) count() int {
	w.mu.Lock()
	defer w.mu.Unlock()

	now := time.Now()
	windowStart := now.Add(-w.duration)
	count := 0

	for e := w.requests.Front(); e != nil; e = e.Next() {
		if timestamp := e.Value.(time.Time); timestamp.After(windowStart) {
			count++
		}
	}

	return count
}