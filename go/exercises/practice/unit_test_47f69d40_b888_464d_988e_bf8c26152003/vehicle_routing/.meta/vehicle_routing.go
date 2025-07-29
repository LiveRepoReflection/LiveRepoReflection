package vehicle_routing

import (
	"container/heap"
	"errors"
)

type Edge struct {
	From   string
	To     string
	Weight int
}

type Vehicle struct {
	ID            string
	Start         string
	End           string
	DepartureTime int
}

type TrafficEvent struct {
	Node      string
	StartTime int
	EndTime   int
	Delay     int
}

type item struct {
	node string
	cost int
	// index is needed by the heap.Interface methods.
	index int
}

type PriorityQueue []*item

func (pq PriorityQueue) Len() int { 
	return len(pq) 
}

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].cost < pq[j].cost
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	it := x.(*item)
	it.index = n
	*pq = append(*pq, it)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	it := old[n-1]
	old[n-1] = nil
	it.index = -1 // for safety
	*pq = old[0 : n-1]
	return it
}

func FindOptimalRoutes(nodes []string, edges []Edge, vehicles []Vehicle, trafficEvents []TrafficEvent, queryTime int) (map[string][]string, error) {
	// Validate nodes: build nodeSet map
	nodeSet := make(map[string]bool)
	for _, node := range nodes {
		nodeSet[node] = true
	}

	// Validate edges: ensure both From and To are in nodes
	graph := make(map[string][]Edge)
	for _, edge := range edges {
		if !nodeSet[edge.From] || !nodeSet[edge.To] {
			return nil, errors.New("edge contains invalid node")
		}
		graph[edge.From] = append(graph[edge.From], edge)
	}

	// Validate vehicles: duplicate IDs and invalid nodes in Start/End
	vehicleIDSet := make(map[string]bool)
	for _, vehicle := range vehicles {
		if vehicleIDSet[vehicle.ID] {
			return nil, errors.New("duplicate vehicle ID found")
		}
		vehicleIDSet[vehicle.ID] = true
		if !nodeSet[vehicle.Start] || !nodeSet[vehicle.End] {
			return nil, errors.New("vehicle contains invalid start or end node")
		}
	}

	result := make(map[string][]string)
	// Process each vehicle independently
	for _, vehicle := range vehicles {
		// Determine effective time: use departure time if it is greater than queryTime.
		effTime := queryTime
		if vehicle.DepartureTime > queryTime {
			effTime = vehicle.DepartureTime
		}
		// Build delay map for each node for this vehicle based on effective time.
		delayMap := make(map[string]int)
		for _, event := range trafficEvents {
			if _, exists := nodeSet[event.Node]; !exists {
				return nil, errors.New("traffic event contains invalid node")
			}
			if effTime >= event.StartTime && effTime <= event.EndTime {
				delayMap[event.Node] += event.Delay
			}
		}

		path, err := dijkstra(vehicle.Start, vehicle.End, graph, delayMap)
		if err != nil {
			// if no route found, return empty slice for that vehicle
			result[vehicle.ID] = []string{}
		} else {
			result[vehicle.ID] = path
		}
	}

	return result, nil
}

func dijkstra(start, end string, graph map[string][]Edge, delayMap map[string]int) ([]string, error) {
	// distances map and predecessor map
	dist := make(map[string]int)
	prev := make(map[string]string)
	for node := range delayMap {
		// initialize all nodes encountered in delayMap
		dist[node] = 1<<31 - 1
	}
	// Also include nodes from graph keys and from edges
	for node := range graph {
		dist[node] = 1<<31 - 1
		for _, edge := range graph[node] {
			dist[edge.To] = 1<<31 - 1
		}
	}
	// Ensure start and end are in dist map
	if _, ok := dist[start]; !ok {
		dist[start] = 1<<31 - 1
	}
	if _, ok := dist[end]; !ok {
		dist[end] = 1<<31 - 1
	}

	dist[start] = 0
	pq := make(PriorityQueue, 0)
	heap.Push(&pq, &item{
		node: start,
		cost: 0,
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*item)
		u := current.node
		currentCost := current.cost

		// If this popped cost is greater than the recorded distance, skip.
		if currentCost > dist[u] {
			continue
		}

		if u == end {
			// Reconstruct path and return; do not apply delay at destination.
			return reconstructPath(prev, u), nil
		}

		neighbors := graph[u]
		for _, edge := range neighbors {
			v := edge.To
			// Calculate additional delay if v is not the destination.
			extraDelay := 0
			if v != end {
				extraDelay = delayMap[v]
			}
			newCost := currentCost + edge.Weight + extraDelay
			if newCost < dist[v] {
				dist[v] = newCost
				prev[v] = u
				heap.Push(&pq, &item{
					node: v,
					cost: newCost,
				})
			}
		}
	}

	// If end is not reachable, return empty path
	return []string{}, nil
}

func reconstructPath(prev map[string]string, end string) []string {
	path := []string{}
	for current := end; current != ""; {
		path = append([]string{current}, path...)
		currentPrev, ok := prev[current]
		if !ok {
			break
		}
		current = currentPrev
	}
	return path
}