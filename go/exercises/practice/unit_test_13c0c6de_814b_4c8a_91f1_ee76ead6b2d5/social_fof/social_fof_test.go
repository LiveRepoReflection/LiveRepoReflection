package social_fof

import (
	"reflect"
	"sort"
	"testing"
)

// resetGraph resets the internal graph data structure for testing.
func resetGraph() {
	// Assume the production code maintains a global variable "graph"
	// which maps a user ID to a set of friend IDs.
	// Here, we reinitialize it to an empty state.
	graph = make(map[int]map[int]struct{})
}

// addFriendship adds a bidirectional friendship between user u and user v.
func addFriendship(u, v int) {
	// Assume the existence of an exported function AddFriendship(u, v int)
	// in the production code that registers the friendship in the graph.
	AddFriendship(u, v)
}

func TestFindFoF(t *testing.T) {
	t.Run("Basic FoF Query", func(t *testing.T) {
		resetGraph()
		// Build graph:
		// 1: [2,3]
		// 2: [1,4]
		// 3: [1,5]
		// 4: [2]
		// 5: [3]
		addFriendship(1, 2)
		addFriendship(1, 3)
		addFriendship(2, 4)
		addFriendship(3, 5)
		// Test duplicate edge should be handled gracefully.
		addFriendship(1, 2)

		expected := []int{4, 5}
		result := FindFoF(1)
		sort.Ints(result)
		if !reflect.DeepEqual(result, expected) {
			t.Errorf("FindFoF(1) = %v; want %v", result, expected)
		}
	})

	t.Run("No Friends", func(t *testing.T) {
		resetGraph()
		// User 10 is isolated with no friendships.
		result := FindFoF(10)
		if len(result) != 0 {
			t.Errorf("FindFoF(10) = %v; expected empty slice", result)
		}
	})

	t.Run("User Not In Graph", func(t *testing.T) {
		resetGraph()
		// Build a simple graph.
		addFriendship(1, 2)
		addFriendship(2, 3)
		// Query a user (99) that hasn't been added to the graph.
		result := FindFoF(99)
		if len(result) != 0 {
			t.Errorf("FindFoF(99) = %v; expected empty slice", result)
		}
	})

	t.Run("Cycle Graph", func(t *testing.T) {
		resetGraph()
		// Build a cycle: 6-7, 7-8, 8-6.
		addFriendship(6, 7)
		addFriendship(7, 8)
		addFriendship(8, 6)
		// For user 6, direct friends are 7 and 8.
		// Their friends are 6 and 8 from 7, and 6 and 7 from 8.
		// After excluding self and direct friends, the FoF set is empty.
		result := FindFoF(6)
		if len(result) != 0 {
			t.Errorf("FindFoF(6) = %v; expected empty slice", result)
		}
	})

	t.Run("Multiple Paths to Same FoF", func(t *testing.T) {
		resetGraph()
		// Build graph:
		// 1: [2,3,4]
		// 2: [1,5]
		// 3: [1,5]
		// 4: [1,5]
		// 5: [2,3,4]
		addFriendship(1, 2)
		addFriendship(1, 3)
		addFriendship(1, 4)
		addFriendship(2, 5)
		addFriendship(3, 5)
		addFriendship(4, 5)

		expected := []int{5}
		result := FindFoF(1)
		sort.Ints(result)
		if !reflect.DeepEqual(result, expected) {
			t.Errorf("FindFoF(1) = %v; want %v", result, expected)
		}
	})
}