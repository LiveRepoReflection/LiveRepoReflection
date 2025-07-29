package weighted_limiter

import (
	"errors"
	"sync"
	"time"
)

// BucketTier represents configuration for a single rate limiting tier
type BucketTier struct {
	Capacity   int     // Maximum capacity of the bucket
	RefillRate int     // Tokens added per second
	current    float64 // Current number of tokens
	lastRefill time.Time
}

// Client represents the state of a single client's rate limiting buckets
type Client struct {
	tiers []BucketTier
	mu    sync.Mutex
	lastAccess time.Time
}

// RateLimiter implements the weighted bucket rate limiting algorithm
type RateLimiter struct {
	tiers        []BucketTier
	clients      map[string]*Client
	mu           sync.RWMutex
	cleanupTimer *time.Timer
}

// NewRateLimiter creates a new rate limiter with the specified bucket tiers
func NewRateLimiter(tiers []BucketTier) (*RateLimiter, error) {
	if err := validateTiers(tiers); err != nil {
		return nil, err
	}

	limiter := &RateLimiter{
		tiers:   tiers,
		clients: make(map[string]*Client),
	}

	// Start cleanup goroutine
	limiter.startCleanup()

	return limiter, nil
}

func validateTiers(tiers []BucketTier) error {
	if len(tiers) == 0 {
		return errors.New("at least one tier must be specified")
	}
	if len(tiers) > 10 {
		return errors.New("maximum 10 tiers allowed")
	}

	for i, tier := range tiers {
		if tier.Capacity <= 0 {
			return errors.New("tier capacity must be positive")
		}
		if tier.RefillRate <= 0 {
			return errors.New("tier refill rate must be positive")
		}
		if i > 0 && tier.Capacity <= tiers[i-1].Capacity {
			return errors.New("tier capacities must be strictly increasing")
		}
	}

	return nil
}

// AllowRequest checks if a request with given weight is allowed for the specified client
func (rl *RateLimiter) AllowRequest(clientID string, weight int) bool {
	if weight <= 0 || weight > 10000 || clientID == "" {
		return false
	}

	rl.mu.Lock()
	client, exists := rl.clients[clientID]
	if !exists {
		client = rl.createNewClient()
		rl.clients[clientID] = client
	}
	rl.mu.Unlock()

	return client.tryConsume(weight)
}

func (rl *RateLimiter) createNewClient() *Client {
	tiers := make([]BucketTier, len(rl.tiers))
	now := time.Now()
	
	for i, tier := range rl.tiers {
		tiers[i] = BucketTier{
			Capacity:   tier.Capacity,
			RefillRate: tier.RefillRate,
			current:    float64(tier.Capacity),
			lastRefill: now,
		}
	}

	return &Client{
		tiers:      tiers,
		lastAccess: now,
	}
}

func (c *Client) tryConsume(weight int) bool {
	c.mu.Lock()
	defer c.mu.Unlock()

	now := time.Now()
	remainingWeight := weight

	// Refill all tiers
	for i := range c.tiers {
		c.refillTier(&c.tiers[i], now)
	}

	// Try to consume from each tier
	for i := range c.tiers {
		if remainingWeight <= 0 {
			break
		}

		available := int(c.tiers[i].current)
		if available > remainingWeight {
			c.tiers[i].current -= float64(remainingWeight)
			remainingWeight = 0
		} else {
			c.tiers[i].current = 0
			remainingWeight -= available
		}
	}

	c.lastAccess = now
	return remainingWeight == 0
}

func (c *Client) refillTier(tier *BucketTier, now time.Time) {
	elapsed := now.Sub(tier.lastRefill).Seconds()
	tier.current += float64(tier.RefillRate) * elapsed
	if tier.current > float64(tier.Capacity) {
		tier.current = float64(tier.Capacity)
	}
	tier.lastRefill = now
}

func (rl *RateLimiter) startCleanup() {
	const cleanupInterval = 1 * time.Hour
	const clientTimeout = 24 * time.Hour

	go func() {
		ticker := time.NewTicker(cleanupInterval)
		defer ticker.Stop()

		for range ticker.C {
			rl.mu.Lock()
			now := time.Now()
			
			for clientID, client := range rl.clients {
				if now.Sub(client.lastAccess) > clientTimeout {
					delete(rl.clients, clientID)
				}
			}
			
			rl.mu.Unlock()
		}
	}()
}