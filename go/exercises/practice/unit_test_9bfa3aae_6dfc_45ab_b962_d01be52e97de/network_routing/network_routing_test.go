package network_routing

import (
	"testing"
)

func TestNetworkRouting(t *testing.T) {
	t.Run("NewNetwork", func(t *testing.T) {
		n := NewNetwork(5)
		if n == nil {
			t.Error("NewNetwork returned nil")
		}
	})

	t.Run("AddLink and GetShortestPath", func(t *testing.T) {
		n := NewNetwork(3)
		n.AddLink(0, 1, 5)
		n.AddLink(1, 2, 3)

		if got := n.GetShortestPath(0, 2); got != 8 {
			t.Errorf("Expected shortest path 8, got %d", got)
		}
	})

	t.Run("RemoveLink", func(t *testing.T) {
		n := NewNetwork(3)
		n.AddLink(0, 1, 5)
		n.AddLink(1, 2, 3)
		n.RemoveLink(1, 2)

		if got := n.GetShortestPath(0, 2); got != -1 {
			t.Errorf("Expected no path (-1), got %d", got)
		}
	})

	t.Run("UpdateLink", func(t *testing.T) {
		n := NewNetwork(3)
		n.AddLink(0, 1, 5)
		n.AddLink(0, 1, 2) // Update existing link
		n.AddLink(1, 2, 3)

		if got := n.GetShortestPath(0, 2); got != 5 {
			t.Errorf("Expected shortest path 5, got %d", got)
		}
	})

	t.Run("DisconnectedGraph", func(t *testing.T) {
		n := NewNetwork(4)
		n.AddLink(0, 1, 2)
		n.AddLink(2, 3, 3)

		if got := n.GetShortestPath(0, 3); got != -1 {
			t.Errorf("Expected no path (-1), got %d", got)
		}
	})

	t.Run("MultiplePaths", func(t *testing.T) {
		n := NewNetwork(4)
		n.AddLink(0, 1, 5)
		n.AddLink(0, 2, 2)
		n.AddLink(1, 3, 1)
		n.AddLink(2, 3, 3)

		if got := n.GetShortestPath(0, 3); got != 5 {
			t.Errorf("Expected shortest path 5, got %d", got)
		}
	})

	t.Run("SelfLoop", func(t *testing.T) {
		n := NewNetwork(2)
		n.AddLink(0, 0, 1) // Self loop
		n.AddLink(0, 1, 2)

		if got := n.GetShortestPath(0, 1); got != 2 {
			t.Errorf("Expected shortest path 2, got %d", got)
		}
	})

	t.Run("LargeNetwork", func(t *testing.T) {
		n := NewNetwork(1000)
		for i := 0; i < 999; i++ {
			n.AddLink(i, i+1, 1)
		}

		if got := n.GetShortestPath(0, 999); got != 999 {
			t.Errorf("Expected shortest path 999, got %d", got)
		}
	})
}