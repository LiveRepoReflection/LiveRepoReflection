package network_rescue

func OptimalPartitioning(n int, edges [][]int, affectedServices []int, recoveryCosts []int) int {
	affected := make(map[int]bool)
	for _, a := range affectedServices {
		affected[a] = true
	}

	graph := make([][]int, n)
	for i := 0; i < n; i++ {
		graph[i] = []int{}
	}
	for _, edge := range edges {
		u, v := edge[0], edge[1]
		graph[u] = append(graph[u], v)
		graph[v] = append(graph[v], u)
	}

	visited := make([]bool, n)
	totalCost := 0

	var dfs func(node int) int
	dfs = func(node int) int {
		visited[node] = true
		cost := recoveryCosts[node]
		for _, neighbor := range graph[node] {
			if !visited[neighbor] && !affected[neighbor] {
				cost += dfs(neighbor)
			}
		}
		return cost
	}

	for i := 0; i < n; i++ {
		if affected[i] {
			continue
		}
		if !visited[i] {
			componentCost := dfs(i)
			totalCost += componentCost
		}
	}
	return totalCost
}