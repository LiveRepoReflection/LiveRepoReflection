package social_mapper

func EstimateComponentSize(startNode string, getNodeInfo func(string) (friends []string, gossip map[string][]string, err error)) int {
	if startNode == "" {
		return 0
	}
	// Verify the start node is reachable.
	_, _, err := getNodeInfo(startNode)
	if err != nil {
		return 0
	}

	visited := make(map[string]bool)
	queue := []string{startNode}

	for len(queue) > 0 {
		current := queue[0]
		queue = queue[1:]
		if visited[current] {
			continue
		}
		visited[current] = true

		// Retrieve direct friend list, which is reliable.
		friends, _, err := getNodeInfo(current)
		if err != nil {
			continue
		}
		// Enqueue each unvisited friend.
		for _, neighbor := range friends {
			if !visited[neighbor] {
				queue = append(queue, neighbor)
			}
		}
	}

	return len(visited)
}