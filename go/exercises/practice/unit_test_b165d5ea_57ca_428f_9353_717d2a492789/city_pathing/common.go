package city_pathing

// TrafficAPI defines the interface for fetching traffic signal states
type TrafficAPI interface {
	GetSignalStates() map[int]string
}

// CityGraph represents the city road network
type CityGraph struct {
	intersections map[int]struct{}
	roads         map[int]map[int]Road
}

// Road represents a connection between two intersections
type Road struct {
	length     int
	isOneWay   bool
	conditions int // Additional conditions affecting travel time
}

// NewCityGraph creates a new empty city graph
func NewCityGraph() *CityGraph {
	return &CityGraph{
		intersections: make(map[int]struct{}),
		roads:         make(map[int]map[int]Road),
	}
}

// PathFinder handles pathfinding operations
type PathFinder struct {
	graph *CityGraph
	api   TrafficAPI
}

// NewPathFinder creates a new path finder instance
func NewPathFinder(graph *CityGraph, api TrafficAPI) *PathFinder {
	return &PathFinder{
		graph: graph,
		api:   api,
	}
}