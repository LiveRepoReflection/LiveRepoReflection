package dynamic_rate_limit

import (
	"errors"
	"sync"
	"time"
)

type ClientLimit struct {
	Limit     int
	Window    int
	Count     int
	ResetTime time.Time
	mu        sync.Mutex
}

type RateLimiter struct {
	clients map[string]*ClientLimit
	mu      sync.RWMutex
}

func NewRateLimiter() *RateLimiter {
	return &RateLimiter{
		clients: make(map[string]*ClientLimit),
	}
}

func (rl *RateLimiter) Allow(clientID string, requestCost int) bool {
	if clientID == "" || requestCost <= 0 {
		return false
	}

	rl.mu.RLock()
	client, exists := rl.clients[clientID]
	rl.mu.RUnlock()

	if !exists {
		return true // No rate limit set for this client
	}

	client.mu.Lock()
	defer client.mu.Unlock()

	now := time.Now()
	if now.After(client.ResetTime) {
		client.Count = 0
		client.ResetTime = now.Add(time.Duration(client.Window) * time.Second)
	}

	if client.Count+requestCost > client.Limit {
		return false
	}

	client.Count += requestCost
	return true
}

func (rl *RateLimiter) SetRateLimit(clientID string, limit int, window int) error {
	if limit <= 0 {
		return errors.New("limit must be positive")
	}
	if window <= 0 {
		return errors.New("window must be positive")
	}

	rl.mu.Lock()
	defer rl.mu.Unlock()

	if _, exists := rl.clients[clientID]; !exists {
		rl.clients[clientID] = &ClientLimit{
			Limit:     limit,
			Window:    window,
			ResetTime: time.Now().Add(time.Duration(window) * time.Second),
		}
		return nil
	}

	client := rl.clients[clientID]
	client.mu.Lock()
	defer client.mu.Unlock()

	client.Limit = limit
	client.Window = window
	return nil
}

func (rl *RateLimiter) GetRateLimit(clientID string) (limit int, window int, err error) {
	rl.mu.RLock()
	defer rl.mu.RUnlock()

	client, exists := rl.clients[clientID]
	if !exists {
		return 0, 0, nil
	}

	client.mu.Lock()
	defer client.mu.Unlock()

	return client.Limit, client.Window, nil
}