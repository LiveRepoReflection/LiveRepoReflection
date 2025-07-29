package distributed_kv

import (
	"math/rand"
	"sync"
	"testing"
	"time"
)

// Assumed interface (not provided) for the Node type and its constructor.
// The Node should implement the following methods:
//   - Put(key, value string)
//   - Get(key string) string
//   - Gossip()  // performs one round of gossip, including message loss simulation.
//   - AddPeer(peer *Node)
//   - Start() // starts background gossip routine (if implemented)
//   - Stop()  // stops background gossip routine (if implemented)
// For testing purposes, we assume that NewNode(id int, fanout int, dropRate float64) *Node
// creates a new node with the provided configuration.

func createCluster(n int, fanout int, dropRate float64) []*Node {
	cluster := make([]*Node, n)
	for i := 0; i < n; i++ {
		cluster[i] = NewNode(i, fanout, dropRate)
	}
	// Add all nodes as peers to each other. In a real system, nodes might not know all peers.
	for i := 0; i < n; i++ {
		for j := 0; j < n; j++ {
			if i != j {
				cluster[i].AddPeer(cluster[j])
			}
		}
	}
	return cluster
}

// simulateGossip performs a given number of gossip rounds over the entire cluster.
func simulateGossip(cluster []*Node, rounds int) {
	for i := 0; i < rounds; i++ {
		for _, node := range cluster {
			node.Gossip()
		}
		// Wait a bit between rounds to simulate asynchronous propagation.
		time.Sleep(10 * time.Millisecond)
	}
}

func TestBasicPutGet(t *testing.T) {
	// Create a single node cluster.
	node := NewNode(0, 5, 0.0) // no message loss in single node.
	// Basic PUT and GET.
	key := "testKey"
	value := "testValue"
	node.Put(key, value)
	got := node.Get(key)
	if got != value {
		t.Errorf("BasicPutGet: for key %q expected %q, got %q", key, value, got)
	}
}

func TestConflictResolution(t *testing.T) {
	// Create a two-node cluster with no gossip loss.
	cluster := createCluster(2, 1, 0.0)
	key := "conflictKey"

	// Introduce two conflicting writes.
	// To simulate conflict, we perform two writes with a very small delay.
	// The one with the later timestamp should normally win.
	// However if the timestamps are equal, then by rule the lexicographically smaller one wins.
	// Given that the internal timestamp is based on a monotonically increasing counter,
	// we force a conflict scenario by performing two puts nearly concurrently.
	cluster[0].Put(key, "B_value")
	// Sleep briefly to allow the counter to increment.
	time.Sleep(1 * time.Millisecond)
	cluster[1].Put(key, "A_value")
	
	// Manually gossip a few rounds to ensure both nodes learn of each other's updates.
	simulateGossip(cluster, 10)
	
	// Determine expected value based on timestamps and lexicographical order.
	// In this test, since cluster[1] did a PUT with a later timestamp, its value ("A_value")
	// should prevail even though lexicographically "A_value" is less than "B_value".
	expected := "A_value"
	for i, node := range cluster {
		got := node.Get(key)
		if got != expected {
			t.Errorf("ConflictResolution: node %d expected %q for key %q, got %q", i, expected, key, got)
		}
	}
}

func TestGossipConvergence(t *testing.T) {
	// Create a cluster of 5 nodes with some message loss (simulate unreliability).
	cluster := createCluster(5, 3, 0.1)
	key := "gossipKey"
	value := "finalValue"

	// Issue a PUT on one node.
	cluster[0].Put(key, value)

	// Run many gossip rounds to allow the update to propagate.
	simulateGossip(cluster, 50)

	// Check that all nodes have converged to the same value.
	for i, node := range cluster {
		got := node.Get(key)
		if got != value {
			t.Errorf("GossipConvergence: node %d expected %q for key %q, got %q", i, value, key, got)
		}
	}
}

func TestConcurrentOperations(t *testing.T) {
	// Create a cluster of 7 nodes with some message loss.
	cluster := createCluster(7, 3, 0.15)
	keys := []string{"alpha", "beta", "gamma", "delta", "epsilon"}
	numOps := 100

	var wg sync.WaitGroup
	// Launch concurrent PUT operations.
	for i := 0; i < numOps; i++ {
		wg.Add(1)
		go func(op int) {
			defer wg.Done()
			// Each operation picks a random node and random key-value update.
			node := cluster[rand.Intn(len(cluster))]
			key := keys[rand.Intn(len(keys))]
			// The value is determined by the op number and node id for diversity.
			value := key + "_" + time.Now().Format("150405.000") 
			node.Put(key, value)
		}(i)
	}

	// Additionally, concurrently trigger gossip rounds.
	stopCh := make(chan struct{})
	go func() {
		for {
			select {
			case <-stopCh:
				return
			default:
				for _, node := range cluster {
					node.Gossip()
				}
				time.Sleep(5 * time.Millisecond)
			}
		}
	}()

	wg.Wait()
	// Stop the concurrent gossip.
	close(stopCh)

	// Allow additional rounds for final convergence.
	simulateGossip(cluster, 50)

	// Verify that for each key, all nodes return the same value.
	for _, key := range keys {
		var expected string
		for i, node := range cluster {
			val := node.Get(key)
			if i == 0 {
				expected = val
			} else {
				if val != expected {
					t.Errorf("ConcurrentOperations: mismatch for key %q: expected %q, but node %d has %q", key, expected, i, val)
				}
			}
		}
	}
}