package shortest_path

import (
	"reflect"
	"sync"
	"testing"
)

func TestBasicPathfinding(t *testing.T) {
	pf := NewPathfinder()
	// Adding locations to form a simple path: 1 -> 2 -> 3 -> 4, with an alternative direct edge 1 -> 4.
	pf.AddLocation(1)
	pf.AddLocation(2)
	pf.AddLocation(3)
	pf.AddLocation(4)

	pf.AddRoad(1, 2, 10)
	pf.AddRoad(2, 3, 15)
	pf.AddRoad(3, 4, 10)
	pf.AddRoad(1, 4, 50)

	// Expect the optimal path 1->2->3->4 with a total cost of 35.
	path, cost := pf.FindShortestPath(1, 4, []int{})
	expectedPath := []int{1, 2, 3, 4}
	if cost != 35 || !reflect.DeepEqual(path, expectedPath) {
		t.Errorf("Expected path %v with cost 35, but got path %v with cost %d", expectedPath, path, cost)
	}
}

func TestAvoidNodes(t *testing.T) {
	pf := NewPathfinder()
	// Build the graph: 1 -> 2 -> 3 -> 4 and a direct 1 -> 4.
	pf.AddLocation(1)
	pf.AddLocation(2)
	pf.AddLocation(3)
	pf.AddLocation(4)

	pf.AddRoad(1, 2, 10)
	pf.AddRoad(2, 3, 15)
	pf.AddRoad(3, 4, 10)
	pf.AddRoad(1, 4, 50)

	// When avoiding node 2, the optimal path should be direct: 1->4 with cost 50.
	path, cost := pf.FindShortestPath(1, 4, []int{2})
	expectedPath := []int{1, 4}
	if cost != 50 || !reflect.DeepEqual(path, expectedPath) {
		t.Errorf("Expected path %v with cost 50 when avoiding node 2, but got path %v with cost %d", expectedPath, path, cost)
	}

	// When avoiding both nodes 2 and 3, the only remaining possibility is also direct: 1->4.
	path, cost = pf.FindShortestPath(1, 4, []int{2, 3})
	expectedPath = []int{1, 4}
	if cost != 50 || !reflect.DeepEqual(path, expectedPath) {
		t.Errorf("Expected path %v with cost 50 when avoiding nodes 2 and 3, but got path %v with cost %d", expectedPath, path, cost)
	}

	// If start is in the avoid list, return no valid path.
	path, cost = pf.FindShortestPath(1, 4, []int{1})
	if cost != -1 || len(path) != 0 {
		t.Errorf("Expected no path when start is avoided, got path %v with cost %d", path, cost)
	}

	// If end is in the avoid list, return no valid path.
	path, cost = pf.FindShortestPath(1, 4, []int{4})
	if cost != -1 || len(path) != 0 {
		t.Errorf("Expected no path when end is avoided, got path %v with cost %d", path, cost)
	}
}

func TestUpdateRoadCost(t *testing.T) {
	pf := NewPathfinder()
	// Create a triangle graph: 1 <-> 2, 2 <-> 3, and a direct edge 1 <-> 3.
	pf.AddLocation(1)
	pf.AddLocation(2)
	pf.AddLocation(3)

	pf.AddRoad(1, 2, 10)
	pf.AddRoad(2, 3, 15)
	pf.AddRoad(1, 3, 50)

	// Initially, the optimal path from 1 to 3 should be via 2 with cost 25.
	path, cost := pf.FindShortestPath(1, 3, []int{})
	expectedPath := []int{1, 2, 3}
	if cost != 25 || !reflect.DeepEqual(path, expectedPath) {
		t.Errorf("Expected path %v with cost 25, but got path %v with cost %d", expectedPath, path, cost)
	}

	// Update the direct edge to have a lower cost than the indirect path.
	pf.UpdateRoadCost(1, 3, 5)
	path, cost = pf.FindShortestPath(1, 3, []int{})
	expectedPath = []int{1, 3}
	if cost != 5 || !reflect.DeepEqual(path, expectedPath) {
		t.Errorf("After updating, expected path %v with cost 5, but got path %v with cost %d", expectedPath, path, cost)
	}
}

func TestNonExistentPaths(t *testing.T) {
	pf := NewPathfinder()
	// Add two locations without connecting them.
	pf.AddLocation(1)
	pf.AddLocation(2)

	// Should return no valid path between 1 and 2.
	path, cost := pf.FindShortestPath(1, 2, []int{})
	if cost != -1 || len(path) != 0 {
		t.Errorf("Expected no path between 1 and 2, got path %v with cost %d", path, cost)
	}

	// Start location does not exist.
	path, cost = pf.FindShortestPath(3, 2, []int{})
	if cost != -1 || len(path) != 0 {
		t.Errorf("Expected no path when start location does not exist, got path %v with cost %d", path, cost)
	}

	// End location does not exist.
	path, cost = pf.FindShortestPath(1, 3, []int{})
	if cost != -1 || len(path) != 0 {
		t.Errorf("Expected no path when end location does not exist, got path %v with cost %d", path, cost)
	}
}

func TestConcurrency(t *testing.T) {
	pf := NewPathfinder()
	var wg sync.WaitGroup

	// Concurrently add 100 locations.
	for i := 1; i <= 100; i++ {
		wg.Add(1)
		go func(id int) {
			pf.AddLocation(id)
			wg.Done()
		}(i)
	}
	wg.Wait()

	// Concurrently add roads connecting consecutive locations.
	for i := 1; i < 100; i++ {
		wg.Add(1)
		go func(from int) {
			pf.AddRoad(from, from+1, from)
			wg.Done()
		}(i)
	}
	wg.Wait()

	// Query the path from 1 to 100.
	path, cost := pf.FindShortestPath(1, 100, []int{})
	if len(path) == 0 || path[0] != 1 || path[len(path)-1] != 100 {
		t.Errorf("Path does not start at 1 or end at 100: %v", path)
	}

	// Verify the total cost is the sum of costs from 1 to 99.
	expectedCost := 0
	for i := 1; i < 100; i++ {
		expectedCost += i
	}
	if cost != expectedCost {
		t.Errorf("Expected total cost %d, got %d", expectedCost, cost)
	}
}