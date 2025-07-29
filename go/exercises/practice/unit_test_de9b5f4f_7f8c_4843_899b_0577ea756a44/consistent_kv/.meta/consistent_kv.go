package consistent_kv

import (
	"crypto/sha256"
	"encoding/binary"
	"errors"
	"sort"
	"sync"
)

type Node struct {
	id        string
	available bool
	store     map[string]string
	lock      sync.RWMutex
}

func NewNode(id string) *Node {
	return &Node{
		id:        id,
		available: true,
		store:     make(map[string]string),
	}
}

func (n *Node) Put(key, value string) error {
	n.lock.Lock()
	defer n.lock.Unlock()
	if !n.available {
		return errors.New("node " + n.id + " is unavailable")
	}
	n.store[key] = value
	return nil
}

func (n *Node) Get(key string) (string, error) {
	n.lock.RLock()
	defer n.lock.RUnlock()
	if !n.available {
		return "", errors.New("node " + n.id + " is unavailable")
	}
	val, ok := n.store[key]
	if !ok {
		return "", errors.New("key not found")
	}
	return val, nil
}

func (n *Node) Fail() {
	n.lock.Lock()
	defer n.lock.Unlock()
	n.available = false
}

func (n *Node) Recover() {
	n.lock.Lock()
	defer n.lock.Unlock()
	n.available = true
}

type hashEntry struct {
	hash uint64
	node *Node
}

type Cluster struct {
	nodes             []*Node
	replicationFactor int
	ring              []hashEntry
	lock              sync.RWMutex
}

// NewCluster creates a new cluster with the provided node IDs and replication factor.
func NewCluster(nodeIDs []string, replicationFactor int) *Cluster {
	cluster := &Cluster{
		replicationFactor: replicationFactor,
	}
	for _, id := range nodeIDs {
		cluster.nodes = append(cluster.nodes, NewNode(id))
	}
	cluster.generateRing()
	return cluster
}

// generateRing generates the consistent hash ring from the cluster's nodes.
func (c *Cluster) generateRing() {
	c.lock.Lock()
	defer c.lock.Unlock()
	c.ring = make([]hashEntry, 0, len(c.nodes))
	for _, node := range c.nodes {
		h := computeHash(node.id)
		c.ring = append(c.ring, hashEntry{
			hash: h,
			node: node,
		})
	}
	sort.Slice(c.ring, func(i, j int) bool {
		return c.ring[i].hash < c.ring[j].hash
	})
}

// computeHash computes a hash value for a given string using sha256.
func computeHash(key string) uint64 {
	sum := sha256.Sum256([]byte(key))
	return binary.BigEndian.Uint64(sum[:8])
}

// getNodesForKey returns the list of nodes handling the key based on consistent hashing.
func (c *Cluster) getNodesForKey(key string) []*Node {
	c.lock.RLock()
	defer c.lock.RUnlock()
	var nodes []*Node
	if len(c.ring) == 0 {
		return nodes
	}
	keyHash := computeHash(key)
	// Find the first node with a hash greater than or equal to keyHash.
	idx := sort.Search(len(c.ring), func(i int) bool {
		return c.ring[i].hash >= keyHash
	})
	// Wrap around the ring if needed.
	if idx == len(c.ring) {
		idx = 0
	}
	// Collect replicationFactor nodes.
	count := c.replicationFactor
	if count > len(c.ring) {
		count = len(c.ring)
	}
	for i := 0; i < count; i++ {
		entry := c.ring[(idx+i)%len(c.ring)]
		nodes = append(nodes, entry.node)
	}
	return nodes
}

// Put stores the key-value pair on all replication nodes. Returns an error if any replica fails.
func (c *Cluster) Put(key, value string) error {
	nodes := c.getNodesForKey(key)
	for _, node := range nodes {
		err := node.Put(key, value)
		if err != nil {
			return err
		}
	}
	return nil
}

// Get retrieves the value for a key from the first available replication node.
func (c *Cluster) Get(key string) (string, error) {
	nodes := c.getNodesForKey(key)
	var lastErr error
	for _, node := range nodes {
		val, err := node.Get(key)
		if err == nil {
			return val, nil
		}
		lastErr = err
	}
	if lastErr == nil {
		lastErr = errors.New("key not found")
	}
	return "", lastErr
}

// GetPrimaryNode returns the id of the primary node for the given key.
func (c *Cluster) GetPrimaryNode(key string) (string, error) {
	nodes := c.getNodesForKey(key)
	if len(nodes) == 0 {
		return "", errors.New("no nodes in cluster")
	}
	return nodes[0].id, nil
}

// FailNode simulates a node failure by marking the node as unavailable.
func (c *Cluster) FailNode(nodeID string) error {
	c.lock.RLock()
	defer c.lock.RUnlock()
	for _, node := range c.nodes {
		if node.id == nodeID {
			node.Fail()
			return nil
		}
	}
	return errors.New("node not found")
}

// RecoverNode simulates a node recovery by marking the node as available.
func (c *Cluster) RecoverNode(nodeID string) error {
	c.lock.RLock()
	defer c.lock.RUnlock()
	for _, node := range c.nodes {
		if node.id == nodeID {
			node.Recover()
			return nil
		}
	}
	return errors.New("node not found")
}