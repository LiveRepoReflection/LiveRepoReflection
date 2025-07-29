package async_routing

func FindPath(n int, adjacency [][]int, source int, destination int) []int {
	if source == destination {
		return []int{source}
	}

	visited := make([]bool, n)
	prev := make([]int, n)
	for i := 0; i < n; i++ {
		prev[i] = -1
	}

	queue := []int{source}
	visited[source] = true

	for len(queue) > 0 {
		curr := queue[0]
		queue = queue[1:]
		for _, neighbor := range adjacency[curr] {
			if !visited[neighbor] {
				visited[neighbor] = true
				prev[neighbor] = curr
				if neighbor == destination {
					// Reconstruct the path from destination to source.
					path := []int{destination}
					for at := curr; at != -1; at = prev[at] {
						path = append([]int{at}, path...)
					}
					return path
				}
				queue = append(queue, neighbor)
			}
		}
	}
	return []int{}
}