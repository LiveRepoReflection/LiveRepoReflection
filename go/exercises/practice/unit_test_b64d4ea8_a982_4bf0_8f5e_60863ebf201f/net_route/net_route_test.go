package net_route

import (
	"testing"
)

// TestOptimalRouting runs a series of subtests to validate the network routing system.
func TestOptimalRouting(t *testing.T) {
	t.Run("BasicRoute", func(t *testing.T) {
		// Create a network of 5 nodes with a simple chain connection.
		n := 5
		netw := NewNetwork(n)
		netw.AddLink(0, 1, 10)
		netw.AddLink(1, 2, 5)
		netw.AddLink(2, 3, 2)
		netw.AddLink(3, 4, 1)

		result := netw.RouteRequest(0, 4)
		expected := 18
		if result != expected {
			t.Errorf("BasicRoute: expected %d, got %d", expected, result)
		}
	})

	t.Run("NonConnectingRoute", func(t *testing.T) {
		// Create a network of 4 nodes but leave one node disconnected.
		n := 4
		netw := NewNetwork(n)
		netw.AddLink(0, 1, 5)
		netw.AddLink(1, 2, 5)
		// Node 3 is isolated.
		result := netw.RouteRequest(0, 3)
		if result != -1 {
			t.Errorf("NonConnectingRoute: expected -1 for disconnected nodes, got %d", result)
		}
	})

	t.Run("LinkRemoval", func(t *testing.T) {
		// Create a network of 5 nodes and then remove a critical link.
		n := 5
		netw := NewNetwork(n)
		netw.AddLink(0, 1, 10)
		netw.AddLink(1, 2, 5)
		netw.AddLink(2, 3, 2)
		netw.AddLink(3, 4, 1)

		// Remove the link between nodes 2 and 3.
		netw.RemoveLink(2, 3)
		result := netw.RouteRequest(0, 4)
		if result != -1 {
			t.Errorf("LinkRemoval: expected -1 after removing link, got %d", result)
		}

		// Add an alternative path.
		netw.AddLink(2, 4, 20)
		result = netw.RouteRequest(0, 4)
		expected := 10 + 5 + 20
		if result != expected {
			t.Errorf("LinkRemoval alternative: expected %d, got %d", expected, result)
		}
	})

	t.Run("NodeFailure", func(t *testing.T) {
		// Create a network and simulate a node failure.
		n := 5
		netw := NewNetwork(n)
		netw.AddLink(0, 1, 10)
		netw.AddLink(1, 2, 5)
		netw.AddLink(2, 3, 2)
		netw.AddLink(3, 4, 1)

		// Fail node 2 which should disconnect the network.
		netw.NodeFailure(2)
		result := netw.RouteRequest(0, 4)
		if result != -1 {
			t.Errorf("NodeFailure: expected -1 due to node failure, got %d", result)
		}
	})

	t.Run("UpdateLink", func(t *testing.T) {
		// Create a network and then update the latency on an existing link.
		n := 4
		netw := NewNetwork(n)
		netw.AddLink(0, 1, 15)
		netw.AddLink(1, 2, 15)
		netw.AddLink(2, 3, 15)

		result := netw.RouteRequest(0, 3)
		expected := 45
		if result != expected {
			t.Errorf("UpdateLink initial: expected %d, got %d", expected, result)
		}

		// Update the latency for link between nodes 1 and 2.
		netw.AddLink(1, 2, 5)
		result = netw.RouteRequest(0, 3)
		expected = 15 + 5 + 15
		if result != expected {
			t.Errorf("UpdateLink updated: expected %d, got %d", expected, result)
		}
	})

	t.Run("MultipleUpdatesSequence", func(t *testing.T) {
		// Simulate a sequence of operations including additions, removals, and node failures.
		n := 6
		netw := NewNetwork(n)
		// Establish two potential routes.
		netw.AddLink(0, 1, 3)
		netw.AddLink(1, 2, 4)
		netw.AddLink(2, 5, 10)
		netw.AddLink(0, 3, 2)
		netw.AddLink(3, 4, 2)
		netw.AddLink(4, 5, 2)

		// The optimal route from 0 to 5 should initially be 0->3->4->5: 2+2+2 = 6.
		result := netw.RouteRequest(0, 5)
		expected := 6
		if result != expected {
			t.Errorf("MultipleUpdatesSequence initial: expected %d, got %d", expected, result)
		}

		// Remove part of the optimal route.
		netw.RemoveLink(3, 4)
		result = netw.RouteRequest(0, 5)
		// Next best option is 0->1->2->5: 3+4+10 = 17.
		expected = 17
		if result != expected {
			t.Errorf("MultipleUpdatesSequence after removal: expected %d, got %d", expected, result)
		}

		// Restore the removed link with updated lower latency.
		netw.AddLink(3, 4, 1)
		result = netw.RouteRequest(0, 5)
		// New optimal route should be 0->3->4->5: 2+1+2 = 5.
		expected = 5
		if result != expected {
			t.Errorf("MultipleUpdatesSequence after restoration: expected %d, got %d", expected, result)
		}

		// Fail a node in the optimal path.
		netw.NodeFailure(4)
		result = netw.RouteRequest(0, 5)
		// The only valid route now is 0->1->2->5: 3+4+10 = 17.
		expected = 17
		if result != expected {
			t.Errorf("MultipleUpdatesSequence after node failure: expected %d, got %d", expected, result)
		}
	})
}

// BenchmarkRouteRequest benchmarks the RouteRequest function on a large chain network.
func BenchmarkRouteRequest(b *testing.B) {
	n := 1000
	netw := NewNetwork(n)
	// Create a simple chain: 0 -> 1 -> 2 -> ... -> n-1 with latency 1.
	for i := 0; i < n-1; i++ {
		netw.AddLink(i, i+1, 1)
	}
	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		_ = netw.RouteRequest(0, n-1)
	}
}