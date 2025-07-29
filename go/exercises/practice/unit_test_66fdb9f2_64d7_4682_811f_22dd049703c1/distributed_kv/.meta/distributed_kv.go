package distributed_kv

import (
	"math/rand"
	"sync"
	"time"
)

type ValueEntry struct {
	Value     string
	Timestamp int
}

type Node struct {
	id       int
	fanout   int
	dropRate float64
	peers    []*Node

	lock  sync.RWMutex
	store map[string]ValueEntry
	clock int
}

// NewNode creates a new Node with the given id, fanout, and dropRate.
func NewNode(id int, fanout int, dropRate float64) *Node {
	// Seed the random generator once per node creation.
	rand.Seed(time.Now().UnixNano() + int64(id))
	return &Node{
		id:       id,
		fanout:   fanout,
		dropRate: dropRate,
		store:    make(map[string]ValueEntry),
		peers:    make([]*Node, 0),
		clock:    0,
	}
}

// Put inserts or updates the key with the given value using LWW rule.
func (n *Node) Put(key, value string) {
	n.lock.Lock()
	n.clock++
	timestamp := n.clock
	// If key exists, enforce conflict resolution if timestamps are equal.
	existing, exists := n.store[key]
	if exists {
		if timestamp > existing.Timestamp {
			n.store[key] = ValueEntry{
				Value:     value,
				Timestamp: timestamp,
			}
		} else if timestamp == existing.Timestamp {
			// If timestamps equal, choose lexicographically smaller value.
			if value < existing.Value {
				n.store[key] = ValueEntry{
					Value:     value,
					Timestamp: timestamp,
				}
			}
		}
	} else {
		n.store[key] = ValueEntry{
			Value:     value,
			Timestamp: timestamp,
		}
	}
	n.lock.Unlock()
}

// Get retrieves the value associated with the key.
// If the key is not found, it returns an empty string.
func (n *Node) Get(key string) string {
	n.lock.RLock()
	entry, exists := n.store[key]
	n.lock.RUnlock()
	if exists {
		return entry.Value
	}
	return ""
}

// AddPeer adds a new peer to the node's list of peers.
func (n *Node) AddPeer(peer *Node) {
	n.lock.Lock()
	defer n.lock.Unlock()
	n.peers = append(n.peers, peer)
}

// Gossip sends the local store to a random subset of peers and merges remote updates.
func (n *Node) Gossip() {
	// Create a snapshot of the local store.
	n.lock.RLock()
	snapshot := make(map[string]ValueEntry, len(n.store))
	for k, v := range n.store {
		snapshot[k] = v
	}
	peersCopy := make([]*Node, len(n.peers))
	copy(peersCopy, n.peers)
	n.lock.RUnlock()

	// Determine number of peers to gossip to.
	numPeers := n.fanout
	if numPeers > len(peersCopy) {
		numPeers = len(peersCopy)
	}

	// Randomly sample peers without replacement.
	indices := rand.Perm(len(peersCopy))
	for i := 0; i < numPeers; i++ {
		peer := peersCopy[indices[i]]
		// Simulate message drop with probability dropRate.
		if rand.Float64() < n.dropRate {
			continue
		}
		peer.mergeStore(snapshot)
	}
}

// mergeStore merges an incoming store snapshot into the node's local store.
func (n *Node) mergeStore(incoming map[string]ValueEntry) {
	n.lock.Lock()
	defer n.lock.Unlock()
	for key, incomingEntry := range incoming {
		localEntry, exists := n.store[key]
		if !exists {
			n.store[key] = incomingEntry
		} else {
			// Conflict resolution: choose the entry with higher timestamp.
			// If timestamps are equal, choose the one with lexicographically smaller value.
			if incomingEntry.Timestamp > localEntry.Timestamp {
				n.store[key] = incomingEntry
			} else if incomingEntry.Timestamp == localEntry.Timestamp {
				if incomingEntry.Value < localEntry.Value {
					n.store[key] = incomingEntry
				}
			}
		}
		// Also update local clock if needed.
		if incomingEntry.Timestamp > n.clock {
			n.clock = incomingEntry.Timestamp
		}
	}
}