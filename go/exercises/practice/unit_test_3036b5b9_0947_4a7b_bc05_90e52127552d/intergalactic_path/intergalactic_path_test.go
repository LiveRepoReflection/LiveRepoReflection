package intergalactic

import (
	"testing"
)

func TestBasicPathOperations(t *testing.T) {
	network := NewNetwork()

	// Test adding planets
	network.AddPlanet(1)
	network.AddPlanet(2)
	network.AddPlanet(3)

	// Test adding stargates
	network.AddStargate(1, 2, 5)
	network.AddStargate(2, 3, 3)

	// Test basic path query
	if cost := network.QueryShortestPath(1, 3); cost != 8 {
		t.Errorf("Expected shortest path cost of 8, got %d", cost)
	}
}

func TestMultipleStargates(t *testing.T) {
	network := NewNetwork()

	// Setup initial network
	network.AddPlanet(1)
	network.AddPlanet(2)
	network.AddPlanet(3)
	
	// Add multiple stargates between same planets
	network.AddStargate(1, 2, 5)
	network.AddStargate(1, 2, 3) // Lower cost path
	network.AddStargate(2, 3, 4)

	if cost := network.QueryShortestPath(1, 3); cost != 7 {
		t.Errorf("Expected shortest path cost of 7, got %d", cost)
	}
}

func TestPlanetRemoval(t *testing.T) {
	network := NewNetwork()

	// Setup network
	network.AddPlanet(1)
	network.AddPlanet(2)
	network.AddPlanet(3)
	network.AddStargate(1, 2, 5)
	network.AddStargate(2, 3, 3)

	// Remove middle planet
	network.RemovePlanet(2)

	// Path should no longer exist
	if cost := network.QueryShortestPath(1, 3); cost != -1 {
		t.Errorf("Expected no path (-1), got %d", cost)
	}
}

func TestStargateOperations(t *testing.T) {
	network := NewNetwork()

	// Setup network
	network.AddPlanet(1)
	network.AddPlanet(2)
	network.AddPlanet(3)
	network.AddStargate(1, 2, 5)
	network.AddStargate(2, 3, 3)

	// Update stargate cost
	network.UpdateStargateCost(1, 2, 5, 2)

	if cost := network.QueryShortestPath(1, 3); cost != 5 {
		t.Errorf("Expected shortest path cost of 5, got %d", cost)
	}

	// Remove stargate
	network.RemoveStargate(1, 2, 2)

	if cost := network.QueryShortestPath(1, 3); cost != -1 {
		t.Errorf("Expected no path (-1), got %d", cost)
	}
}

func TestLargeNetwork(t *testing.T) {
	network := NewNetwork()
	
	// Create a large network
	for i := 1; i <= 1000; i++ {
		network.AddPlanet(i)
	}

	// Add stargates in a ring topology
	for i := 1; i < 1000; i++ {
		network.AddStargate(i, i+1, 1)
	}
	network.AddStargate(1000, 1, 1) // Complete the ring

	// Test path finding in large network
	if cost := network.QueryShortestPath(1, 500); cost != 499 {
		t.Errorf("Expected shortest path cost of 499, got %d", cost)
	}
}

func TestEdgeCases(t *testing.T) {
	network := NewNetwork()

	// Test operations with non-existent planets
	network.RemovePlanet(1) // Should not panic
	network.AddStargate(1, 2, 5) // Should be ignored

	network.AddPlanet(1)
	network.AddPlanet(2)

	// Test duplicate operations
	network.AddPlanet(1) // Should be ignored
	network.AddStargate(1, 2, 5)
	network.AddStargate(1, 2, 5) // Should be ignored

	// Test invalid stargate operations
	network.RemoveStargate(1, 2, 3) // Non-existent cost
	network.UpdateStargateCost(1, 2, 3, 4) // Non-existent old cost

	// Test self-loops
	network.AddStargate(1, 1, 5)
	if cost := network.QueryShortestPath(1, 1); cost != 0 {
		t.Errorf("Expected self-loop cost of 0, got %d", cost)
	}
}

func TestComplexTopology(t *testing.T) {
	network := NewNetwork()

	// Create a complex network topology
	for i := 1; i <= 5; i++ {
		network.AddPlanet(i)
	}

	// Add stargates forming multiple possible paths
	network.AddStargate(1, 2, 2)
	network.AddStargate(2, 3, 3)
	network.AddStargate(3, 4, 1)
	network.AddStargate(4, 5, 4)
	network.AddStargate(1, 3, 7)
	network.AddStargate(2, 4, 6)
	network.AddStargate(3, 5, 3)
	network.AddStargate(1, 5, 20)

	// Test shortest path in complex topology
	if cost := network.QueryShortestPath(1, 5); cost != 8 {
		t.Errorf("Expected shortest path cost of 8, got %d", cost)
	}
}

func TestPerformance(t *testing.T) {
	network := NewNetwork()
	
	// Create a large network with multiple paths
	for i := 1; i <= 10000; i++ {
		network.AddPlanet(i)
	}

	// Add regular connections
	for i := 1; i < 10000; i++ {
		network.AddStargate(i, i+1, 1)
	}

	// Add some random long-distance connections
	for i := 1; i <= 1000; i++ {
		start := (i * 7) % 10000 + 1
		end := (i * 13) % 10000 + 1
		network.AddStargate(start, end, i%100+1)
	}

	// Perform multiple queries to test performance
	for i := 0; i < 1000; i++ {
		start := (i * 17) % 10000 + 1
		end := (i * 23) % 10000 + 1
		if cost := network.QueryShortestPath(start, end); cost == -1 {
			t.Errorf("Expected a valid path between %d and %d", start, end)
		}
	}
}