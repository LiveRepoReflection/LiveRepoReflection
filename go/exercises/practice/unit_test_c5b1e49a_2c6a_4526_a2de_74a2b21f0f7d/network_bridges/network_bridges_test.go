package network_bridges

import (
	"testing"
)

func TestNetworkBridges(t *testing.T) {
	tests := []struct {
		name           string
		n              int
		edges          [][]int
		connectTests   []struct{ a, b int; want bool }
		criticalLinks  [][]int
	}{
		{
			name: "single node",
			n:    1,
			edges: [][]int{},
			connectTests: []struct{ a, b int; want bool }{
				{0, 0, true},
			},
			criticalLinks: [][]int{},
		},
		{
			name: "two disconnected nodes",
			n:    2,
			edges: [][]int{},
			connectTests: []struct{ a, b int; want bool }{
				{0, 1, false},
			},
			criticalLinks: [][]int{},
		},
		{
			name: "simple connected graph",
			n:    4,
			edges: [][]int{{0, 1}, {1, 2}, {2, 3}},
			connectTests: []struct{ a, b int; want bool }{
				{0, 3, true},
				{1, 2, true},
			},
			criticalLinks: [][]int{{0, 1}, {1, 2}, {2, 3}},
		},
		{
			name: "graph with cycle",
			n:    5,
			edges: [][]int{{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}},
			connectTests: []struct{ a, b int; want bool }{
				{0, 4, true},
				{2, 3, true},
			},
			criticalLinks: [][]int{{1, 3}, {3, 4}},
		},
		{
			name: "multiple components",
			n:    6,
			edges: [][]int{{0, 1}, {1, 2}, {3, 4}, {4, 5}},
			connectTests: []struct{ a, b int; want bool }{
				{0, 2, true},
				{3, 5, true},
				{0, 3, false},
				{2, 4, false},
			},
			criticalLinks: [][]int{{0, 1}, {1, 2}, {3, 4}, {4, 5}},
		},
		{
			name: "complex graph with multiple bridges",
			n:    7,
			edges: [][]int{{0, 1}, {1, 2}, {2, 0}, {1, 3}, {3, 4}, {4, 5}, {5, 3}, {3, 6}},
			connectTests: []struct{ a, b int; want bool }{
				{0, 6, true},
				{4, 5, true},
				{2, 6, true},
			},
			criticalLinks: [][]int{{1, 3}, {3, 6}},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			net := NewNetwork(tt.n, tt.edges)

			// Test connectivity
			for _, ct := range tt.connectTests {
				got := net.isConnected(ct.a, ct.b)
				if got != ct.want {
					t.Errorf("isConnected(%d, %d) = %v, want %v", ct.a, ct.b, got, ct.want)
				}
			}

			// Test critical links
			gotLinks := net.getCriticalLinks()
			if !compareLinks(gotLinks, tt.criticalLinks) {
				t.Errorf("getCriticalLinks() = %v, want %v", gotLinks, tt.criticalLinks)
			}
		})
	}
}

func compareLinks(a, b [][]int) bool {
	if len(a) != len(b) {
		return false
	}

	linkMap := make(map[[2]int]bool)
	for _, link := range a {
		u, v := link[0], link[1]
		if u > v {
			u, v = v, u
		}
		linkMap[[2]int{u, v}] = true
	}

	for _, link := range b {
		u, v := link[0], link[1]
		if u > v {
			u, v = v, u
		}
		if !linkMap[[2]int{u, v}] {
			return false
		}
	}

	return true
}