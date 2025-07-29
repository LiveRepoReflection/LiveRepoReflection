package dav_network

import (
	"testing"
	"time"
)

func TestDAVNetworkInitialization(t *testing.T) {
	graph := Graph{
		Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}},
		Edges: []Edge{
			{From: 1, To: 2, Weight: 5},
			{From: 2, To: 3, Weight: 3},
			{From: 1, To: 3, Weight: 10},
		},
	}

	davs := []DAV{
		{ID: 1, Location: 1, PassengerCapacity: 4, CargoCapacity: 100, MaxBattery: 20, ProcessingPower: 10},
	}

	network := NewNetwork(graph, davs)
	if len(network.DAVs) != 1 {
		t.Errorf("Expected 1 DAV, got %d", len(network.DAVs))
	}
}

func TestRequestHandling(t *testing.T) {
	graph := Graph{
		Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}},
		Edges: []Edge{
			{From: 1, To: 2, Weight: 5},
			{From: 2, To: 3, Weight: 3},
			{From: 1, To: 3, Weight: 10},
		},
	}

	davs := []DAV{
		{ID: 1, Location: 1, PassengerCapacity: 4, CargoCapacity: 100, MaxBattery: 20, ProcessingPower: 10},
	}

	network := NewNetwork(graph, davs)

	requests := []Request{
		{ID: 1, Start: 1, End: 3, Type: PASSENGER, Quantity: 2, Deadline: time.Now().Add(30 * time.Minute), Reward: 50},
	}

	actions := network.HandleRequests(requests)
	if len(actions) == 0 {
		t.Error("Expected actions to be generated for request")
	}
}

func TestBatteryConstraints(t *testing.T) {
	graph := Graph{
		Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}},
		Edges: []Edge{
			{From: 1, To: 2, Weight: 5},
			{From: 2, To: 3, Weight: 3},
			{From: 1, To: 3, Weight: 10},
		},
	}

	davs := []DAV{
		{ID: 1, Location: 1, PassengerCapacity: 4, CargoCapacity: 100, MaxBattery: 8, ProcessingPower: 10},
	}

	network := NewNetwork(graph, davs)

	requests := []Request{
		{ID: 1, Start: 1, End: 3, Type: PASSENGER, Quantity: 2, Deadline: time.Now().Add(30 * time.Minute), Reward: 50},
	}

	actions := network.HandleRequests(requests)
	for _, action := range actions {
		if action.Type == PICKUP || action.Type == DELIVER {
			totalWeight := 0
			for i := 0; i < len(action.Path)-1; i++ {
				for _, edge := range graph.Edges {
					if (edge.From == action.Path[i] && edge.To == action.Path[i+1]) ||
						(edge.From == action.Path[i+1] && edge.To == action.Path[i]) {
						totalWeight += edge.Weight
						break
					}
				}
			}
			if totalWeight > davs[0].MaxBattery {
				t.Errorf("DAV battery constraint violated: required %d, available %d", totalWeight, davs[0].MaxBattery)
			}
		}
	}
}

func TestCapacityConstraints(t *testing.T) {
	graph := Graph{
		Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}},
		Edges: []Edge{
			{From: 1, To: 2, Weight: 5},
			{From: 2, To: 3, Weight: 3},
			{From: 1, To: 3, Weight: 10},
		},
	}

	davs := []DAV{
		{ID: 1, Location: 1, PassengerCapacity: 1, CargoCapacity: 100, MaxBattery: 20, ProcessingPower: 10},
	}

	network := NewNetwork(graph, davs)

	requests := []Request{
		{ID: 1, Start: 1, End: 3, Type: PASSENGER, Quantity: 2, Deadline: time.Now().Add(30 * time.Minute), Reward: 50},
	}

	actions := network.HandleRequests(requests)
	for _, action := range actions {
		if action.Type == PICKUP {
			t.Error("DAV should not pick up request that exceeds capacity")
		}
	}
}

func TestDeadlineConstraints(t *testing.T) {
	graph := Graph{
		Nodes: []Node{{ID: 1}, {ID: 2}, {ID: 3}},
		Edges: []Edge{
			{From: 1, To: 2, Weight: 5},
			{From: 2, To: 3, Weight: 3},
			{From: 1, To: 3, Weight: 10},
		},
	}

	davs := []DAV{
		{ID: 1, Location: 1, PassengerCapacity: 4, CargoCapacity: 100, MaxBattery: 20, ProcessingPower: 10},
	}

	network := NewNetwork(graph, davs)

	requests := []Request{
		{ID: 1, Start: 1, End: 3, Type: PASSENGER, Quantity: 2, Deadline: time.Now().Add(-10 * time.Minute), Reward: 50},
	}

	actions := network.HandleRequests(requests)
	for _, action := range actions {
		if action.Type == PICKUP {
			t.Error("DAV should not pick up expired request")
		}
	}
}