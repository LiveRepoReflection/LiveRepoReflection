package network_pathfinder

type Edge struct {
	to      int
	latency int
}

func findPaths(n int, cables [][]int, queries [][]int) []int {
	graph := make([][]Edge, n)
	for _, cable := range cables {
		u, v, l := cable[0], cable[1], cable[2]
		graph[u] = append(graph[u], Edge{to: v, latency: l})
		graph[v] = append(graph[v], Edge{to: u, latency: l})
	}

	results := make([]int, 0, len(queries))
	for _, query := range queries {
		src, dst, maxCables, allowedLatency := query[0], query[1], query[2], query[3]
		if src == dst {
			results = append(results, 1)
			continue
		}
		visited := make([]bool, n)
		visited[src] = true
		count := dfs(src, dst, 0, maxCables, 0, allowedLatency, visited, graph)
		results = append(results, count)
	}
	return results
}

func dfs(cur, dst, usedEdges, maxEdges, currentLatency, allowedLatency int, visited []bool, graph [][]Edge) int {
	count := 0
	for _, edge := range graph[cur] {
		nextNode := edge.to
		nextLatency := currentLatency + edge.latency
		if usedEdges+1 > maxEdges || nextLatency > allowedLatency {
			continue
		}
		if visited[nextNode] {
			continue
		}
		if nextNode == dst {
			count++
		}
		visited[nextNode] = true
		count += dfs(nextNode, dst, usedEdges+1, maxEdges, nextLatency, allowedLatency, visited, graph)
		visited[nextNode] = false
	}
	return count
}