package resilience

type nodeData struct {
	NodeID  int
	DataID  int
	Version int
}

func IsResilient(N int, adjMatrix [][]int, data []nodeData) bool {
	// Create a map for quick lookup of node data
	nodeDataMap := make(map[int]nodeData)
	for _, nd := range data {
		nodeDataMap[nd.NodeID] = nd
	}

	// Find all connected components using DFS
	visited := make([]bool, N)
	components := [][]int{}

	for i := 0; i < N; i++ {
		if !visited[i] {
			component := []int{}
			dfs(i, N, adjMatrix, visited, &component)
			components = append(components, component)
		}
	}

	// Find the largest component
	largestComponent := []int{}
	for _, comp := range components {
		if len(comp) > len(largestComponent) {
			largestComponent = comp
		} else if len(comp) == len(largestComponent) {
			// If sizes are equal, choose the one with lowest node ID
			if comp[0] < largestComponent[0] {
				largestComponent = comp
			}
		}
	}

	// Check data integrity within the largest component
	if len(largestComponent) == 0 {
		return false
	}

	// Get reference data from first node in largest component
	refData := nodeDataMap[largestComponent[0]]
	refDataID := refData.DataID
	refVersion := refData.Version

	// Check if all nodes in largest component have same data ID and version
	for _, nodeID := range largestComponent {
		nodeData := nodeDataMap[nodeID]
		if nodeData.DataID != refDataID || nodeData.Version != refVersion {
			return false
		}
	}

	return true
}

// DFS implementation to find connected components
func dfs(node int, N int, adjMatrix [][]int, visited []bool, component *[]int) {
	visited[node] = true
	*component = append(*component, node)

	for neighbor := 0; neighbor < N; neighbor++ {
		if adjMatrix[node][neighbor] == 1 && !visited[neighbor] {
			dfs(neighbor, N, adjMatrix, visited, component)
		}
	}
}