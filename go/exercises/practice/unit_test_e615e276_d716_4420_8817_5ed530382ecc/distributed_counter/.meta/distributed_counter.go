package distributed_counter

import (
	"sync"
)

type Node struct {
	id    string
	state map[string]int
	mu    sync.Mutex
	peers []*Node
}

// NewNode creates a new Node with the given id and initial counter value.
// The internal state is represented as a map for a G-Counter CRDT.
func NewNode(id string, initial int) *Node {
	n := &Node{
		id:    id,
		state: make(map[string]int),
		peers: make([]*Node, 0),
	}
	// Initialize the state with the given initial value for this node.
	n.state[id] = initial
	return n
}

// Increment increases the local counter for this node by 1.
func (n *Node) Increment() error {
	n.mu.Lock()
	defer n.mu.Unlock()
	n.state[n.id]++
	return nil
}

// Read returns the total count as the sum of all counters in the node's state.
func (n *Node) Read() (int, error) {
	n.mu.Lock()
	defer n.mu.Unlock()
	total := 0
	for _, count := range n.state {
		total += count
	}
	return total, nil
}

// Sync synchronizes the node's state with all its peers using the pairwise maximum operation.
// It copies states from peers and updates its own state accordingly.
func (n *Node) Sync() error {
	// Create a copy of the local state.
	n.mu.Lock()
	localCopy := make(map[string]int)
	for k, v := range n.state {
		localCopy[k] = v
	}
	n.mu.Unlock()

	// Iterate over each peer and merge their state into localCopy.
	for _, peer := range n.peers {
		peer.mu.Lock()
		peerCopy := make(map[string]int)
		for k, v := range peer.state {
			peerCopy[k] = v
		}
		peer.mu.Unlock()
		for key, peerVal := range peerCopy {
			if localVal, exists := localCopy[key]; !exists || peerVal > localVal {
				localCopy[key] = peerVal
			}
		}
	}

	// Update the node's state with the merged result.
	n.mu.Lock()
	for key, val := range localCopy {
		n.state[key] = val
	}
	n.mu.Unlock()
	return nil
}

// AddPeer adds a peer node to the current node's list of peers.
func (n *Node) AddPeer(peer *Node) {
	n.mu.Lock()
	defer n.mu.Unlock()
	for _, p := range n.peers {
		if p.id == peer.id {
			return
		}
	}
	n.peers = append(n.peers, peer)
}

// RemovePeer removes a peer node from the current node's list of peers.
func (n *Node) RemovePeer(peer *Node) {
	n.mu.Lock()
	defer n.mu.Unlock()
	for i, p := range n.peers {
		if p.id == peer.id {
			n.peers = append(n.peers[:i], n.peers[i+1:]...)
			return
		}
	}
}