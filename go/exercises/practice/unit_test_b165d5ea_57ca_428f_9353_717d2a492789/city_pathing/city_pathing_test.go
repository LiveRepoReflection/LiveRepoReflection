package city_pathing

import (
	"testing"
	"time"
)

type mockTrafficAPI struct {
	signals map[int]string
}

func (m *mockTrafficAPI) GetSignalStates() map[int]string {
	return m.signals
}

func TestBasicPathfinding(t *testing.T) {
	graph := NewCityGraph()
	graph.AddIntersection(1)
	graph.AddIntersection(2)
	graph.AddRoad(1, 2, 100, false) // 100m road, not one-way

	api := &mockTrafficAPI{signals: map[int]string{1: "green", 2: "green"}}
	finder := NewPathFinder(graph, api)

	path, time, err := finder.FindPath(1, []int{2})
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if len(path) != 2 || path[0] != 1 || path[1] != 2 {
		t.Errorf("Incorrect path: %v", path)
	}
	if time != 100 {
		t.Errorf("Expected time 100, got %v", time)
	}
}

func TestTrafficSignalImpact(t *testing.T) {
	graph := NewCityGraph()
	graph.AddIntersection(1)
	graph.AddIntersection(2)
	graph.AddRoad(1, 2, 100, false)

	// Setup API with red light at intersection 1
	api := &mockTrafficAPI{signals: map[int]string{1: "red", 2: "green"}}
	finder := NewPathFinder(graph, api)

	_, time, _ := finder.FindPath(1, []int{2})
	// Red light should add significant delay
	if time <= 100 {
		t.Errorf("Expected increased time due to red light, got %v", time)
	}
}

func TestOneWayRoads(t *testing.T) {
	graph := NewCityGraph()
	graph.AddIntersection(1)
	graph.AddIntersection(2)
	graph.AddRoad(1, 2, 100, true) // One-way from 1 to 2

	api := &mockTrafficAPI{signals: map[int]string{1: "green", 2: "green"}}
	finder := NewPathFinder(graph, api)

	// Should fail to find reverse path
	_, _, err := finder.FindPath(2, []int{1})
	if err == nil {
		t.Error("Expected error for illegal one-way traversal")
	}
}

func TestMultiDestination(t *testing.T) {
	graph := NewCityGraph()
	graph.AddIntersection(1)
	graph.AddIntersection(2)
	graph.AddIntersection(3)
	graph.AddRoad(1, 2, 100, false)
	graph.AddRoad(2, 3, 100, false)
	graph.AddRoad(1, 3, 300, false) // Direct but longer path

	api := &mockTrafficAPI{signals: map[int]string{1: "green", 2: "green", 3: "green"}}
	finder := NewPathFinder(graph, api)

	path, time, err := finder.FindPath(1, []int{2, 3})
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	if len(path) != 3 || path[0] != 1 || path[1] != 2 || path[2] != 3 {
		t.Errorf("Incorrect path: %v", path)
	}
	if time != 200 {
		t.Errorf("Expected time 200, got %v", time)
	}
}

func TestDynamicUpdates(t *testing.T) {
	graph := NewCityGraph()
	graph.AddIntersection(1)
	graph.AddIntersection(2)
	graph.AddRoad(1, 2, 100, false)

	api := &mockTrafficAPI{signals: map[int]string{1: "green", 2: "green"}}
	finder := NewPathFinder(graph, api)

	// Initial path with normal conditions
	_, initialTime, _ := finder.FindPath(1, []int{2})

	// Simulate road condition update
	graph.UpdateRoadCondition(1, 2, 500) // Now takes 500m due to traffic

	_, updatedTime, _ := finder.FindPath(1, []int{2})
	if updatedTime <= initialTime {
		t.Errorf("Expected increased time after road condition update")
	}
}

func TestPerformance(t *testing.T) {
	// Create large graph
	graph := NewCityGraph()
	for i := 1; i <= 1000; i++ {
		graph.AddIntersection(i)
		if i > 1 {
			graph.AddRoad(i-1, i, 100, false)
		}
	}

	api := &mockTrafficAPI{signals: make(map[int]string)}
	for i := 1; i <= 1000; i++ {
		api.signals[i] = "green"
	}

	finder := NewPathFinder(graph, api)

	start := time.Now()
	_, _, err := finder.FindPath(1, []int{1000})
	if err != nil {
		t.Fatalf("Unexpected error: %v", err)
	}
	elapsed := time.Since(start)

	if elapsed > 500*time.Millisecond {
		t.Errorf("Pathfinding took too long: %v", elapsed)
	}
}