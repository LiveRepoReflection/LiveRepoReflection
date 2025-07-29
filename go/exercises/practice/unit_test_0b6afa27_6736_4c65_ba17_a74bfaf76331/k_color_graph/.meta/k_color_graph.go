package k_color_graph

// IsKColorable determines if an undirected graph with n nodes (labeled 0 to n-1)
// and given edges is k-colorable. The graph is represented as a slice of edges,
// where each edge is a slice of 2 integers [u, v] indicating an undirected edge between u and v.
// A self-loop (an edge from a node to itself) causes the graph to be non-k-colorable.
// An empty graph (n == 0) is considered k-colorable.
func IsKColorable(n int, edges [][]int, k int) bool {
	// An empty graph is k-colorable.
	if n == 0 {
		return true
	}

	// Create an adjacency list for the graph.
	graph := make([][]int, n)
	for _, e := range edges {
		if len(e) != 2 {
			// If the edge does not have exactly 2 vertices, skip it.
			continue
		}
		u, v := e[0], e[1]
		// If there's a self-loop, the graph cannot be colored.
		if u == v {
			return false
		}
		// Assuming valid vertices according to constraints.
		graph[u] = append(graph[u], v)
		graph[v] = append(graph[v], u)
	}

	// colors[i] will hold the color assigned to node i (1-based). 0 means uncolored.
	colors := make([]int, n)

	// dfs attempts to assign a color to each node recursively.
	var dfs func(int) bool
	dfs = func(node int) bool {
		if node == n {
			// All nodes have been colored successfully.
			return true
		}
		// Try every color from 1 to k.
		for col := 1; col <= k; col++ {
			valid := true
			// Check all neighbors of the current node.
			for _, neighbor := range graph[node] {
				if colors[neighbor] == col {
					valid = false
					break
				}
			}
			if valid {
				colors[node] = col
				if dfs(node + 1) {
					return true
				}
				// Backtrack by unassigning the color.
				colors[node] = 0
			}
		}
		// If no color can be assigned to this node, return false.
		return false
	}

	return dfs(0)
}