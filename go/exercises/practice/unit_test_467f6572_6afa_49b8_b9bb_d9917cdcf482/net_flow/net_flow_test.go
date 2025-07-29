package net_flow

import (
	"testing"
)

func TestNetFlow(t *testing.T) {
	tests := []struct {
		name     string
		servers  int
		edges    [][]int
		requests [][]int
		want     int
	}{
		{
			name:    "simple case",
			servers: 4,
			edges: [][]int{
				{0, 1, 10},
				{0, 2, 5},
				{1, 3, 10},
				{2, 3, 15},
			},
			requests: [][]int{
				{0, 3, 7},
				{0, 3, 8},
				{1, 2, 5},
			},
			want: 1,
		},
		{
			name:    "no rejections needed",
			servers: 3,
			edges: [][]int{
				{0, 1, 10},
				{1, 2, 10},
			},
			requests: [][]int{
				{0, 2, 5},
				{0, 2, 4},
			},
			want: 0,
		},
		{
			name:    "all requests must be rejected",
			servers: 2,
			edges: [][]int{
				{0, 1, 1},
			},
			requests: [][]int{
				{0, 1, 2},
				{0, 1, 3},
			},
			want: 2,
		},
		{
			name:    "disconnected graph",
			servers: 4,
			edges: [][]int{
				{0, 1, 10},
				{2, 3, 10},
			},
			requests: [][]int{
				{0, 3, 5},
				{1, 2, 5},
			},
			want: 2,
		},
		{
			name:    "multiple paths",
			servers: 5,
			edges: [][]int{
				{0, 1, 10},
				{0, 2, 10},
				{1, 3, 5},
				{2, 3, 15},
				{3, 4, 10},
			},
			requests: [][]int{
				{0, 4, 10},
				{0, 4, 5},
				{1, 4, 5},
			},
			want: 0,
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			if got := MinRejectedRequests(tt.servers, tt.edges, tt.requests); got != tt.want {
				t.Errorf("MinRejectedRequests() = %v, want %v", got, tt.want)
			}
		})
	}
}

func BenchmarkMinRejectedRequests(b *testing.B) {
	servers := 100
	edges := make([][]int, 0)
	for i := 0; i < servers-1; i++ {
		edges = append(edges, []int{i, i + 1, 10})
	}
	requests := make([][]int, 0)
	for i := 0; i < 1000; i++ {
		requests = append(requests, []int{0, servers - 1, 5})
	}

	b.ResetTimer()
	for i := 0; i < b.N; i++ {
		MinRejectedRequests(servers, edges, requests)
	}
}