package rate_limit_dist

import (
	"context"
	"sync"
	"time"
)

type inMemoryStore struct {
	mu      sync.RWMutex
	entries map[string]*entry
}

type entry struct {
	count     int
	limit     int
	expiresAt time.Time
}

func NewInMemoryStore() Store {
	return &inMemoryStore{
		entries: make(map[string]*entry),
	}
}

func (s *inMemoryStore) Increment(ctx context.Context, key string, window time.Duration) (int, error) {
	s.mu.Lock()
	defer s.mu.Unlock()

	now := time.Now()
	e, exists := s.entries[key]
	if !exists || now.After(e.expiresAt) {
		e = &entry{
			count:     0,
			expiresAt: now.Add(window),
		}
		s.entries[key] = e
	}

	e.count++
	return e.count, nil
}

func (s *inMemoryStore) GetCount(ctx context.Context, key string) (int, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	e, exists := s.entries[key]
	if !exists {
		return 0, nil
	}
	return e.count, nil
}

func (s *inMemoryStore) SetLimit(ctx context.Context, key string, limit int, window time.Duration) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	e, exists := s.entries[key]
	if !exists {
		e = &entry{
			expiresAt: time.Now().Add(window),
		}
		s.entries[key] = e
	}
	e.limit = limit
	e.expiresAt = time.Now().Add(window)
	return nil
}

func (s *inMemoryStore) GetLimit(ctx context.Context, key string) (int, time.Duration, error) {
	s.mu.RLock()
	defer s.mu.RUnlock()

	e, exists := s.entries[key]
	if !exists {
		return 0, 0, nil
	}
	return e.limit, time.Until(e.expiresAt), nil
}

func (s *inMemoryStore) Reset(ctx context.Context, key string) error {
	s.mu.Lock()
	defer s.mu.Unlock()

	delete(s.entries, key)
	return nil
}