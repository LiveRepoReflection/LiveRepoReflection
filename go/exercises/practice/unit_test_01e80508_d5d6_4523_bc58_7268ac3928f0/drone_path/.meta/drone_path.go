package drone_path

import (
	"container/heap"
	"errors"
	"math"
)

// Node represents a location in the graph.
type Node struct {
	ID   int
	X, Y float64
	Risk int
}

// Edge represents a flight path from one node to another.
type Edge struct {
	From        int
	To          int
	FlightTime  float64
	MaxAltitude float64
}

// Graph represents the entire network of nodes and edges.
type Graph struct {
	Nodes map[int]Node
	Edges map[int][]Edge
}

// NoFlyZone represents a circular area where the drone cannot fly.
type NoFlyZone struct {
	CenterX, CenterY float64
	Radius           float64
}

// state represents a node in the search with cumulative parameters.
type state struct {
	node   int
	time   float64
	risk   int
	path   []int
	index  int // index in the heap
}

// a priority queue implementation for states based on cumulative flight time.
type statePQ []*state

func (pq statePQ) Len() int { return len(pq) }

func (pq statePQ) Less(i, j int) bool {
	return pq[i].time < pq[j].time
}

func (pq statePQ) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *statePQ) Push(x interface{}) {
	n := len(*pq)
	item := x.(*state)
	item.index = n
	*pq = append(*pq, item)
}

func (pq *statePQ) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}

// flightAltitude is the assumed constant altitude at which the drone flies.
const flightAltitude = 100.0

// lineSegmentIntersectsCircle checks if the line segment from (x1,y1) to (x2,y2)
// intersects the circle centered at (cx,cy) with radius r.
func lineSegmentIntersectsCircle(x1, y1, x2, y2, cx, cy, r float64) bool {
	// Vector from A to B.
	dx := x2 - x1
	dy := y2 - y1

	// Vector from A to circle center.
	fx := x1 - cx
	fy := y1 - cy

	a := dx*dx + dy*dy
	b := 2 * (fx*dx + fy*dy)
	c := (fx*fx + fy*fy) - r*r

	// Discriminant
	discriminant := b*b - 4*a*c
	if discriminant < 0 {
		// No intersection if discriminant < 0
		return false
	}

	discriminant = math.Sqrt(discriminant)

	// Find the two possible values of t
	t1 := (-b - discriminant) / (2 * a)
	t2 := (-b + discriminant) / (2 * a)

	// Check if either t is within the segment [0,1]
	if (t1 >= 0 && t1 <= 1) || (t2 >= 0 && t2 <= 1) {
		return true
	}
	return false
}

// edgeIntersectsNoFlyZones checks whether the edge from node u to node v intersects any no-fly zone.
func edgeIntersectsNoFlyZones(u, v Node, noFlyZones []NoFlyZone) bool {
	for _, zone := range noFlyZones {
		if lineSegmentIntersectsCircle(u.X, u.Y, v.X, v.Y, zone.CenterX, zone.CenterY, zone.Radius) {
			return true
		}
	}
	return false
}

// FindOptimalPath finds the optimal path (with minimum flight time) from start to end node
// in the graph given the maximum total risk, maximum flight time, and list of no-fly zones.
// It returns an error if no valid path exists.
func FindOptimalPath(g Graph, start, end int, maxRisk int, maxTime float64, noFlyZones []NoFlyZone) ([]int, error) {
	// Check if start and end nodes exist
	startNode, ok := g.Nodes[start]
	if !ok {
		return nil, errors.New("start node not in graph")
	}
	_, ok = g.Nodes[end]
	if !ok {
		return nil, errors.New("end node not in graph")
	}

	// `best` maps node id to a map of cumulative risk and the best flight time found for that risk.
	best := make(map[int]map[int]float64)
	pq := &statePQ{}
	heap.Init(pq)

	initialRisk := startNode.Risk
	initialState := &state{
		node: start,
		time: 0.0,
		risk: initialRisk,
		path: []int{start},
	}
	heap.Push(pq, initialState)
	best[start] = map[int]float64{initialRisk: 0.0}

	for pq.Len() > 0 {
		curr := heap.Pop(pq).(*state)
		// If we've reached the destination with valid conditions, return the path.
		if curr.node == end {
			if curr.time <= maxTime {
				return curr.path, nil
			}
		}

		// Expand all outgoing edges from current node.
		for _, edge := range g.Edges[curr.node] {
			// Check the altitude constraint; drone flies at flightAltitude.
			if flightAltitude > edge.MaxAltitude {
				continue
			}

			nextNode, exists := g.Nodes[edge.To]
			if !exists {
				continue
			}

			// Check if the edge intersects any no-fly zone.
			if edgeIntersectsNoFlyZones(g.Nodes[curr.node], nextNode, noFlyZones) {
				continue
			}

			newTime := curr.time + edge.FlightTime
			if newTime > maxTime {
				continue
			}

			newRisk := curr.risk + nextNode.Risk
			if newRisk > maxRisk {
				continue
			}

			// Check if we have a better time for this node at this or lower risk.
			existing, ok := best[nextNode.ID]
			skip := false
			if ok {
				for r, tval := range existing {
					// if we already reached this node with risk r <= newRisk and time tval <= newTime, skip.
					if r <= newRisk && tval <= newTime {
						skip = true
						break
					}
				}
			}
			if skip {
				continue
			}
			// Record the new cost.
			if best[nextNode.ID] == nil {
				best[nextNode.ID] = make(map[int]float64)
			}
			best[nextNode.ID][newRisk] = newTime

			// Append the new state.
			newPath := make([]int, len(curr.path))
			copy(newPath, curr.path)
			newPath = append(newPath, nextNode.ID)
			newState := &state{
				node: nextNode.ID,
				time: newTime,
				risk: newRisk,
				path: newPath,
			}
			heap.Push(pq, newState)
		}
	}
	return nil, errors.New("no valid path found")
}