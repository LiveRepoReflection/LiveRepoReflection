package consistentcache

import (
	"hash/fnv"
	"sync"
	"time"
)

type CacheEntry struct {
	Value     string
	Timestamp time.Time
}

type Node struct {
	data     map[string]CacheEntry
	mutex    sync.RWMutex
	capacity int
	lru      []string
}

type CacheCluster struct {
	nodes       []*Node
	numNodes    int
	updateChan  chan updateMessage
	mutex       sync.RWMutex
	wg          sync.WaitGroup
}

type updateMessage struct {
	key       string
	value     string
	timestamp time.Time
	delete    bool
	sourceID  int
}

func NewNode(capacity int) *Node {
	return &Node{
		data:     make(map[string]CacheEntry),
		capacity: capacity,
		lru:      make([]string, 0),
	}
}

func NewCacheCluster(numNodes int) *CacheCluster {
	cluster := &CacheCluster{
		nodes:      make([]*Node, numNodes),
		numNodes:   numNodes,
		updateChan: make(chan updateMessage, 1000),
	}

	for i := 0; i < numNodes; i++ {
		cluster.nodes[i] = NewNode(10000)
	}

	// Start update propagation goroutine
	cluster.wg.Add(1)
	go cluster.propagateUpdates()

	return cluster
}

func (c *CacheCluster) propagateUpdates() {
	defer c.wg.Done()
	for msg := range c.updateChan {
		for nodeID, node := range c.nodes {
			if nodeID == msg.sourceID {
				continue
			}
			node.mutex.Lock()
			if msg.delete {
				delete(node.data, msg.key)
				node.removeLRU(msg.key)
			} else {
				node.updateEntry(msg.key, msg.value, msg.timestamp)
			}
			node.mutex.Unlock()
		}
	}
}

func (c *CacheCluster) getNodeForKey(key string) *Node {
	hash := fnv.New32a()
	hash.Write([]byte(key))
	nodeIndex := int(hash.Sum32()) % c.numNodes
	return c.nodes[nodeIndex]
}

func (n *Node) updateEntry(key, value string, timestamp time.Time) {
	// Check if we need to evict
	if len(n.data) >= n.capacity && n.data[key].Timestamp.IsZero() {
		// Evict least recently used
		if len(n.lru) > 0 {
			delete(n.data, n.lru[0])
			n.lru = n.lru[1:]
		}
	}

	// Update entry
	n.data[key] = CacheEntry{
		Value:     value,
		Timestamp: timestamp,
	}

	// Update LRU
	n.removeLRU(key)
	n.lru = append(n.lru, key)
}

func (n *Node) removeLRU(key string) {
	for i, k := range n.lru {
		if k == key {
			n.lru = append(n.lru[:i], n.lru[i+1:]...)
			break
		}
	}
}

func (c *CacheCluster) Set(key, value string) {
	node := c.getNodeForKey(key)
	timestamp := time.Now()

	node.mutex.Lock()
	node.updateEntry(key, value, timestamp)
	node.mutex.Unlock()

	// Propagate update to other nodes
	c.updateChan <- updateMessage{
		key:       key,
		value:     value,
		timestamp: timestamp,
		delete:    false,
		sourceID:  -1,
	}
}

func (c *CacheCluster) Get(key string) (string, bool) {
	node := c.getNodeForKey(key)
	
	node.mutex.RLock()
	entry, exists := node.data[key]
	if exists {
		// Update LRU
		node.mutex.RUnlock()
		node.mutex.Lock()
		node.removeLRU(key)
		node.lru = append(node.lru, key)
		node.mutex.Unlock()
	} else {
		node.mutex.RUnlock()
	}

	return entry.Value, exists
}

func (c *CacheCluster) Delete(key string) {
	node := c.getNodeForKey(key)
	
	node.mutex.Lock()
	delete(node.data, key)
	node.removeLRU(key)
	node.mutex.Unlock()

	// Propagate delete to other nodes
	c.updateChan <- updateMessage{
		key:       key,
		timestamp: time.Now(),
		delete:    true,
		sourceID:  -1,
	}
}

func (c *CacheCluster) Close() {
	close(c.updateChan)
	c.wg.Wait()
}