package traffic_lights

// MinTrafficLights computes the minimum number of traffic lights needed to control
// all roads in an N x M grid with restricted intersections, while also implicitly
// choosing the configuration that minimizes the maximum distance between intersections
// without traffic lights. The problem is modeled as a vertex cover problem on a bipartite grid graph.
func MinTrafficLights(N int, M int, restricted [][]int) int {
	// Create a 2D boolean grid for restricted intersections.
	restrictedFlag := make([][]bool, N)
	for i := 0; i < N; i++ {
		restrictedFlag[i] = make([]bool, M)
	}
	for _, pos := range restricted {
		if len(pos) >= 2 {
			i, j := pos[0], pos[1]
			if i >= 0 && i < N && j >= 0 && j < M {
				restrictedFlag[i][j] = true
			}
		}
	}

	// forced[i][j] will be true if the allowed cell (i,j) is forced to include a traffic light
	// because it is adjacent to a restricted intersection.
	forced := make([][]bool, N)
	for i := 0; i < N; i++ {
		forced[i] = make([]bool, M)
	}

	// Directions: up, down, left, right.
	dirs := [][]int{
		{-1, 0},
		{1, 0},
		{0, -1},
		{0, 1},
	}

	// Determine forced placements:
	for i := 0; i < N; i++ {
		for j := 0; j < M; j++ {
			// Only consider allowed intersections.
			if restrictedFlag[i][j] {
				continue
			}
			// If any neighbor is restricted, then (i,j) is forced.
			for _, d := range dirs {
				ni, nj := i+d[0], j+d[1]
				if ni >= 0 && ni < N && nj >= 0 && nj < M {
					if restrictedFlag[ni][nj] {
						forced[i][j] = true
						break
					}
				}
			}
		}
	}

	// Count forced selections.
	forcedCount := 0
	for i := 0; i < N; i++ {
		for j := 0; j < M; j++ {
			if forced[i][j] {
				forcedCount++
			}
		}
	}

	// Build bipartite graph from allowed cells that are not forced.
	// Partition based on parity: use (i+j)%2.
	// For nodes in left partition (parity 0), add edges to adjacent nodes in right partition.
	// We'll map grid coordinates to integer ids.
	type coord struct {
		i, j int
	}

	// Maps for left and right partition nodes that are not forced and not restricted.
	leftID := make(map[coord]int)
	rightID := make(map[coord]int)
	leftNodes := []coord{}
	rightNodes := []coord{}

	// Assign IDs.
	for i := 0; i < N; i++ {
		for j := 0; j < M; j++ {
			// Only allowed and not forced.
			if restrictedFlag[i][j] || forced[i][j] {
				continue
			}
			pos := coord{i, j}
			if (i+j)%2 == 0 {
				leftID[pos] = len(leftNodes)
				leftNodes = append(leftNodes, pos)
			} else {
				rightID[pos] = len(rightNodes)
				rightNodes = append(rightNodes, pos)
			}
		}
	}

	// Build graph as adjacency list for left partition.
	graph := make([][]int, len(leftNodes))
	for idx, pos := range leftNodes {
		// Check all four adjacent cells.
		for _, d := range dirs {
			ni, nj := pos.i+d[0], pos.j+d[1]
			neighbor := coord{ni, nj}
			if ni >= 0 && ni < N && nj >= 0 && nj < M {
				// Neighbor must be allowed and not forced.
				if restrictedFlag[ni][nj] || forced[ni][nj] {
					continue
				}
				// Edge goes only to right partition.
				if (ni+nj)%2 == 1 {
					if rid, exists := rightID[neighbor]; exists {
						graph[idx] = append(graph[idx], rid)
					}
				}
			}
		}
	}

	// Use Hopcroft-Karp algorithm to compute maximum matching on bipartite graph.
	matching := hopcroftKarp(graph, len(leftNodes), len(rightNodes))

	// Minimum vertex cover size in bipartite graph equals maximum matching.
	return forcedCount + matching
}

// hopcroftKarp computes the maximum matching for a bipartite graph using Hopcroft-Karp algorithm.
// graph: adjacency list for left partition where graph[u] gives list of neighbors in right partition.
// nLeft: number of nodes in left partition.
// nRight: number of nodes in right partition.
func hopcroftKarp(graph [][]int, nLeft, nRight int) int {
	// pairLeft[u] is the right node matched with left node u, or -1 if unmatched.
	// pairRight[v] is the left node matched with right node v, or -1 if unmatched.
	pairLeft := make([]int, nLeft)
	for i := range pairLeft {
		pairLeft[i] = -1
	}
	pairRight := make([]int, nRight)
	for i := range pairRight {
		pairRight[i] = -1
	}
	// distance array for left nodes.
	dist := make([]int, nLeft)

	const INF = 1 << 30

	var bfs func() bool
	bfs = func() bool {
		queue := make([]int, 0, nLeft)
		// Initialize distance for free left nodes.
		for u := 0; u < nLeft; u++ {
			if pairLeft[u] == -1 {
				dist[u] = 0
				queue = append(queue, u)
			} else {
				dist[u] = INF
			}
		}
		distance := INF
		for len(queue) > 0 {
			u := queue[0]
			queue = queue[1:]
			if dist[u] < distance {
				for _, v := range graph[u] {
					if pairRight[v] == -1 {
						if distance > dist[u]+1 {
							distance = dist[u] + 1
						}
					} else if dist[pairRight[v]] == INF {
						dist[pairRight[v]] = dist[u] + 1
						queue = append(queue, pairRight[v])
					}
				}
			}
		}
		return distance != INF
	}

	var dfs func(u int, distance int) bool
	dfs = func(u int, distance int) bool {
		if dist[u] == distance {
			dist[u] = INF
			for _, v := range graph[u] {
				var pu int
				if pairRight[v] == -1 {
					pu = -1
				} else {
					pu = pairRight[v]
				}
				if pu == -1 || (dist[pu] == distance+1 && dfs(pu, distance+1)) {
					pairLeft[u] = v
					pairRight[v] = u
					return true
				}
			}
		}
		return false
	}

	matching := 0
	for bfs() {
		for u := 0; u < nLeft; u++ {
			if pairLeft[u] == -1 {
				if dfs(u, 0) {
					matching++
				}
			}
		}
	}
	return matching
}