// Package tenant_limiter provides functionality for rate limiting requests on a per-tenant basis.
package tenant_limiter

import (
	"container/list"
	"sync"
	"time"
)

// Constants for default values and limits
const (
	defaultCacheSize  = 10000 // Default LRU cache size
	persistenceWindow = 5     // Seconds to wait before persisting to storage
	maxRequestsToLog  = 10000 // Maximum number of requests to log per tenant
)

// RequestLog represents a log of requests with timestamps for a sliding window
type RequestLog struct {
	requests    *list.List     // Linked list of request timestamps
	windowStart time.Time      // Start time of current window
	mutex       sync.Mutex     // Mutex for thread safety
	lastPersist time.Time      // Last time this tenant's data was persisted
	dirty       bool           // Whether this tenant's data has changed since last persistence
}

// tokenBucketState represents the state for a token bucket rate limiter
type tokenBucketState struct {
	tokens        float64   // Current number of tokens in the bucket
	lastRefill    time.Time // Last time tokens were refilled
	refillRate    float64   // Rate at which tokens are refilled (tokens per second)
	maxTokens     float64   // Maximum number of tokens the bucket can hold
	mutex         sync.Mutex
	lastPersist   time.Time
	dirty         bool
}

// LRUCache implements a thread-safe Least Recently Used cache
type LRUCache struct {
	capacity int
	items    map[string]*list.Element
	list     *list.List
	mutex    sync.RWMutex
}

// cacheItem is a key-value pair stored in the LRU cache
type cacheItem struct {
	key   string
	value interface{}
}

// slidingWindowLimiter implements a sliding window rate limiter
type slidingWindowLimiter struct {
	cache   *LRUCache
	storage *mockStorage
	mutex   sync.RWMutex
}

// tokenBucketLimiter implements a token bucket rate limiter
type tokenBucketLimiter struct {
	cache   *LRUCache
	storage *mockStorage
	mutex   sync.RWMutex
}

// mockStorage simulates an external persistent storage
type mockStorage struct {
	data  map[string]interface{}
	mutex sync.RWMutex
}

// global limiter instance
var (
	// Using sliding window limiter for better accuracy
	limiter *slidingWindowLimiter
	once    sync.Once
)

// initLimiter initializes the global rate limiter
func initLimiter() {
	once.Do(func() {
		limiter = &slidingWindowLimiter{
			cache:   newLRUCache(defaultCacheSize),
			storage: newMockStorage(),
		}
	})
}

// newLRUCache creates a new LRU cache with the given capacity
func newLRUCache(capacity int) *LRUCache {
	return &LRUCache{
		capacity: capacity,
		items:    make(map[string]*list.Element),
		list:     list.New(),
	}
}

// Get retrieves a value from the cache
func (c *LRUCache) Get(key string) (interface{}, bool) {
	c.mutex.RLock()
	element, exists := c.items[key]
	c.mutex.RUnlock()

	if !exists {
		return nil, false
	}

	c.mutex.Lock()
	defer c.mutex.Unlock()
	
	// Move to front (most recently used)
	c.list.MoveToFront(element)
	return element.Value.(*cacheItem).value, true
}

// Set adds or updates a value in the cache
func (c *LRUCache) Set(key string, value interface{}) {
	c.mutex.Lock()
	defer c.mutex.Unlock()

	// If key already exists, update its value and move to front
	if element, exists := c.items[key]; exists {
		c.list.MoveToFront(element)
		element.Value.(*cacheItem).value = value
		return
	}

	// Add new item to the front
	element := c.list.PushFront(&cacheItem{
		key:   key,
		value: value,
	})
	c.items[key] = element

	// Evict least recently used if capacity is exceeded
	if c.list.Len() > c.capacity {
		oldest := c.list.Back()
		if oldest != nil {
			c.removeElement(oldest)
		}
	}
}

// removeElement removes an element from the cache
func (c *LRUCache) removeElement(element *list.Element) {
	c.list.Remove(element)
	delete(c.items, element.Value.(*cacheItem).value.(*cacheItem).key)
}

// newMockStorage creates a new mock storage
func newMockStorage() *mockStorage {
	return &mockStorage{
		data: make(map[string]interface{}),
	}
}

// Get retrieves a value from storage
func (s *mockStorage) Get(key string) (interface{}, bool) {
	s.mutex.RLock()
	defer s.mutex.RUnlock()
	value, exists := s.data[key]
	return value, exists
}

// Set adds or updates a value in storage
func (s *mockStorage) Set(key string, value interface{}) {
	s.mutex.Lock()
	defer s.mutex.Unlock()
	s.data[key] = value
}

// newRequestLog creates a new request log
func newRequestLog() *RequestLog {
	return &RequestLog{
		requests:    list.New(),
		windowStart: time.Now(),
		lastPersist: time.Now(),
	}
}

// addRequest adds a new request to the log
func (r *RequestLog) addRequest(now time.Time, window int) {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	// Add new request
	r.requests.PushBack(now)
	r.dirty = true

	// Cleanup old requests
	windowSeconds := time.Duration(window) * time.Second
	cutoff := now.Add(-windowSeconds)
	
	for r.requests.Len() > 0 {
		oldest := r.requests.Front()
		ts := oldest.Value.(time.Time)
		if ts.Before(cutoff) {
			r.requests.Remove(oldest)
		} else {
			break
		}
	}

	// Cap the maximum number of requests to prevent memory overflow
	for r.requests.Len() > maxRequestsToLog {
		r.requests.Remove(r.requests.Front())
	}
}

// countRequests counts the number of requests within the window
func (r *RequestLog) countRequests(now time.Time, window int) int {
	r.mutex.Lock()
	defer r.mutex.Unlock()

	windowSeconds := time.Duration(window) * time.Second
	cutoff := now.Add(-windowSeconds)
	
	count := 0
	for e := r.requests.Front(); e != nil; e = e.Next() {
		ts := e.Value.(time.Time)
		if !ts.Before(cutoff) {
			count++
		}
	}
	
	return count
}

// newTokenBucketState creates a new token bucket state
func newTokenBucketState(rateLimit, window int) *tokenBucketState {
	tokens := float64(rateLimit)
	refillRate := float64(rateLimit) / float64(window)
	
	return &tokenBucketState{
		tokens:      tokens,
		maxTokens:   tokens,
		refillRate:  refillRate,
		lastRefill:  time.Now(),
		lastPersist: time.Now(),
	}
}

// consumeToken attempts to consume a token from the bucket
func (t *tokenBucketState) consumeToken() bool {
	t.mutex.Lock()
	defer t.mutex.Unlock()
	
	now := time.Now()
	elapsed := now.Sub(t.lastRefill).Seconds()
	
	// Refill tokens based on elapsed time
	t.tokens += elapsed * t.refillRate
	if t.tokens > t.maxTokens {
		t.tokens = t.maxTokens
	}
	
	t.lastRefill = now
	
	// Try to consume a token
	if t.tokens >= 1.0 {
		t.tokens--
		t.dirty = true
		return true
	}
	
	return false
}

// getAllowSlidingWindow implements the Allow function using sliding window algorithm
func (l *slidingWindowLimiter) getAllowSlidingWindow(tenantID string, rateLimit int, window int) bool {
	// Validate input parameters
	if rateLimit <= 0 || window <= 0 {
		return false
	}

	now := time.Now()
	cacheKey := tenantID

	// Try to get tenant data from cache
	var log *RequestLog
	cached, found := l.cache.Get(cacheKey)
	if found {
		log = cached.(*RequestLog)
	} else {
		// Try to get from storage
		l.mutex.Lock()
		storedData, found := l.storage.Get(cacheKey)
		if found {
			log = storedData.(*RequestLog)
		} else {
			// Create new log if not found
			log = newRequestLog()
		}
		l.mutex.Unlock()
		
		// Add to cache
		l.cache.Set(cacheKey, log)
	}

	// Check if request is allowed
	currentCount := log.countRequests(now, window)
	if currentCount >= rateLimit {
		return false
	}

	// Add request to log
	log.addRequest(now, window)

	// Periodically persist to storage
	if now.Sub(log.lastPersist) > persistenceWindow*time.Second && log.dirty {
		go func(tenant string, logCopy *RequestLog) {
			l.mutex.Lock()
			defer l.mutex.Unlock()
			l.storage.Set(tenant, logCopy)
			logCopy.lastPersist = now
			logCopy.dirty = false
		}(tenantID, log)
	}

	return true
}

// getAllowTokenBucket implements the Allow function using token bucket algorithm
func (l *tokenBucketLimiter) getAllowTokenBucket(tenantID string, rateLimit int, window int) bool {
	// Validate input parameters
	if rateLimit <= 0 || window <= 0 {
		return false
	}

	now := time.Now()
	cacheKey := tenantID

	// Try to get tenant data from cache
	var bucket *tokenBucketState
	cached, found := l.cache.Get(cacheKey)
	if found {
		bucket = cached.(*tokenBucketState)
	} else {
		// Try to get from storage
		l.mutex.Lock()
		storedData, found := l.storage.Get(cacheKey)
		if found {
			bucket = storedData.(*tokenBucketState)
		} else {
			// Create new bucket if not found
			bucket = newTokenBucketState(rateLimit, window)
		}
		l.mutex.Unlock()
		
		// Add to cache
		l.cache.Set(cacheKey, bucket)
	}

	// Try to consume a token
	allowed := bucket.consumeToken()

	// Periodically persist to storage
	if now.Sub(bucket.lastPersist) > persistenceWindow*time.Second && bucket.dirty {
		go func(tenant string, bucketCopy *tokenBucketState) {
			l.mutex.Lock()
			defer l.mutex.Unlock()
			l.storage.Set(tenant, bucketCopy)
			bucketCopy.lastPersist = now
			bucketCopy.dirty = false
		}(tenantID, bucket)
	}

	return allowed
}

// Allow checks if a request from the given tenant is allowed based on its rate limit.
// It returns true if the request is allowed, and false otherwise.
// If the request is allowed, the rate limiter should atomically increment the request count for that tenant.
//
// tenantID: A string identifying the tenant making the request.
// rateLimit: The maximum number of requests allowed per window for the tenant.
// window: The time window in seconds for the rate limit (e.g., 60 for 60 seconds).
func Allow(tenantID string, rateLimit int, window int) bool {
	// Initialize the limiter if needed
	initLimiter()
	
	// Use sliding window implementation for better accuracy
	return limiter.getAllowSlidingWindow(tenantID, rateLimit, window)
}