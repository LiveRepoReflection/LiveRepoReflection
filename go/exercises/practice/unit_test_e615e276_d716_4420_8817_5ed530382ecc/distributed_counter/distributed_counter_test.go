package distributed_counter_test

import (
	"sync"
	"testing"
	"time"

	"distributed_counter"
)

func TestBasicIncrementRead(t *testing.T) {
	node := distributed_counter.NewNode("node1", 0)

	// Perform 10 increments on the node
	for i := 0; i < 10; i++ {
		err := node.Increment()
		if err != nil {
			t.Fatalf("Increment error on iteration %d: %v", i, err)
		}
	}

	value, err := node.Read()
	if err != nil {
		t.Fatalf("Read error: %v", err)
	}
	if value != 10 {
		t.Errorf("Expected value 10 after 10 increments, got %d", value)
	}
}

func TestConcurrentIncrement(t *testing.T) {
	node := distributed_counter.NewNode("node1", 0)
	var wg sync.WaitGroup
	numGoroutines := 100
	incrementsPerGoroutine := 100

	wg.Add(numGoroutines)
	for i := 0; i < numGoroutines; i++ {
		go func() {
			defer wg.Done()
			for j := 0; j < incrementsPerGoroutine; j++ {
				if err := node.Increment(); err != nil {
					t.Errorf("Concurrent Increment error: %v", err)
				}
			}
		}()
	}
	wg.Wait()

	value, err := node.Read()
	if err != nil {
		t.Fatalf("Read error after concurrent increments: %v", err)
	}
	expected := numGoroutines * incrementsPerGoroutine
	if value != expected {
		t.Errorf("Expected value %d after concurrent increments, got %d", expected, value)
	}
}

func TestMultipleNodesConvergence(t *testing.T) {
	// Create three nodes
	node1 := distributed_counter.NewNode("node1", 0)
	node2 := distributed_counter.NewNode("node2", 0)
	node3 := distributed_counter.NewNode("node3", 0)

	// Establish peer connections among the nodes
	node1.AddPeer(node2)
	node1.AddPeer(node3)
	node2.AddPeer(node1)
	node2.AddPeer(node3)
	node3.AddPeer(node1)
	node3.AddPeer(node2)

	var wg sync.WaitGroup
	increments := 100
	wg.Add(3)

	// Increment on node1
	go func() {
		defer wg.Done()
		for i := 0; i < increments; i++ {
			if err := node1.Increment(); err != nil {
				t.Errorf("node1 Increment error: %v", err)
			}
		}
	}()

	// Increment on node2
	go func() {
		defer wg.Done()
		for i := 0; i < increments; i++ {
			if err := node2.Increment(); err != nil {
				t.Errorf("node2 Increment error: %v", err)
			}
		}
	}()

	// Increment on node3
	go func() {
		defer wg.Done()
		for i := 0; i < increments; i++ {
			if err := node3.Increment(); err != nil {
				t.Errorf("node3 Increment error: %v", err)
			}
		}
	}()

	wg.Wait()

	// Trigger synchronization on all nodes
	if err := node1.Sync(); err != nil {
		t.Errorf("node1 Sync error: %v", err)
	}
	if err := node2.Sync(); err != nil {
		t.Errorf("node2 Sync error: %v", err)
	}
	if err := node3.Sync(); err != nil {
		t.Errorf("node3 Sync error: %v", err)
	}

	// Allow time for eventual consistency
	time.Sleep(100 * time.Millisecond)

	expected := increments * 3

	v1, err := node1.Read()
	if err != nil {
		t.Errorf("node1 Read error: %v", err)
	}
	v2, err := node2.Read()
	if err != nil {
		t.Errorf("node2 Read error: %v", err)
	}
	v3, err := node3.Read()
	if err != nil {
		t.Errorf("node3 Read error: %v", err)
	}

	if v1 != expected || v2 != expected || v3 != expected {
		t.Errorf("Expected converged count %d; got node1=%d, node2=%d, node3=%d", expected, v1, v2, v3)
	}
}

func TestFaultTolerance(t *testing.T) {
	// Create three nodes
	node1 := distributed_counter.NewNode("node1", 0)
	node2 := distributed_counter.NewNode("node2", 0)
	node3 := distributed_counter.NewNode("node3", 0)

	// Establish initial peer connections
	node1.AddPeer(node2)
	node1.AddPeer(node3)
	node2.AddPeer(node1)
	node2.AddPeer(node3)
	node3.AddPeer(node1)
	node3.AddPeer(node2)

	// Perform initial increments on all nodes
	for i := 0; i < 50; i++ {
		if err := node1.Increment(); err != nil {
			t.Errorf("node1 initial Increment error: %v", err)
		}
		if err := node2.Increment(); err != nil {
			t.Errorf("node2 initial Increment error: %v", err)
		}
		if err := node3.Increment(); err != nil {
			t.Errorf("node3 initial Increment error: %v", err)
		}
	}

	// Simulate fault: remove node3 from node1 and node2 peers
	node1.RemovePeer(node3)
	node2.RemovePeer(node3)

	// Further increments on available nodes (node1 and node2)
	for i := 0; i < 50; i++ {
		if err := node1.Increment(); err != nil {
			t.Errorf("node1 Increment during fault: %v", err)
		}
		if err := node2.Increment(); err != nil {
			t.Errorf("node2 Increment during fault: %v", err)
		}
	}

	// Simulate recovery: re-establish peer connections for node3
	node1.AddPeer(node3)
	node2.AddPeer(node3)
	node3.AddPeer(node1)
	node3.AddPeer(node2)

	// Trigger synchronization on all nodes
	if err := node1.Sync(); err != nil {
		t.Errorf("node1 Sync error: %v", err)
	}
	if err := node2.Sync(); err != nil {
		t.Errorf("node2 Sync error: %v", err)
	}
	if err := node3.Sync(); err != nil {
		t.Errorf("node3 Sync error: %v", err)
	}

	// Allow time for state convergence
	time.Sleep(100 * time.Millisecond)

	// Calculation:
	// Each node did 50 increments initially (total 150).
	// Then node1 and node2 did another 50 each (total 100 additional).
	// Expected final count is 150 + 100 = 250.
	expected := 250

	v1, err := node1.Read()
	if err != nil {
		t.Errorf("node1 Read error: %v", err)
	}
	v2, err := node2.Read()
	if err != nil {
		t.Errorf("node2 Read error: %v", err)
	}
	v3, err := node3.Read()
	if err != nil {
		t.Errorf("node3 Read error: %v", err)
	}

	if v1 != expected || v2 != expected || v3 != expected {
		t.Errorf("Expected final count %d; got node1=%d, node2=%d, node3=%d", expected, v1, v2, v3)
	}
}