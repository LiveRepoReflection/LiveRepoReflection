package network_topology

import (
	"reflect"
	"sort"
	"testing"
)

// Helper type for testing critical edges
type testEdge struct {
	From    int
	To      int
	Latency int
}

// sortTestEdges sorts a slice of testEdge by (From, To, Latency)
func sortTestEdges(edges []testEdge) {
	sort.Slice(edges, func(i, j int) bool {
		if edges[i].From != edges[j].From {
			return edges[i].From < edges[j].From
		}
		if edges[i].To != edges[j].To {
			return edges[i].To < edges[j].To
		}
		return edges[i].Latency < edges[j].Latency
	})
}

// convertEdges converts a slice of Edge (from implementation) to []testEdge.
// It assumes the existence of a type Edge with fields From, To, and Latency.
func convertEdges(edges []Edge) []testEdge {
	var res []testEdge
	for _, e := range edges {
		res = append(res, testEdge{From: e.From, To: e.To, Latency: e.Latency})
	}
	return res
}

func TestAddEdgeInvalid(t *testing.T) {
	// Create a network with 3 nodes: 0,1,2.
	net, err := NewNetwork(3)
	if err != nil {
		t.Fatalf("NewNetwork error: %v", err)
	}
	// Adding an edge with an invalid target node index.
	if err := net.AddEdge(0, 3, 10); err == nil {
		t.Fatalf("expected error when adding edge with invalid node index, got nil")
	}
	// Adding an edge with an invalid source node index.
	if err := net.AddEdge(-1, 1, 5); err == nil {
		t.Fatalf("expected error when adding edge with invalid node index, got nil")
	}
}

func TestConnectivity(t *testing.T) {
	// Build a network:
	// 0 -> 1, 1 -> 2, 2 -> 0 (cycle) and 1 -> 3 (branch)
	net, err := NewNetwork(4)
	if err != nil {
		t.Fatalf("NewNetwork error: %v", err)
	}
	edges := []struct {
		u, v, latency int
	}{
		{0, 1, 5},
		{1, 2, 10},
		{2, 0, 7},
		{1, 3, 3},
	}
	for _, ed := range edges {
		if err := net.AddEdge(ed.u, ed.v, ed.latency); err != nil {
			t.Fatalf("AddEdge(%d, %d, %d) error: %v", ed.u, ed.v, ed.latency, err)
		}
	}
	// Test connectivity inside cycle
	if !net.Connected(0, 2) {
		t.Fatalf("expected 0 and 2 to be connected")
	}
	// Test connectivity through branch
	if !net.Connected(0, 3) {
		t.Fatalf("expected 0 and 3 to be connected")
	}
	// Test non-existent connectivity
	if net.Connected(3, 0) {
		t.Fatalf("expected 3 and 0 not to be connected in directed graph")
	}
}

func TestLatencyEstimation(t *testing.T) {
	// Build a network with parallel paths.
	// Structure:
	// 0 -> 1 with latency 10; 0 -> 1 with latency 5; 1 -> 2 with latency 7; 0 -> 2 with latency 20.
	net, err := NewNetwork(3)
	if err != nil {
		t.Fatalf("NewNetwork error: %v", err)
	}
	// Add parallel edges: only smallest latency should be considered.
	if err := net.AddEdge(0, 1, 10); err != nil {
		t.Fatalf("AddEdge error: %v", err)
	}
	if err := net.AddEdge(0, 1, 5); err != nil {
		t.Fatalf("AddEdge error: %v", err)
	}
	if err := net.AddEdge(1, 2, 7); err != nil {
		t.Fatalf("AddEdge error: %v", err)
	}
	if err := net.AddEdge(0, 2, 20); err != nil {
		t.Fatalf("AddEdge error: %v", err)
	}
	// Expected minimum latency from 0 to 2 is via 0->1 (5) and 1->2 (7): total 12.
	latency := net.MinLatency(0, 2)
	if latency != 12 {
		t.Fatalf("expected latency 12, got %d", latency)
	}
	// Test unreachable nodes.
	if latency = net.MinLatency(2, 0); latency != -1 {
		t.Fatalf("expected latency -1 for unreachable nodes, got %d", latency)
	}
}

func TestRemoveEdge(t *testing.T) {
	// Build a network:
	// 0 -> 1, 1 -> 2, and 0 -> 2.
	net, err := NewNetwork(3)
	if err != nil {
		t.Fatalf("NewNetwork error: %v", err)
	}
	if err := net.AddEdge(0, 1, 4); err != nil {
		t.Fatalf("AddEdge error: %v", err)
	}
	if err := net.AddEdge(1, 2, 6); err != nil {
		t.Fatalf("AddEdge error: %v", err)
	}
	if err := net.AddEdge(0, 2, 15); err != nil {
		t.Fatalf("AddEdge error: %v", err)
	}

	// Initially, connectivity from 0 to 2 should exist and minimum latency should be 10.
	if !net.Connected(0, 2) {
		t.Fatalf("expected 0 and 2 to be connected")
	}
	if latency := net.MinLatency(0, 2); latency != 10 {
		t.Fatalf("expected latency 10, got %d", latency)
	}

	// Remove edge 1 -> 2, now the only path is direct edge 0->2 with latency 15.
	if err := net.RemoveEdge(1, 2); err != nil {
		t.Fatalf("RemoveEdge error: %v", err)
	}
	if !net.Connected(0, 2) {
		t.Fatalf("expected 0 and 2 to be connected after removal")
	}
	if latency := net.MinLatency(0, 2); latency != 15 {
		t.Fatalf("expected latency 15 after removal, got %d", latency)
	}

	// Remove direct edge 0->2, now 0 and 2 should be disconnected.
	if err := net.RemoveEdge(0, 2); err != nil {
		t.Fatalf("RemoveEdge error: %v", err)
	}
	if net.Connected(0, 2) {
		t.Fatalf("expected 0 and 2 to be disconnected after removal")
	}
	if latency := net.MinLatency(0, 2); latency != -1 {
		t.Fatalf("expected latency -1 for disconnected nodes, got %d", latency)
	}
}

func TestSelfLoop(t *testing.T) {
	// Build a network and add a self-loop; ensure connectivity and latency behaves as expected.
	net, err := NewNetwork(2)
	if err != nil {
		t.Fatalf("NewNetwork error: %v", err)
	}
	if err := net.AddEdge(0, 0, 3); err != nil {
		t.Fatalf("AddEdge self-loop error: %v", err)
	}
	if err := net.AddEdge(0, 1, 5); err != nil {
		t.Fatalf("AddEdge error: %v", err)
	}
	// Self-loop should not affect connectivity from 0 to 1.
	if !net.Connected(0, 1) {
		t.Fatalf("expected 0 and 1 to be connected")
	}
	if latency := net.MinLatency(0, 1); latency != 5 {
		t.Fatalf("expected latency 5, got %d", latency)
	}
	// Self-loop connectivity: 0 should be connected to itself with 0 or self-loop cost.
	// Depending on implementation, MinLatency(0,0) could be 0.
	if latency := net.MinLatency(0, 0); latency != 0 && latency != 3 {
		t.Fatalf("expected latency 0 or 3 for self-loop, got %d", latency)
	}
}

func TestCycle(t *testing.T) {
	// Build a network with a cycle: 0->1, 1->2, 2->0.
	net, err := NewNetwork(3)
	if err != nil {
		t.Fatalf("NewNetwork error: %v", err)
	}
	edges := []struct {
		u, v, latency int
	}{
		{0, 1, 2},
		{1, 2, 3},
		{2, 0, 4},
	}
	for _, ed := range edges {
		if err := net.AddEdge(ed.u, ed.v, ed.latency); err != nil {
			t.Fatalf("AddEdge(%d, %d, %d) error: %v", ed.u, ed.v, ed.latency, err)
		}
	}
	// Test connectivity in cycle
	for i := 0; i < 3; i++ {
		if !net.Connected(i, (i+1)%3) {
			t.Fatalf("expected nodes %d and %d to be connected", i, (i+1)%3)
		}
	}
	// Check latency estimation in presence of cycle.
	latency := net.MinLatency(0, 2)
	// Two possible paths: 0->1->2 (latency 5) or 0->(via cycle) but should choose shortest.
	if latency != 5 {
		t.Fatalf("expected latency 5 from 0 to 2, got %d", latency)
	}
}

func TestCriticalEdges(t *testing.T) {
	// Build a network:
	// 0 -> 1 (latency 4)
	// 1 -> 2 (latency 5)
	// 2 -> 3 (latency 6)
	// 0 -> 2 (latency 10)
	// In this configuration:
	// Removing edge 0->2 should not affect overall connectivity because 0->1->2 remains.
	// Removing edge 0->1, 1->2, or 2->3 would disconnect some nodes.
	net, err := NewNetwork(4)
	if err != nil {
		t.Fatalf("NewNetwork error: %v", err)
	}
	edges := []struct {
		u, v, latency int
	}{
		{0, 1, 4},
		{1, 2, 5},
		{2, 3, 6},
		{0, 2, 10},
	}
	for _, ed := range edges {
		if err := net.AddEdge(ed.u, ed.v, ed.latency); err != nil {
			t.Fatalf("AddEdge(%d, %d, %d) error: %v", ed.u, ed.v, ed.latency, err)
		}
	}
	critical := net.CriticalEdges()
	// Convert edges to our testEdge type.
	actualEdges := convertEdges(critical)
	// Expected critical edges are those whose removal disconnects the graph.
	// In this graph, edges 0->1, 1->2, and 2->3 are critical while 0->2 is not.
	expected := []testEdge{
		{From: 0, To: 1, Latency: 4},
		{From: 1, To: 2, Latency: 5},
		{From: 2, To: 3, Latency: 6},
	}

	sortTestEdges(actualEdges)
	sortTestEdges(expected)

	if !reflect.DeepEqual(actualEdges, expected) {
		t.Fatalf("expected critical edges %v, got %v", expected, actualEdges)
	}
}