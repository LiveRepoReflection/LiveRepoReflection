package hashing_ring

import (
	"testing"
)

func TestNewConsistentHashingRing(t *testing.T) {
	t.Run("creates ring with specified virtual nodes", func(t *testing.T) {
		ring := NewConsistentHashingRing(10)
		if ring == nil {
			t.Fatal("Expected new ring instance, got nil")
		}
	})

	t.Run("panics when virtual nodes is zero", func(t *testing.T) {
		defer func() {
			if r := recover(); r == nil {
				t.Error("Expected panic when virtual nodes is zero")
			}
		}()
		NewConsistentHashingRing(0)
	})
}

func TestAddNode(t *testing.T) {
	ring := NewConsistentHashingRing(3)

	t.Run("adds single node", func(t *testing.T) {
		ring.AddNode("node1")
		nodes := ring.ListNodes()
		if len(nodes) != 1 || nodes[0] != "node1" {
			t.Errorf("Expected [node1], got %v", nodes)
		}
	})

	t.Run("adds multiple nodes", func(t *testing.T) {
		ring.AddNode("node2")
		ring.AddNode("node3")
		nodes := ring.ListNodes()
		expected := []string{"node1", "node2", "node3"}
		if !equalStringSlices(nodes, expected) {
			t.Errorf("Expected %v, got %v", expected, nodes)
		}
	})

	t.Run("ignores duplicate nodes", func(t *testing.T) {
		ring.AddNode("node1")
		nodes := ring.ListNodes()
		if len(nodes) != 3 {
			t.Errorf("Expected 3 nodes, got %d", len(nodes))
		}
	})
}

func TestRemoveNode(t *testing.T) {
	ring := NewConsistentHashingRing(3)
	ring.AddNode("node1")
	ring.AddNode("node2")
	ring.AddNode("node3")

	t.Run("removes existing node", func(t *testing.T) {
		ring.RemoveNode("node2")
		nodes := ring.ListNodes()
		expected := []string{"node1", "node3"}
		if !equalStringSlices(nodes, expected) {
			t.Errorf("Expected %v, got %v", expected, nodes)
		}
	})

	t.Run("ignores non-existent node", func(t *testing.T) {
		ring.RemoveNode("node4")
		nodes := ring.ListNodes()
		if len(nodes) != 2 {
			t.Errorf("Expected 2 nodes, got %d", len(nodes))
		}
	})

	t.Run("handles empty ring", func(t *testing.T) {
		emptyRing := NewConsistentHashingRing(3)
		emptyRing.RemoveNode("node1") // Should not panic
	})
}

func TestGetNode(t *testing.T) {
	ring := NewConsistentHashingRing(3)
	ring.AddNode("node1")
	ring.AddNode("node2")
	ring.AddNode("node3")

	t.Run("returns correct node for key", func(t *testing.T) {
		key := "test_key"
		node1 := ring.GetNode(key)
		node2 := ring.GetNode(key)
		if node1 != node2 {
			t.Errorf("Expected consistent node for same key, got %s and %s", node1, node2)
		}
	})

	t.Run("handles empty ring", func(t *testing.T) {
		emptyRing := NewConsistentHashingRing(3)
		node := emptyRing.GetNode("any_key")
		if node != "" {
			t.Errorf("Expected empty string for empty ring, got %s", node)
		}
	})

	t.Run("redistributes keys after node removal", func(t *testing.T) {
		key := "important_key"
		originalNode := ring.GetNode(key)
		ring.RemoveNode(originalNode)
		newNode := ring.GetNode(key)
		if newNode == originalNode {
			t.Errorf("Expected key to be redistributed after node removal")
		}
	})
}

func TestListNodes(t *testing.T) {
	ring := NewConsistentHashingRing(3)

	t.Run("returns empty slice for empty ring", func(t *testing.T) {
		nodes := ring.ListNodes()
		if len(nodes) != 0 {
			t.Errorf("Expected empty slice, got %v", nodes)
		}
	})

	t.Run("returns sorted list of nodes", func(t *testing.T) {
		ring.AddNode("node3")
		ring.AddNode("node1")
		ring.AddNode("node2")
		nodes := ring.ListNodes()
		expected := []string{"node1", "node2", "node3"}
		if !equalStringSlices(nodes, expected) {
			t.Errorf("Expected %v, got %v", expected, nodes)
		}
	})
}

func TestConcurrentAccess(t *testing.T) {
	ring := NewConsistentHashingRing(3)
	done := make(chan bool)

	go func() {
		for i := 0; i < 100; i++ {
			ring.AddNode("node1")
		}
		done <- true
	}()

	go func() {
		for i := 0; i < 100; i++ {
			ring.GetNode("key")
		}
		done <- true
	}()

	<-done
	<-done
	// Test passes if no race conditions detected
}

func equalStringSlices(a, b []string) bool {
	if len(a) != len(b) {
		return false
	}
	for i := range a {
		if a[i] != b[i] {
			return false
		}
	}
	return true
}