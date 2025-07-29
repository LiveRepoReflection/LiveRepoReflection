package net_connect

import (
	"sync"
	"testing"
)

func TestAddAndAreConnected(t *testing.T) {
	nc := NewNetwork()

	// Test basic connectivity
	nc.AddConnection(1, 2)
	nc.AddConnection(2, 3)
	if !nc.AreConnected(1, 3) {
		t.Errorf("Expected nodes 1 and 3 to be connected")
	}

	// Test duplicate connection (should be no-op)
	nc.AddConnection(1, 2)
	if !nc.AreConnected(1, 2) {
		t.Errorf("Expected nodes 1 and 2 to remain connected after duplicate addition")
	}

	// Test adding connections with invalid node IDs (should be no-op)
	nc.AddConnection(-1, 4)
	nc.AddConnection(4, 1000000)
	if nc.AreConnected(-1, 4) {
		t.Errorf("Expected invalid nodes (-1 and 4) not to be connected")
	}
	if nc.AreConnected(4, 1000000) {
		t.Errorf("Expected invalid nodes (4 and 1000000) not to be connected")
	}
}

func TestRemoveConnection(t *testing.T) {
	nc := NewNetwork()

	// Build a small component: 10 - 20 - 30
	nc.AddConnection(10, 20)
	nc.AddConnection(20, 30)
	if !nc.AreConnected(10, 30) {
		t.Errorf("Expected nodes 10 and 30 to be connected")
	}

	// Remove a connection and test connectivity
	nc.RemoveConnection(20, 30)
	if nc.AreConnected(10, 30) {
		t.Errorf("Expected nodes 10 and 30 to be disconnected after removal")
	}

	// Removing non-existent connection should be safe (no panic, no change)
	nc.RemoveConnection(10, 30)
	if nc.AreConnected(10, 30) {
		t.Errorf("Expected nodes 10 and 30 to remain disconnected")
	}
}

func TestLargestConnectedComponent(t *testing.T) {
	nc := NewNetwork()

	// Initially, no valid connections
	if size := nc.FindLargestConnectedComponent(); size != 0 {
		t.Errorf("Expected largest connected component to be 0, got %d", size)
	}

	// Create two separate components:
	// Component 1: 1-2-3-4 (size 4)
	nc.AddConnection(1, 2)
	nc.AddConnection(2, 3)
	nc.AddConnection(3, 4)

	// Component 2: 5-6 (size 2)
	nc.AddConnection(5, 6)

	size := nc.FindLargestConnectedComponent()
	if size != 4 {
		t.Errorf("Expected largest connected component size 4, got %d", size)
	}

	// Connect the two components to form one larger component of size 6
	nc.AddConnection(4, 5)
	size = nc.FindLargestConnectedComponent()
	if size != 6 {
		t.Errorf("Expected largest connected component size 6 after merging, got %d", size)
	}
}

func TestConcurrentAccess(t *testing.T) {
	nc := NewNetwork()
	var wg sync.WaitGroup

	// Spawn many goroutines to add connections concurrently
	for i := 0; i < 1000; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			// Connect node i to i+1 if valid
			if i < 999 {
				nc.AddConnection(i, i+1)
			}
		}(i)
	}
	wg.Wait()

	// Check connectivity between the first and the last nodes
	if !nc.AreConnected(0, 999) {
		t.Errorf("Expected nodes 0 and 999 to be connected after concurrent operations")
	}

	// Concurrent removals
	for i := 0; i < 500; i++ {
		wg.Add(1)
		go func(i int) {
			defer wg.Done()
			nc.RemoveConnection(i, i+1)
		}(i)
	}
	wg.Wait()

	// It's uncertain which exact nodes remain connected,
	// but the largest component should be less than or equal to 1000.
	size := nc.FindLargestConnectedComponent()
	if size > 1000 {
		t.Errorf("Expected largest connected component size to be <= 1000, got %d", size)
	}
}