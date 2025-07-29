package cache_invalidation

import (
	"sync"
)

type InvalidationMessage struct {
	Key       string
	Timestamp int64
}

type cacheItem struct {
	value   string
	version int64
}

type CacheServer struct {
	name string
	data map[string]cacheItem
	mu   sync.RWMutex
}

func NewCacheServer(name string) *CacheServer {
	return &CacheServer{
		name: name,
		data: make(map[string]cacheItem),
	}
}

func (cs *CacheServer) Set(key, value string) {
	cs.mu.Lock()
	defer cs.mu.Unlock()
	// Default version is 0, meaning no explicit versioning.
	cs.data[key] = cacheItem{
		value:   value,
		version: 0,
	}
}

func (cs *CacheServer) SetWithVersion(key, value string, version int64) {
	cs.mu.Lock()
	defer cs.mu.Unlock()
	cs.data[key] = cacheItem{
		value:   value,
		version: version,
	}
}

func (cs *CacheServer) Get(key string) (string, bool) {
	cs.mu.RLock()
	defer cs.mu.RUnlock()
	item, ok := cs.data[key]
	if !ok {
		return "", false
	}
	return item.value, true
}

func (cs *CacheServer) Invalidate(msg InvalidationMessage) {
	cs.mu.Lock()
	defer cs.mu.Unlock()
	item, exists := cs.data[msg.Key]
	if !exists {
		return
	}
	// If the invalidation message timestamp is greater than the item's version, remove it.
	// For items set using Set (with default version 0), any msg with Timestamp > 0 should remove the item.
	if msg.Timestamp > item.version {
		delete(cs.data, msg.Key)
	}
}