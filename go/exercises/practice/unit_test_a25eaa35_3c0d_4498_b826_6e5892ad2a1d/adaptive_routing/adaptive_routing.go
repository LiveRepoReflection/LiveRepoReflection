package adaptive_routing

// AdaptiveRouter interface defines the methods required for the adaptive routing system
type AdaptiveRouter interface {
	// AddNode adds a node with the given ID to the network
	AddNode(nodeID int)
	
	// RemoveNode removes the node with the given ID from the network
	RemoveNode(nodeID int)
	
	// AddLink establishes a directed link from source to destination
	AddLink(source, destination int)
	
	// RemoveLink removes the directed link from source to destination
	RemoveLink(source, destination int)
	
	// FindShortestPath finds the shortest path from source to destination
	// Returns the path as a slice of node IDs and an error if no path exists
	FindShortestPath(source, destination int) ([]int, error)
}

// NewAdaptiveRouter creates and returns a new instance of AdaptiveRouter
func NewAdaptiveRouter() AdaptiveRouter {
	// Implementation to be provided by the student
	return nil
}