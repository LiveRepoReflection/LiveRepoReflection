package dav_network

import (
	"container/heap"
	"time"
)

type TransportType int

const (
	PASSENGER TransportType = iota
	CARGO
	BOTH
)

type Node struct {
	ID int
}

type Edge struct {
	From   int
	To     int
	Weight int
}

type Graph struct {
	Nodes []Node
	Edges []Edge
}

type DAV struct {
	ID               int
	Location         int
	PassengerCapacity int
	CargoCapacity    int
	MaxBattery       int
	ProcessingPower  int
	CurrentBattery   int
	CurrentPassenger int
	CurrentCargo     int
	CurrentPath      []int
	AssignedRequests []Request
}

type Request struct {
	ID        int
	Start     int
	End       int
	Type      TransportType
	Quantity  int
	Deadline  time.Time
	Reward    int
	Assigned  bool
	Completed bool
}

type Action struct {
	DAVID      int
	Type       ActionType
	RequestID  int
	Path       []int
	StartTime  time.Time
	FinishTime time.Time
}

type ActionType int

const (
	PICKUP ActionType = iota
	DELIVER
	IDLE
)

type Network struct {
	Graph    Graph
	DAVs     []DAV
	Requests []Request
	Time     time.Time
}

func NewNetwork(graph Graph, davs []DAV) *Network {
	return &Network{
		Graph: graph,
		DAVs:  davs,
		Time:  time.Now(),
	}
}

func (n *Network) HandleRequests(requests []Request) []Action {
	n.Requests = requests
	var actions []Action

	// Priority queue for requests (max heap based on reward)
	pq := make(PriorityQueue, len(requests))
	for i := range requests {
		pq[i] = &Item{
			value:    &requests[i],
			priority: requests[i].Reward,
			index:    i,
		}
	}
	heap.Init(&pq)

	for pq.Len() > 0 {
		item := heap.Pop(&pq).(*Item)
		req := item.value

		// Skip if request is already assigned or expired
		if req.Assigned || req.Deadline.Before(n.Time) {
			continue
		}

		// Find best DAV for this request
		bestDAV, path := n.findBestDAVForRequest(*req)
		if bestDAV == nil {
			continue
		}

		// Create actions
		pickupAction := Action{
			DAVID:      bestDAV.ID,
			Type:       PICKUP,
			RequestID:  req.ID,
			Path:       path,
			StartTime:  n.Time,
			FinishTime: n.Time.Add(time.Duration(n.calculatePathTime(path)) * time.Minute),
		}

		deliveryPath := n.findPath(req.Start, req.End)
		deliveryAction := Action{
			DAVID:      bestDAV.ID,
			Type:       DELIVER,
			RequestID:  req.ID,
			Path:       deliveryPath,
			StartTime:  pickupAction.FinishTime,
			FinishTime: pickupAction.FinishTime.Add(time.Duration(n.calculatePathTime(deliveryPath)) * time.Minute),
		}

		// Update DAV state
		bestDAV.CurrentPath = path
		bestDAV.AssignedRequests = append(bestDAV.AssignedRequests, *req)
		bestDAV.CurrentBattery -= n.calculatePathTime(path)
		bestDAV.CurrentBattery -= n.calculatePathTime(deliveryPath)
		if req.Type == PASSENGER || req.Type == BOTH {
			bestDAV.CurrentPassenger += req.Quantity
		}
		if req.Type == CARGO || req.Type == BOTH {
			bestDAV.CurrentCargo += req.Quantity
		}

		// Update request state
		req.Assigned = true
		n.Time = deliveryAction.FinishTime

		actions = append(actions, pickupAction, deliveryAction)
	}

	return actions
}

func (n *Network) findBestDAVForRequest(req Request) (*DAV, []int) {
	var bestDAV *DAV
	var bestPath []int
	var bestScore int

	for i := range n.DAVs {
		dav := &n.DAVs[i]
		
		// Check capacity constraints
		if (req.Type == PASSENGER || req.Type == BOTH) && 
		   (dav.CurrentPassenger + req.Quantity > dav.PassengerCapacity) {
			continue
		}
		if (req.Type == CARGO || req.Type == BOTH) && 
		   (dav.CurrentCargo + req.Quantity > dav.CargoCapacity) {
			continue
		}

		// Find path to request start
		path := n.findPath(dav.Location, req.Start)
		pathTime := n.calculatePathTime(path)

		// Check battery constraints
		deliveryPath := n.findPath(req.Start, req.End)
		totalBatteryNeeded := pathTime + n.calculatePathTime(deliveryPath)
		if totalBatteryNeeded > dav.MaxBattery {
			continue
		}

		// Calculate score (higher is better)
		score := req.Reward - pathTime // Simple heuristic: reward minus distance

		if bestDAV == nil || score > bestScore {
			bestDAV = dav
			bestPath = path
			bestScore = score
		}
	}

	return bestDAV, bestPath
}

func (n *Network) findPath(from, to int) []int {
	// Simplified Dijkstra's algorithm implementation
	// In a real implementation, you'd want a more optimized version
	dist := make(map[int]int)
	prev := make(map[int]int)
	visited := make(map[int]bool)
	
	for _, node := range n.Graph.Nodes {
		dist[node.ID] = 1 << 30 // "Infinity"
	}
	dist[from] = 0

	for len(visited) < len(n.Graph.Nodes) {
		// Find unvisited node with smallest distance
		var u int
		minDist := 1 << 30
		for _, node := range n.Graph.Nodes {
			if !visited[node.ID] && dist[node.ID] < minDist {
				minDist = dist[node.ID]
				u = node.ID
			}
		}

		if u == to {
			break
		}

		visited[u] = true

		// Update distances to neighbors
		for _, edge := range n.Graph.Edges {
			if edge.From == u || edge.To == u {
				v := edge.To
				if edge.From == u {
					v = edge.To
				} else {
					v = edge.From
				}

				if !visited[v] {
					alt := dist[u] + edge.Weight
					if alt < dist[v] {
						dist[v] = alt
						prev[v] = u
					}
				}
			}
		}
	}

	// Reconstruct path
	path := []int{}
	u := to
	for u != from {
		path = append([]int{u}, path...)
		u = prev[u]
	}
	path = append([]int{from}, path...)

	return path
}

func (n *Network) calculatePathTime(path []int) int {
	if len(path) < 2 {
		return 0
	}

	total := 0
	for i := 0; i < len(path)-1; i++ {
		for _, edge := range n.Graph.Edges {
			if (edge.From == path[i] && edge.To == path[i+1]) ||
			   (edge.From == path[i+1] && edge.To == path[i]) {
				total += edge.Weight
				break
			}
		}
	}
	return total
}

// Priority queue implementation for requests
type Item struct {
	value    *Request
	priority int
	index    int
}

type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	return pq[i].priority > pq[j].priority // Max-heap based on reward
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	n := len(*pq)
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	old[n-1] = nil
	item.index = -1
	*pq = old[0 : n-1]
	return item
}