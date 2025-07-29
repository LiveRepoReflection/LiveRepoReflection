package ratelimiter

import (
	"errors"
	"sync"
	"time"
)

type RateLimiter interface {
	SetClientLimit(clientID string, limit int) error
	SetResourceWeight(resourceID string, weight int) error
	Allow(clientID string, resourceID string) (bool, error)
	ResetClient(clientID string)
}

type rateLimiter struct {
	windowDuration time.Duration
	evictionTime   time.Duration
	clients        map[string]*clientData
	resources      map[string]int
	mu             sync.RWMutex
	cleanupTicker  *time.Ticker
}

type clientData struct {
	limit      int
	used       int
	accessTime time.Time
	requests   []requestEntry
	mu         sync.Mutex
}

type requestEntry struct {
	weight    int
	timestamp time.Time
}

func InitializeRateLimiter(window, eviction int) RateLimiter {
	rl := &rateLimiter{
		windowDuration: time.Duration(window) * time.Second,
		evictionTime:   time.Duration(eviction) * time.Second,
		clients:        make(map[string]*clientData),
		resources:      make(map[string]int),
	}

	rl.cleanupTicker = time.NewTicker(1 * time.Minute)
	go rl.cleanupExpiredClients()

	return rl
}

func (rl *rateLimiter) SetClientLimit(clientID string, limit int) error {
	if limit <= 0 {
		return errors.New("limit must be positive")
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	if _, exists := rl.clients[clientID]; !exists {
		rl.clients[clientID] = &clientData{
			limit: limit,
		}
	} else {
		rl.clients[clientID].limit = limit
	}

	return nil
}

func (rl *rateLimiter) SetResourceWeight(resourceID string, weight int) error {
	if weight <= 0 {
		return errors.New("weight must be positive")
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	rl.resources[resourceID] = weight
	return nil
}

func (rl *rateLimiter) Allow(clientID string, resourceID string) (bool, error) {
	rl.mu.RLock()
	client, clientExists := rl.clients[clientID]
	weight, resourceExists := rl.resources[resourceID]
	rl.mu.RUnlock()

	if !clientExists {
		return false, errors.New("client does not exist")
	}
	if !resourceExists {
		return false, errors.New("resource does not exist")
	}

	client.mu.Lock()
	defer client.mu.Unlock()

	now := time.Now()
	client.accessTime = now

	// Clean up old requests
	cutoff := now.Add(-rl.windowDuration)
	var validRequests []requestEntry
	currentUsed := 0

	for _, req := range client.requests {
		if req.timestamp.After(cutoff) {
			validRequests = append(validRequests, req)
			currentUsed += req.weight
		}
	}

	client.requests = validRequests
	client.used = currentUsed

	if client.used+weight > client.limit {
		return false, nil
	}

	client.requests = append(client.requests, requestEntry{
		weight:    weight,
		timestamp: now,
	})
	client.used += weight

	return true, nil
}

func (rl *rateLimiter) ResetClient(clientID string) {
	rl.mu.Lock()
	defer rl.mu.Unlock()

	if client, exists := rl.clients[clientID]; exists {
		client.mu.Lock()
		defer client.mu.Unlock()
		client.used = 0
		client.requests = nil
	}
}

func (rl *rateLimiter) cleanupExpiredClients() {
	for range rl.cleanupTicker.C {
		rl.mu.Lock()
		now := time.Now()
		for id, client := range rl.clients {
			client.mu.Lock()
			if now.Sub(client.accessTime) > rl.evictionTime {
				delete(rl.clients, id)
			}
			client.mu.Unlock()
		}
		rl.mu.Unlock()
	}
}