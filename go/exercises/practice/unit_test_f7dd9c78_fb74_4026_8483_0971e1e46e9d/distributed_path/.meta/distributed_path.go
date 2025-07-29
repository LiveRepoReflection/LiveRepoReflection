package distributed_path

import (
	"container/heap"
	"errors"
	"sync"
)

type Network struct {
	nodes     map[string]*Node
	nodesLock sync.RWMutex
}

type Node struct {
	ID       string
	Links    map[string]int // neighbor ID -> cost
	Online   bool
	nodeLock sync.RWMutex
}

type pathItem struct {
	node string
	cost int
	path []string
}

type priorityQueue []*pathItem

func (pq priorityQueue) Len() int           { return len(pq) }
func (pq priorityQueue) Less(i, j int) bool { return pq[i].cost < pq[j].cost }
func (pq priorityQueue) Swap(i, j int)      { pq[i], pq[j] = pq[j], pq[i] }

func (pq *priorityQueue) Push(x interface{}) {
	item := x.(*pathItem)
	*pq = append(*pq, item)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

func NewNetwork(initialTopology map[string]map[string]int) *Network {
	n := &Network{
		nodes: make(map[string]*Node),
	}

	for nodeID, links := range initialTopology {
		n.AddNode(nodeID)
		for neighbor, cost := range links {
			n.AddNode(neighbor)
			n.UpdateLink(nodeID, neighbor, cost)
		}
	}

	return n
}

func (n *Network) AddNode(id string) {
	n.nodesLock.Lock()
	defer n.nodesLock.Unlock()

	if _, exists := n.nodes[id]; !exists {
		n.nodes[id] = &Node{
			ID:     id,
			Links:  make(map[string]int),
			Online: true,
		}
	}
}

func (n *Network) MarkNodeOffline(id string) {
	n.nodesLock.RLock()
	node, exists := n.nodes[id]
	n.nodesLock.RUnlock()

	if exists {
		node.nodeLock.Lock()
		node.Online = false
		node.nodeLock.Unlock()
	}
}

func (n *Network) MarkNodeOnline(id string) {
	n.nodesLock.RLock()
	node, exists := n.nodes[id]
	n.nodesLock.RUnlock()

	if exists {
		node.nodeLock.Lock()
		node.Online = true
		node.nodeLock.Unlock()
	}
}

func (n *Network) UpdateLink(from, to string, cost int) {
	n.nodesLock.RLock()
	fromNode, fromExists := n.nodes[from]
	toNode, toExists := n.nodes[to]
	n.nodesLock.RUnlock()

	if fromExists && toExists {
		fromNode.nodeLock.Lock()
		fromNode.Links[to] = cost
		fromNode.nodeLock.Unlock()

		toNode.nodeLock.Lock()
		toNode.Links[from] = cost
		toNode.nodeLock.Unlock()
	}
}

func (n *Network) FindShortestPath(source, destination string) ([]string, int, error) {
	n.nodesLock.RLock()
	defer n.nodesLock.RUnlock()

	if _, exists := n.nodes[source]; !exists {
		return nil, 0, errors.New("source node does not exist")
	}
	if _, exists := n.nodes[destination]; !exists {
		return nil, 0, errors.New("destination node does not exist")
	}

	visited := make(map[string]bool)
	pq := make(priorityQueue, 0)
	heap.Init(&pq)

	heap.Push(&pq, &pathItem{
		node: source,
		cost: 0,
		path: []string{source},
	})

	for pq.Len() > 0 {
		current := heap.Pop(&pq).(*pathItem)

		if current.node == destination {
			return current.path, current.cost, nil
		}

		if visited[current.node] {
			continue
		}
		visited[current.node] = true

		n.nodesLock.RLock()
		node := n.nodes[current.node]
		n.nodesLock.RUnlock()

		node.nodeLock.RLock()
		if !node.Online {
			node.nodeLock.RUnlock()
			continue
		}

		for neighbor, cost := range node.Links {
			if !visited[neighbor] {
				newPath := make([]string, len(current.path)+1)
				copy(newPath, current.path)
				newPath[len(current.path)] = neighbor

				heap.Push(&pq, &pathItem{
					node: neighbor,
					cost: current.cost + cost,
					path: newPath,
				})
			}
		}
		node.nodeLock.RUnlock()
	}

	return nil, 0, errors.New("no path exists between source and destination")
}