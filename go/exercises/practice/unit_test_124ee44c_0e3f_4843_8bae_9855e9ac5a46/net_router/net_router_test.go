package net_router_test

import (
	"sync"
	"testing"

	"net_router"
)

func TestBasicRouting(t *testing.T) {
	router := net_router.NewNetworkRouter()

	// Add devices A, B, C.
	router.AddDevice("A")
	router.AddDevice("B")
	router.AddDevice("C")

	// Add connections: A->B (10), B->C (15), A->C (50).
	router.AddConnection("A", "B", 10)
	router.AddConnection("B", "C", 15)
	router.AddConnection("A", "C", 50)

	router.UpdateRoutingTable()

	// Test same source and destination.
	nh, cost, reachable := router.GetNextHop("A", "A")
	if nh != "A" || cost != 0 || !reachable {
		t.Errorf(`Expected ("A", 0, true) for GetNextHop("A", "A"), got (%q, %d, %v)`, nh, cost, reachable)
	}

	// Test direct routing: A -> B.
	nh, cost, reachable = router.GetNextHop("A", "B")
	if nh != "B" || cost != 10 || !reachable {
		t.Errorf(`Expected ("B", 10, true) for GetNextHop("A", "B"), got (%q, %d, %v)`, nh, cost, reachable)
	}

	// Test multi-hop routing: A -> C.
	// Two possible paths: Direct A->C (50) and A->B->C (10+15=25).
	// Shortest path should be chosen: next hop from A should be "B" with cost 25.
	nh, cost, reachable = router.GetNextHop("A", "C")
	if nh != "B" || cost != 25 || !reachable {
		t.Errorf(`Expected ("B", 25, true) for GetNextHop("A", "C"), got (%q, %d, %v)`, nh, cost, reachable)
	}

	// Test unreachable scenario: B -> A should be unreachable.
	nh, cost, reachable = router.GetNextHop("B", "A")
	if reachable {
		t.Errorf(`Expected GetNextHop("B", "A") to be unreachable, got (%q, %d, %v)`, nh, cost, reachable)
	}
}

func TestRemoveConnection(t *testing.T) {
	router := net_router.NewNetworkRouter()

	// Add devices.
	router.AddDevice("A")
	router.AddDevice("B")
	router.AddDevice("C")

	// Add connections.
	router.AddConnection("A", "B", 10)
	router.AddConnection("B", "C", 15)
	router.AddConnection("A", "C", 50)

	router.UpdateRoutingTable()

	// Remove direct connection A->C.
	router.RemoveConnection("A", "C")
	router.UpdateRoutingTable()

	// Now, path A -> C should be via A->B->C with cost 10+15=25.
	nh, cost, reachable := router.GetNextHop("A", "C")
	if nh != "B" || cost != 25 || !reachable {
		t.Errorf(`Expected ("B", 25, true) for GetNextHop("A", "C") after removal, got (%q, %d, %v)`, nh, cost, reachable)
	}
}

func TestRemoveDevice(t *testing.T) {
	router := net_router.NewNetworkRouter()

	// Add devices.
	router.AddDevice("A")
	router.AddDevice("B")
	router.AddDevice("C")
	router.AddDevice("D")

	// Add connections.
	router.AddConnection("A", "B", 5)
	router.AddConnection("B", "C", 10)
	router.AddConnection("C", "D", 20)
	router.AddConnection("A", "D", 40)

	router.UpdateRoutingTable()

	// Before removal, A -> D should follow the path A->B->C->D with cost 5+10+20 = 35.
	nh, cost, reachable := router.GetNextHop("A", "D")
	if nh != "B" || cost != 35 || !reachable {
		t.Errorf(`Expected ("B", 35, true) for GetNextHop("A", "D"), got (%q, %d, %v)`, nh, cost, reachable)
	}

	// Remove device B.
	router.RemoveDevice("B")
	router.UpdateRoutingTable()

	// After removal, the only connection from A to D is the direct one with cost 40.
	nh, cost, reachable = router.GetNextHop("A", "D")
	if nh != "D" || cost != 40 || !reachable {
		t.Errorf(`Expected ("D", 40, true) for GetNextHop("A", "D") after removing B, got (%q, %d, %v)`, nh, cost, reachable)
	}

	// A -> C should become unreachable due to removal of B.
	nh, cost, reachable = router.GetNextHop("A", "C")
	if reachable {
		t.Errorf(`Expected GetNextHop("A", "C") to be unreachable after removing B, got (%q, %d, %v)`, nh, cost, reachable)
	}
}

func TestCycleRouting(t *testing.T) {
	router := net_router.NewNetworkRouter()

	// Add devices.
	router.AddDevice("A")
	router.AddDevice("B")
	router.AddDevice("C")

	// Create a cycle: A->B, B->C, and C->A.
	router.AddConnection("A", "B", 1)
	router.AddConnection("B", "C", 1)
	router.AddConnection("C", "A", 1)
	router.UpdateRoutingTable()

	// For A -> C, the expected path is A -> B -> C with total cost 2.
	nh, cost, reachable := router.GetNextHop("A", "C")
	if nh != "B" || cost != 2 || !reachable {
		t.Errorf(`Expected ("B", 2, true) for GetNextHop("A", "C") in cycle, got (%q, %d, %v)`, nh, cost, reachable)
	}

	// For B -> A, expected path is B -> C -> A with total cost 2.
	nh, cost, reachable = router.GetNextHop("B", "A")
	if nh != "C" || cost != 2 || !reachable {
		t.Errorf(`Expected ("C", 2, true) for GetNextHop("B", "A") in cycle, got (%q, %d, %v)`, nh, cost, reachable)
	}
}

func TestConcurrentUpdates(t *testing.T) {
	router := net_router.NewNetworkRouter()

	// Add multiple devices.
	devices := []string{"A", "B", "C", "D", "E"}
	for _, d := range devices {
		router.AddDevice(d)
	}

	// Concurrently add connections.
	var wg sync.WaitGroup
	connections := []struct {
		src  string
		dst  string
		cost int
	}{
		{"A", "B", 5},
		{"B", "C", 10},
		{"C", "D", 15},
		{"D", "E", 20},
		{"E", "A", 25},
	}

	for _, conn := range connections {
		wg.Add(1)
		go func(src, dst string, cost int) {
			defer wg.Done()
			router.AddConnection(src, dst, cost)
		}(conn.src, conn.dst, conn.cost)
	}
	wg.Wait()

	router.UpdateRoutingTable()

	// Concurrently check the routing.
	wg.Add(1)
	go func() {
		defer wg.Done()
		nh, cost, reachable := router.GetNextHop("A", "D")
		// Expected path: A -> B (5) -> C (10) -> D (15) = 30, so next hop from A should be "B".
		if nh != "B" || cost != 30 || !reachable {
			t.Errorf(`Expected ("B", 30, true) for GetNextHop("A", "D") in concurrent access, got (%q, %d, %v)`, nh, cost, reachable)
		}
	}()
	wg.Wait()
}