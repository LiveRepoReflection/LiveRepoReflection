package social_path

// FindPath searches for the shortest path from startUserID to targetUserID
// using a BFS strategy that minimizes calls to the userNode function.
// The userNode function receives a userID and returns a map of the local node graph,
// where the key is the userID and the value is a slice of connected user IDs.
// If no valid path is found within maxPathLength hops or if startUserID equals targetUserID,
// an empty slice is returned.
func FindPath(userNode func(string) map[string][]string, startUserID, targetUserID string, maxPathLength int) []string {
	// If start equals target, return an empty path as per specification.
	if startUserID == targetUserID {
		return []string{}
	}

	// Define a structure to hold the current path and its depth (number of hops).
	type pathItem struct {
		path  []string
		depth int
	}

	// Initialize the BFS queue with the starting node.
	queue := []pathItem{{path: []string{startUserID}, depth: 0}}

	// visited stores the minimum hop count at which a node was reached.
	visited := make(map[string]int)
	visited[startUserID] = 0

	// cache stores the result of calling userNode for a given userID to minimize duplicate calls.
	cache := make(map[string][]string)

	// Begin the BFS loop.
	for len(queue) > 0 {
		// Dequeue the next path to process.
		current := queue[0]
		queue = queue[1:]
		lastNode := current.path[len(current.path)-1]
		currentDepth := current.depth

		// If we have reached the maximum allowed hops, do not expand further.
		if currentDepth >= maxPathLength {
			continue
		}

		// Retrieve the friend list for the current node from cache or by calling userNode.
		var friends []string
		if cached, ok := cache[lastNode]; ok {
			friends = cached
		} else {
			result := userNode(lastNode)
			if conns, ok := result[lastNode]; ok {
				friends = conns
			} else {
				friends = []string{}
			}
			cache[lastNode] = friends
		}

		// Process each friend of the current node.
		for _, friend := range friends {
			// Skip if the friend is already in the current path to avoid cycles.
			if contains(current.path, friend) {
				continue
			}
			newDepth := currentDepth + 1
			// If the friend was reached before in fewer hops, skip expanding this path.
			if prevDepth, ok := visited[friend]; ok && newDepth > prevDepth {
				continue
			}
			visited[friend] = newDepth

			// Append the friend to the current path to form a new path.
			newPath := append(copySlice(current.path), friend)
			if friend == targetUserID {
				return newPath
			}
			queue = append(queue, pathItem{path: newPath, depth: newDepth})
		}
	}

	// No valid path found within maxPathLength hops.
	return []string{}
}

// contains checks if a slice of strings already includes a target string.
func contains(slice []string, target string) bool {
	for _, s := range slice {
		if s == target {
			return true
		}
	}
	return false
}

// copySlice creates a copy of a slice of strings.
func copySlice(slice []string) []string {
	newSlice := make([]string, len(slice))
	copy(newSlice, slice)
	return newSlice
}