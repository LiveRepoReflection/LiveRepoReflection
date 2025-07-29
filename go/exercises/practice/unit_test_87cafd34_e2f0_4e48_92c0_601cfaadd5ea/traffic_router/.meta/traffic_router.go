package traffic_router

import (
	"container/heap"
	"errors"
	"math"
	"sync"
)

// Edge represents a road segment in the traffic network
type Edge struct {
	From     int
	To       int
	Capacity int
	BaseTime int
}

// VehicleRequest represents a routing request for a vehicle
type VehicleRequest struct {
	Origin      int
	Destination int
	Priority    int
}

// TrafficRouter handles vehicle routing in the traffic network
type TrafficRouter struct {
	numNodes int
	edges    []Edge
	adjList  [][]Edge
	flows    map[string]int
	mutex    sync.RWMutex
}

// node represents a node in the priority queue for Dijkstra's algorithm
type node struct {
	id       int
	cost     float64
	priority float64
	index    int
}

// priorityQueue implements heap.Interface and holds nodes
type priorityQueue []*node

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	return pq[i].priority < pq[j].priority
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *priorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*node)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

// NewTrafficRouter creates a new TrafficRouter instance
func NewTrafficRouter(numNodes int, edges []Edge) *TrafficRouter {
	tr := &TrafficRouter{
		numNodes: numNodes,
		edges:    edges,
		adjList:  make([][]Edge, numNodes),
		flows:    make(map[string]int),
	}

	// Build adjacency list
	for _, edge := range edges {
		tr.adjList[edge.From] = append(tr.adjList[edge.From], edge)
	}

	return tr
}

// RouteVehicle finds the optimal route for a vehicle
func (tr *TrafficRouter) RouteVehicle(req VehicleRequest) ([]int, error) {
	// Validate input
	if req.Origin < 0 || req.Origin >= tr.numNodes ||
		req.Destination < 0 || req.Destination >= tr.numNodes {
		return nil, errors.New("invalid origin or destination")
	}
	if req.Priority < 1 || req.Priority > 10 {
		return nil, errors.New("invalid priority")
	}

	// Run modified Dijkstra's algorithm
	dist := make([]float64, tr.numNodes)
	prev := make([]int, tr.numNodes)
	for i := range dist {
		dist[i] = math.Inf(1)
		prev[i] = -1
	}
	dist[req.Origin] = 0

	pq := make(priorityQueue, 0)
	heap.Init(&pq)
	heap.Push(&pq, &node{id: req.Origin, cost: 0, priority: 0})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*node)

		if current.id == req.Destination {
			break
		}

		if current.cost > dist[current.id] {
			continue
		}

		for _, edge := range tr.adjList[current.id] {
			tr.mutex.RLock()
			flow := tr.flows[getEdgeKey(edge.From, edge.To)]
			tr.mutex.RUnlock()

			// Calculate actual travel time based on current flow
			actualTime := float64(edge.BaseTime) * (1 + math.Pow(float64(flow)/float64(edge.Capacity), 2))
			
			// Adjust cost based on priority
			priorityFactor := 1.0 / float64(req.Priority)
			newCost := dist[current.id] + actualTime

			if newCost < dist[edge.To] {
				dist[edge.To] = newCost
				prev[edge.To] = current.id
				heap.Push(&pq, &node{
					id:       edge.To,
					cost:     newCost,
					priority: newCost * priorityFactor,
				})
			}
		}
	}

	// Reconstruct path
	if prev[req.Destination] == -1 {
		return nil, errors.New("no path exists")
	}

	path := []int{}
	current := req.Destination
	for current != -1 {
		path = append([]int{current}, path...)
		current = prev[current]
	}

	// Update flows for the chosen path
	tr.updateFlows(path)

	return path, nil
}

// getEdgeKey generates a unique key for an edge
func getEdgeKey(from, to int) string {
	return string(rune(from)) + ":" + string(rune(to))
}

// updateFlows updates the traffic flow for the chosen path
func (tr *TrafficRouter) updateFlows(path []int) {
	tr.mutex.Lock()
	defer tr.mutex.Unlock()

	for i := 0; i < len(path)-1; i++ {
		key := getEdgeKey(path[i], path[i+1])
		tr.flows[key]++
	}
}

// GetCurrentFlow returns the current flow for an edge
func (tr *TrafficRouter) GetCurrentFlow(from, to int) int {
	tr.mutex.RLock()
	defer tr.mutex.RUnlock()
	return tr.flows[getEdgeKey(from, to)]
}