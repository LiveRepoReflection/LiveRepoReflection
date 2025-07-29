package grpc_optimizations

import (
	"context"
	"errors"
	"sync"
	"time"
)

type UserProfile struct {
	ID   string
	Name string
}

type GRPCService interface {
	GetUserProfile(ctx context.Context, userIDs []string) (map[string]*UserProfile, error)
}

type ClientConfig struct {
	CacheSize     int
	CacheTTL      time.Duration
	MaxBatchSize  int
	MaxDelay      time.Duration
	MaxRetries    int
	RetryInterval time.Duration
}

type cacheEntry struct {
	profile *UserProfile
	expires time.Time
}

type GRPCClient struct {
	service GRPCService
	config  ClientConfig

	cache     map[string]cacheEntry
	cacheLRU  []string
	cacheMu   sync.RWMutex
	batchCh   chan batchRequest
	closeOnce sync.Once
	closed    chan struct{}
}

type batchRequest struct {
	userID   string
	respCh   chan batchResponse
	ctx      context.Context
	attempts int
}

type batchResponse struct {
	profile *UserProfile
	err     error
}

func NewGRPCClient(service GRPCService, config ClientConfig) *GRPCClient {
	if config.CacheSize <= 0 {
		config.CacheSize = 1000
	}
	if config.MaxBatchSize <= 0 {
		config.MaxBatchSize = 10
	}
	if config.MaxDelay <= 0 {
		config.MaxDelay = 50 * time.Millisecond
	}
	if config.MaxRetries <= 0 {
		config.MaxRetries = 3
	}
	if config.RetryInterval <= 0 {
		config.RetryInterval = time.Millisecond
	}

	client := &GRPCClient{
		service:  service,
		config:   config,
		cache:    make(map[string]cacheEntry),
		cacheLRU: make([]string, 0, config.CacheSize),
		batchCh:  make(chan batchRequest),
		closed:   make(chan struct{}),
	}

	go client.batchProcessor()
	return client
}

func (c *GRPCClient) Close() {
	c.closeOnce.Do(func() {
		close(c.closed)
	})
}

func (c *GRPCClient) GetUserProfile(ctx context.Context, userID string) (*UserProfile, error) {
	if userID == "" {
		return nil, errors.New("empty user ID")
	}

	// Check cache first
	if profile := c.checkCache(userID); profile != nil {
		return profile, nil
	}

	// Prepare for batching
	respCh := make(chan batchResponse, 1)
	req := batchRequest{
		userID: userID,
		respCh: respCh,
		ctx:    ctx,
	}

	// Send request to batch processor
	select {
	case c.batchCh <- req:
	case <-ctx.Done():
		return nil, ctx.Err()
	case <-c.closed:
		return nil, errors.New("client closed")
	}

	// Wait for response
	select {
	case resp := <-respCh:
		return resp.profile, resp.err
	case <-ctx.Done():
		return nil, ctx.Err()
	}
}

func (c *GRPCClient) checkCache(userID string) *UserProfile {
	c.cacheMu.RLock()
	defer c.cacheMu.RUnlock()

	if entry, exists := c.cache[userID]; exists {
		if time.Now().Before(entry.expires) {
			return entry.profile
		}
	}
	return nil
}

func (c *GRPCClient) updateCache(userID string, profile *UserProfile) {
	c.cacheMu.Lock()
	defer c.cacheMu.Unlock()

	// Remove oldest entry if cache is full
	if len(c.cache) >= c.config.CacheSize {
		oldestID := c.cacheLRU[0]
		delete(c.cache, oldestID)
		c.cacheLRU = c.cacheLRU[1:]
	}

	// Add new entry
	c.cache[userID] = cacheEntry{
		profile: profile,
		expires: time.Now().Add(c.config.CacheTTL),
	}
	c.cacheLRU = append(c.cacheLRU, userID)
}

func (c *GRPCClient) batchProcessor() {
	var batch []batchRequest
	timer := time.NewTimer(c.config.MaxDelay)
	defer timer.Stop()

	for {
		select {
		case req := <-c.batchCh:
			batch = append(batch, req)
			if len(batch) >= c.config.MaxBatchSize {
				c.processBatch(batch)
				batch = nil
				timer.Reset(c.config.MaxDelay)
			}
		case <-timer.C:
			if len(batch) > 0 {
				c.processBatch(batch)
				batch = nil
			}
			timer.Reset(c.config.MaxDelay)
		case <-c.closed:
			return
		}
	}
}

func (c *GRPCClient) processBatch(batch []batchRequest) {
	userIDs := make([]string, len(batch))
	for i, req := range batch {
		userIDs[i] = req.userID
	}

	profiles, err := c.service.GetUserProfile(context.Background(), userIDs)
	if err != nil {
		// Handle error for all requests in batch
		for _, req := range batch {
			if req.attempts < c.config.MaxRetries {
				// Retry the request
				req.attempts++
				go func(r batchRequest) {
					time.Sleep(c.config.RetryInterval * time.Duration(r.attempts))
					select {
					case c.batchCh <- r:
					case <-c.closed:
					}
				}(req)
			} else {
				req.respCh <- batchResponse{err: err}
			}
		}
		return
	}

	// Distribute results
	for _, req := range batch {
		if profile, ok := profiles[req.userID]; ok {
			c.updateCache(req.userID, profile)
			req.respCh <- batchResponse{profile: profile}
		} else {
			req.respCh <- batchResponse{err: errors.New("profile not found")}
		}
	}
}