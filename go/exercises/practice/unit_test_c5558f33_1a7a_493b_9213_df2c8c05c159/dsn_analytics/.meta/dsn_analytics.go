package dsn_analytics

import (
	"container/list"
)

type nodeData struct {
	users     []string
	neighbors []int
}

// AnalyzeDSN queries all nodes in the decentralized social network, builds a graph,
// and computes the shortest directed path between every pair of target user IDs.
// The returned slice contains, in order, the shortest path for each pair (in the order:
// (targetUserIDs[0] -> targetUserIDs[1]), (targetUserIDs[0] -> targetUserIDs[2]), ..., (targetUserIDs[i] -> targetUserIDs[j]) for i < j).
// If a target user does not exist or no path exists, an empty slice is returned for that pair.
func AnalyzeDSN(N int, queryNode func(nodeID int) ([]string, []int), targetUserIDs []string) [][]int {
	// Build graph: query each node exactly once
	graph := make(map[int]nodeData, N)
	userToNodes := make(map[string][]int)

	for i := 0; i < N; i++ {
		users, neighbors := queryNode(i)
		graph[i] = nodeData{
			users:     users,
			neighbors: neighbors,
		}
		// For each user on the node, add mapping from user to nodeID
		for _, user := range users {
			userToNodes[user] = append(userToNodes[user], i)
		}
	}

	// Helper function: perform multi-source BFS to find shortest path from any of the source nodes to any of the destination nodes.
	bfs := func(srcNodes []int, destNodesSet map[int]bool) []int {
		// If any source node is also a destination, return that immediately.
		for _, sn := range srcNodes {
			if destNodesSet[sn] {
				return []int{sn}
			}
		}

		// visited keeps track of visited node IDs.
		visited := make(map[int]bool)
		// predecessor maps each visited node to its predecessor in the BFS tree.
		predecessor := make(map[int]int)
		// queue for BFS
		queue := list.New()
		// Initialize the queue with all source nodes. Use -1 as a flag for no predecessor.
		for _, sn := range srcNodes {
			queue.PushBack(sn)
			visited[sn] = true
			predecessor[sn] = -1
		}

		var destFound int = -1
	searchLoop:
		for queue.Len() > 0 {
			elem := queue.Front()
			queue.Remove(elem)
			current := elem.Value.(int)
			// For each neighbor of the current node
			for _, neighbor := range graph[current].neighbors {
				if !visited[neighbor] {
					visited[neighbor] = true
					predecessor[neighbor] = current
					// Check if this neighbor is one of our destination nodes.
					if destNodesSet[neighbor] {
						destFound = neighbor
						break searchLoop
					}
					queue.PushBack(neighbor)
				}
			}
		}

		// If destination not found, return empty slice.
		if destFound == -1 {
			return []int{}
		}

		// Reconstruct the path from a source node to the found destination.
		var path []int
		for cur := destFound; cur != -1; cur = predecessor[cur] {
			path = append(path, cur)
		}
		// Reverse the path to get from source to destination.
		for i, j := 0, len(path)-1; i < j; i, j = i+1, j-1 {
			path[i], path[j] = path[j], path[i]
		}
		return path
	}

	// Prepare the result slice for each pair.
	var results [][]int
	// For each pair (i, j) for 0 <= i < j < len(targetUserIDs)
	for i := 0; i < len(targetUserIDs)-1; i++ {
		for j := i + 1; j < len(targetUserIDs); j++ {
			srcUser := targetUserIDs[i]
			destUser := targetUserIDs[j]
			srcNodes, srcExists := userToNodes[srcUser]
			destNodes, destExists := userToNodes[destUser]

			// If either target user does not exist, return an empty path for this pair.
			if !srcExists || len(srcNodes) == 0 || !destExists || len(destNodes) == 0 {
				results = append(results, []int{})
				continue
			}

			// Build a set for destination nodes for fast lookup.
			destNodesSet := make(map[int]bool)
			for _, dn := range destNodes {
				destNodesSet[dn] = true
			}

			// Obtain the shortest path from any of the source nodes to any of the destination nodes.
			path := bfs(srcNodes, destNodesSet)
			results = append(results, path)
		}
	}

	return results
}