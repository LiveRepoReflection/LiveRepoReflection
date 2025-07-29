package socialrouting

// FindRoutePath finds the shortest path from startUser to endUser in the social network
// within the maxHops constraint, avoiding any users in the blacklist.
// It returns a slice containing the path (including both start and end users) or an empty slice if no path exists.
func FindRoutePath(network map[string][]string, startUser, endUser string, maxHops int, blacklist []string) []string {
	// Handle edge cases
	if maxHops < 0 {
		return []string{}
	}

	// Check if start and end users exist in the network
	if _, startExists := network[startUser]; !startExists {
		return []string{}
	}
	if _, endExists := network[endUser]; !endExists {
		return []string{}
	}

	// If start and end are the same, return just that user
	if startUser == endUser {
		return []string{startUser}
	}

	// Create a blacklist map for O(1) lookups
	blacklistMap := make(map[string]bool)
	for _, user := range blacklist {
		blacklistMap[user] = true
	}

	// Check if start or end user is blacklisted
	if blacklistMap[startUser] || blacklistMap[endUser] {
		return []string{}
	}

	// BFS to find the shortest path
	type queueItem struct {
		user string
		path []string
		hops int
	}

	// Initialize queue with start user
	queue := []queueItem{{
		user: startUser,
		path: []string{startUser},
		hops: 0,
	}}

	// Track visited users to avoid cycles
	visited := make(map[string]bool)
	visited[startUser] = true

	for len(queue) > 0 {
		// Dequeue the first item
		current := queue[0]
		queue = queue[1:]

		// If we've reached our destination, return the path
		if current.user == endUser {
			return current.path
		}

		// If we've reached the max hops, don't explore further from this node
		if current.hops >= maxHops {
			continue
		}

		// Explore neighbors
		for _, neighbor := range network[current.user] {
			// Skip if already visited or blacklisted
			if visited[neighbor] || blacklistMap[neighbor] {
				continue
			}

			// Mark as visited
			visited[neighbor] = true

			// Create a new path by appending the neighbor
			newPath := make([]string, len(current.path)+1)
			copy(newPath, current.path)
			newPath[len(current.path)] = neighbor

			// Enqueue the neighbor with the new path
			queue = append(queue, queueItem{
				user: neighbor,
				path: newPath,
				hops: current.hops + 1,
			})
		}
	}

	// If we've exhausted the queue without finding a path
	return []string{}
}