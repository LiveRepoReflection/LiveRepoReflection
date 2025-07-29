package auto_navigate

import (
	"container/heap"
	"errors"
	"strconv"
	"sync"
)

// Edge represents an edge from a source node to a destination node.
type Edge struct {
	weight int
	active bool
}

// GraphNavigator maintains the graph and provides methods for dynamic updates and path finding.
type GraphNavigator struct {
	graph map[string]map[string]*Edge
	src   string
	dst   string
	mu    sync.RWMutex
}

// NewGraphNavigator creates and returns a new GraphNavigator.
// initialEdges is a slice of []string where each sub-slice contains source, destination and weight.
func NewGraphNavigator(initialEdges [][]string, source, destination string) *GraphNavigator {
	gn := &GraphNavigator{
		graph: make(map[string]map[string]*Edge),
		src:   source,
		dst:   destination,
	}
	// Populate initial edges.
	for _, edge := range initialEdges {
		if len(edge) != 3 {
			continue
		}
		src := edge[0]
		dst := edge[1]
		weight, err := strconv.Atoi(edge[2])
		if err != nil {
			continue
		}
		if gn.graph[src] == nil {
			gn.graph[src] = make(map[string]*Edge)
		}
		gn.graph[src][dst] = &Edge{
			weight: weight,
			active: true,
		}
		// Ensure the destination node exists in the graph, even with no outgoing edges
		if gn.graph[dst] == nil {
			gn.graph[dst] = make(map[string]*Edge)
		}
	}
	// Ensure source and destination nodes exist.
	if gn.graph[source] == nil {
		gn.graph[source] = make(map[string]*Edge)
	}
	if gn.graph[destination] == nil {
		gn.graph[destination] = make(map[string]*Edge)
	}
	return gn
}

// ProcessEvent processes a single event to dynamically update the graph.
// Valid events are: BlockEdge, UnblockEdge, and AddEdge.
func (gn *GraphNavigator) ProcessEvent(event []string) error {
	if len(event) == 0 {
		return errors.New("empty event")
	}
	gn.mu.Lock()
	defer gn.mu.Unlock()
	switch event[0] {
	case "BlockEdge":
		if len(event) != 3 {
			return errors.New("BlockEdge event requires 3 arguments")
		}
		src, dst := event[1], event[2]
		edgeMap, ok := gn.graph[src]
		if !ok {
			return errors.New("source node does not exist")
		}
		edge, exists := edgeMap[dst]
		if !exists {
			return errors.New("edge does not exist")
		}
		edge.active = false
	case "UnblockEdge":
		if len(event) != 4 {
			return errors.New("UnblockEdge event requires 4 arguments")
		}
		src, dst, weightStr := event[1], event[2], event[3]
		weight, err := strconv.Atoi(weightStr)
		if err != nil {
			return errors.New("invalid weight")
		}
		edgeMap, ok := gn.graph[src]
		if !ok {
			return errors.New("source node does not exist")
		}
		edge, exists := edgeMap[dst]
		if !exists {
			return errors.New("edge does not exist")
		}
		edge.weight = weight
		edge.active = true
	case "AddEdge":
		if len(event) != 4 {
			return errors.New("AddEdge event requires 4 arguments")
		}
		src, dst, weightStr := event[1], event[2], event[3]
		weight, err := strconv.Atoi(weightStr)
		if err != nil {
			return errors.New("invalid weight")
		}
		if gn.graph[src] == nil {
			gn.graph[src] = make(map[string]*Edge)
		}
		gn.graph[src][dst] = &Edge{
			weight: weight,
			active: true,
		}
		// Ensure the destination node exists even if no outgoing edges
		if gn.graph[dst] == nil {
			gn.graph[dst] = make(map[string]*Edge)
		}
	default:
		return errors.New("unknown event type")
	}
	return nil
}

// ShortestPath computes the shortest active path from the source to the destination using Dijkstra's algorithm.
func (gn *GraphNavigator) ShortestPath() ([]string, error) {
	gn.mu.RLock()
	defer gn.mu.RUnlock()
	
	// Check if source and destination exist.
	if _, ok := gn.graph[gn.src]; !ok {
		return nil, errors.New("source node does not exist")
	}
	if _, ok := gn.graph[gn.dst]; !ok {
		return nil, errors.New("destination node does not exist")
	}

	// Initialize distances and priority queue.
	dist := make(map[string]int)
	prev := make(map[string]string)
	for node := range gn.graph {
		dist[node] = 1<<63 - 1 // use a large number as infinity
	}
	dist[gn.src] = 0

	pq := &PriorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &Item{
		node: gn.src,
		cost: 0,
	})
	
	for pq.Len() > 0 {
		currentItem := heap.Pop(pq).(*Item)
		currentNode := currentItem.node
		currentCost := currentItem.cost

		if currentNode == gn.dst {
			// Found destination, reconstruct path.
			return reconstructPath(prev, gn.src, gn.dst), nil
		}
		
		// If we have already found a better way, skip.
		if currentCost > dist[currentNode] {
			continue
		}
		
		neighbors := gn.graph[currentNode]
		for neighbor, edge := range neighbors {
			if !edge.active {
				continue
			}
			newCost := currentCost + edge.weight
			if newCost < dist[neighbor] {
				dist[neighbor] = newCost
				prev[neighbor] = currentNode
				heap.Push(pq, &Item{
					node: neighbor,
					cost: newCost,
				})
			}
		}
	}
	return nil, errors.New("no valid path found")
}

// reconstructPath reconstructs the path from source to destination using the prev map.
func reconstructPath(prev map[string]string, source, destination string) []string {
	path := []string{}
	for at := destination; at != ""; at = prev[at] {
		path = append([]string{at}, path...)
		if at == source {
			break
		}
	}
	if len(path) == 0 || path[0] != source {
		return nil
	}
	return path
}

// Item is a node in the priority queue.
type Item struct {
	node string
	cost int
	index int
}

// PriorityQueue implements heap.Interface and holds Items.
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }
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
	item := x.(*Item)
	item.index = n
	*pq = append(*pq, item)
}
func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	item.index = -1 // for safety
	*pq = old[0 : n-1]
	return item
}