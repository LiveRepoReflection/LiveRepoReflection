package network_split

import (
	"reflect"
	"testing"
)

func TestNetworkSplit(t *testing.T) {
	tests := []struct {
		name       string
		n          int
		m          int
		M          int
		k          int
		resilience []int
		edges      [][]float64
		want       []int
		wantNil    bool
	}{
		{
			name:       "Simple two-cluster network",
			n:          4,
			m:          2,
			M:          2,
			k:          2,
			resilience: []int{10, 10, 20, 20},
			edges: [][]float64{
				{0, 1, 0.9},
				{2, 3, 0.8},
				{1, 2, 0.5},
			},
			want: []int{0, 0, 1, 1},
		},
		{
			name:       "Impossible partitioning",
			n:          3,
			m:          2,
			M:          2,
			k:          2,
			resilience: []int{10, 10, 10},
			edges: [][]float64{
				{0, 1, 0.9},
				{1, 2, 0.8},
			},
			wantNil: true,
		},
		{
			name:       "Three clusters with size constraints",
			n:          6,
			m:          1,
			M:          3,
			k:          3,
			resilience: []int{10, 10, 20, 20, 30, 30},
			edges: [][]float64{
				{0, 1, 0.9},
				{1, 2, 0.8},
				{2, 3, 0.7},
				{3, 4, 0.6},
				{4, 5, 0.5},
			},
			want: []int{0, 0, 1, 1, 2, 2},
		},
		{
			name:       "Disconnected graph",
			n:          4,
			m:          1,
			M:          2,
			k:          2,
			resilience: []int{10, 10, 20, 20},
			edges: [][]float64{
				{0, 1, 0.9},
				{2, 3, 0.8},
			},
			want: []int{0, 0, 1, 1},
		},
		{
			name:       "All zero resilience scores",
			n:          4,
			m:          2,
			M:          2,
			k:          2,
			resilience: []int{0, 0, 0, 0},
			edges: [][]float64{
				{0, 1, 0.9},
				{1, 2, 0.8},
				{2, 3, 0.7},
			},
			want: []int{0, 0, 1, 1},
		},
		{
			name:       "All zero reliability scores",
			n:          4,
			m:          2,
			M:          2,
			k:          2,
			resilience: []int{10, 10, 20, 20},
			edges: [][]float64{
				{0, 1, 0.0},
				{1, 2, 0.0},
				{2, 3, 0.0},
			},
			want: []int{0, 0, 1, 1},
		},
	}

	for _, tt := range tests {
		t.Run(tt.name, func(t *testing.T) {
			got := SplitNetwork(tt.n, tt.m, tt.M, tt.k, tt.resilience, tt.edges)
			if tt.wantNil {
				if got != nil {
					t.Errorf("SplitNetwork() = %v, want nil", got)
				}
				return
			}
			if !reflect.DeepEqual(got, tt.want) {
				t.Errorf("SplitNetwork() = %v, want %v", got, tt.want)
			}
			if !isValidPartitioning(tt.n, tt.m, tt.M, tt.k, tt.resilience, tt.edges, got) {
				t.Error("Invalid partitioning")
			}
		})
	}
}

// Helper function to validate the partitioning
func isValidPartitioning(n, m, M, k int, resilience []int, edges [][]float64, partition []int) bool {
	if len(partition) != n {
		return false
	}

	// Check cluster size constraints
	clusterSizes := make(map[int]int)
	for _, cluster := range partition {
		if cluster < 0 || cluster >= k {
			return false
		}
		clusterSizes[cluster]++
	}
	for _, size := range clusterSizes {
		if size < m || size > M {
			return false
		}
	}

	// Check connectivity within clusters
	for cluster := 0; cluster < k; cluster++ {
		if !isConnectedCluster(n, edges, partition, cluster) {
			return false
		}
	}

	return true
}

// Helper function to check if a cluster is connected
func isConnectedCluster(n int, edges [][]float64, partition []int, cluster int) bool {
	// Create adjacency list for the cluster
	adj := make(map[int][]int)
	for _, edge := range edges {
		u, v := int(edge[0]), int(edge[1])
		if partition[u] == cluster && partition[v] == cluster {
			adj[u] = append(adj[u], v)
			adj[v] = append(adj[v], u)
		}
	}

	// Find first node in cluster
	start := -1
	for i := 0; i < n; i++ {
		if partition[i] == cluster {
			start = i
			break
		}
	}
	if start == -1 {
		return true
	}

	// BFS to check connectivity
	visited := make(map[int]bool)
	queue := []int{start}
	visited[start] = true

	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:]

		for _, next := range adj[curr] {
			if !visited[next] {
				visited[next] = true
				queue = append(queue, next)
			}
		}
	}

	// Check if all nodes in cluster are visited
	for i := 0; i < n; i++ {
		if partition[i] == cluster && !visited[i] {
			return false
		}
	}

	return true
}