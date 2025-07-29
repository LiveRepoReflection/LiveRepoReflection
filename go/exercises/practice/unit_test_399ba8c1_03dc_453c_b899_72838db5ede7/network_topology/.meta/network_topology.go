package network_topology

import (
	"container/heap"
	"errors"
)

// Edge represents a directed edge in the network.
type Edge struct {
	From    int
	To      int
	Latency int
}

// Network represents the network topology as a directed graph.
type Network struct {
	n   int
	adj map[int]map[int]int // for each node, a map from neighbor to minimum latency
}

// NewNetwork creates a new network with n nodes.
func NewNetwork(n int) (*Network, error) {
	if n <= 0 {
		return nil, errors.New("number of nodes must be positive")
	}
	adj := make(map[int]map[int]int)
	for i := 0; i < n; i++ {
		adj[i] = make(map[int]int)
	}
	return &Network{
		n:   n,
		adj: adj,
	}, nil
}

// validNode checks if node id is valid.
func (net *Network) validNode(u int) bool {
	return u >= 0 && u < net.n
}

// AddEdge adds a directed edge from u to v with given latency.
// If an edge already exists, it updates the edge latency with the smaller value.
func (net *Network) AddEdge(u, v, latency int) error {
	if !net.validNode(u) || !net.validNode(v) {
		return errors.New("invalid node index")
	}
	if latency < 0 {
		return errors.New("latency must be non-negative")
	}
	// if edge exists, update if new latency is smaller
	if existing, ok := net.adj[u][v]; ok {
		if latency < existing {
			net.adj[u][v] = latency
		}
	} else {
		net.adj[u][v] = latency
	}
	return nil
}

// RemoveEdge removes the directed edge from u to v.
func (net *Network) RemoveEdge(u, v int) error {
	if !net.validNode(u) || !net.validNode(v) {
		return errors.New("invalid node index")
	}
	if _, ok := net.adj[u][v]; !ok {
		return errors.New("edge does not exist")
	}
	delete(net.adj[u], v)
	return nil
}

// Connected determines if there is a path from node u to node v.
func (net *Network) Connected(u, v int) bool {
	if !net.validNode(u) || !net.validNode(v) {
		return false
	}
	visited := net.bfs(u)
	return visited[v]
}

// MinLatency calculates the minimum total latency from node u to node v using Dijkstra's algorithm.
// Returns -1 if no path exists.
func (net *Network) MinLatency(u, v int) int {
	if !net.validNode(u) || !net.validNode(v) {
		return -1
	}
	dist := make([]int, net.n)
	for i := 0; i < net.n; i++ {
		dist[i] = 1<<31 - 1 // treat as infinity
	}
	dist[u] = 0

	pq := &priorityQueue{}
	heap.Init(pq)
	heap.Push(pq, &item{node: u, priority: 0})

	for pq.Len() > 0 {
		cur := heap.Pop(pq).(*item)
		if cur.priority > dist[cur.node] {
			continue
		}
		// if we've reached the target, we can return early
		if cur.node == v {
			return cur.priority
		}
		for neighbor, latency := range net.adj[cur.node] {
			newDist := dist[cur.node] + latency
			if newDist < dist[neighbor] {
				dist[neighbor] = newDist
				heap.Push(pq, &item{node: neighbor, priority: newDist})
			}
		}
	}
	if dist[v] == 1<<31-1 {
		return -1
	}
	return dist[v]
}

// CriticalEdges returns a list of edges whose removal disconnects at least two nodes
// that were previously connected. This implementation computes the original connectivity
// from every node and then, for every edge, tests connectivity after its removal.
func (net *Network) CriticalEdges() []Edge {
	// compute original connectivity: for each node, get set of reachable nodes.
	origConn := make([]map[int]bool, net.n)
	for i := 0; i < net.n; i++ {
		origConn[i] = net.bfs(i)
	}

	var critical []Edge
	// iterate over each edge in the graph.
	for u := 0; u < net.n; u++ {
		for v, latency := range net.adj[u] {
			// Temporarily remove the edge.
			backup := latency
			delete(net.adj[u], v)

			// Recompute connectivity for all nodes.
			disconnected := false
			for i := 0; i < net.n; i++ {
				newConn := net.bfs(i)
				// For every node that was originally reachable, check if it is still reachable.
				for j := range origConn[i] {
					if origConn[i][j] && !newConn[j] {
						disconnected = true
						break
					}
				}
				if disconnected {
					break
				}
			}

			if disconnected {
				critical = append(critical, Edge{From: u, To: v, Latency: backup})
			}
			// Restore the edge.
			net.adj[u][v] = backup
		}
	}
	return critical
}

// bfs performs a breadth-first search from src and returns a map indicating reachable nodes.
func (net *Network) bfs(src int) map[int]bool {
	visited := make(map[int]bool)
	queue := []int{src}
	visited[src] = true
	for len(queue) > 0 {
		cur := queue[0]
		queue = queue[1:]
		for neighbor := range net.adj[cur] {
			if !visited[neighbor] {
				visited[neighbor] = true
				queue = append(queue, neighbor)
			}
		}
	}
	// Ensure all nodes are marked false if not visited.
	for i := 0; i < net.n; i++ {
		if _, ok := visited[i]; !ok {
			visited[i] = false
		}
	}
	return visited
}

// Priority Queue implementation for Dijkstra's algorithm.
type item struct {
	node     int
	priority int
	index    int
}

type priorityQueue []*item

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
	it := x.(*item)
	it.index = n
	*pq = append(*pq, it)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	it := old[n-1]
	old[n-1] = nil  
	it.index = -1 
	*pq = old[0 : n-1]
	return it
}