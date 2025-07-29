package network_cdn

import (
	"container/heap"
	"math"
)

// Edge represents a connection between two servers with a given cost.
type Edge struct {
	to     int
	weight int
}

// Item represents an entry in the priority queue.
type Item struct {
	cost   int
	vertex int
	origin int
	index  int
}

// PriorityQueue implements heap.Interface for Items.
type PriorityQueue []*Item

func (pq PriorityQueue) Len() int { return len(pq) }

func (pq PriorityQueue) Less(i, j int) bool {
	if pq[i].cost == pq[j].cost {
		return pq[i].origin < pq[j].origin
	}
	return pq[i].cost < pq[j].cost
}

func (pq PriorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
	pq[i].index = i
	pq[j].index = j
}

func (pq *PriorityQueue) Push(x interface{}) {
	item := x.(*Item)
	item.index = len(*pq)
	*pq = append(*pq, item)
}

func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	item.index = -1
	*pq = old[0 : n-1]
	return item
}

// ServeVideos processes each video request and returns a slice of results.
// Each result is a tuple (serving_server, total_cost).
// If a request cannot be served, the corresponding result is (-1, -1).
func ServeVideos(servers []int, videos []string, storage map[int][]string, network [][3]int, requests [][2]interface{}) [][2]int {
	// Build a set of valid servers.
	validServers := make(map[int]bool)
	for _, s := range servers {
		validServers[s] = true
	}

	// Build a set of valid videos.
	validVideos := make(map[string]bool)
	for _, v := range videos {
		validVideos[v] = true
	}

	// Build a mapping from video to the list of source servers that store it.
	videoSources := make(map[string][]int)
	for server, vids := range storage {
		if !validServers[server] {
			continue
		}
		for _, vid := range vids {
			if validVideos[vid] {
				videoSources[vid] = append(videoSources[vid], server)
			}
		}
	}

	// Prepare a mapping from video to its requests.
	type requestEntry struct {
		reqIndex   int
		userServer int
	}
	videoRequests := make(map[string][]requestEntry)
	results := make([][2]int, len(requests))
	for i := range results {
		results[i] = [2]int{-1, -1}
	}
	for i, req := range requests {
		userServer, ok1 := req[0].(int)
		videoName, ok2 := req[1].(string)
		if !ok1 || !ok2 || !validServers[userServer] || !validVideos[videoName] {
			// Invalid request; results[i] remains (-1, -1).
			continue
		}
		videoRequests[videoName] = append(videoRequests[videoName], requestEntry{reqIndex: i, userServer: userServer})
	}

	// Build the graph as an adjacency list.
	graph := make(map[int][]Edge)
	for _, link := range network {
		u := link[0]
		v := link[1]
		w := link[2]
		if !validServers[u] || !validServers[v] {
			continue
		}
		graph[u] = append(graph[u], Edge{to: v, weight: w})
		graph[v] = append(graph[v], Edge{to: u, weight: w})
	}

	// Process each video request group with multi-source Dijkstra.
	for video, reqList := range videoRequests {
		sources, ok := videoSources[video]
		if !ok || len(sources) == 0 {
			// No server has this video; leave requests as (-1, -1).
			continue
		}
		// Initialize distance and origin maps.
		dist := make(map[int]int)
		originMap := make(map[int]int)
		for s := range validServers {
			dist[s] = math.MaxInt64
		}

		// Initialize the priority queue with all source servers.
		pq := &PriorityQueue{}
		heap.Init(pq)
		for _, s := range sources {
			if !validServers[s] {
				continue
			}
			if 0 < dist[s] {
				dist[s] = 0
				originMap[s] = s
				heap.Push(pq, &Item{cost: 0, vertex: s, origin: s})
			} else if 0 == dist[s] && s < originMap[s] {
				originMap[s] = s
			}
		}

		// Run multi-source Dijkstra.
		for pq.Len() > 0 {
			item := heap.Pop(pq).(*Item)
			currentCost := item.cost
			u := item.vertex
			orig := item.origin
			if currentCost > dist[u] {
				continue
			}
			for _, edge := range graph[u] {
				newCost := currentCost + edge.weight
				if newCost < dist[edge.to] {
					dist[edge.to] = newCost
					originMap[edge.to] = orig
					heap.Push(pq, &Item{cost: newCost, vertex: edge.to, origin: orig})
				} else if newCost == dist[edge.to] && orig < originMap[edge.to] {
					originMap[edge.to] = orig
					heap.Push(pq, &Item{cost: newCost, vertex: edge.to, origin: orig})
				}
			}
		}

		// Answer all requests for this video.
		for _, entry := range reqList {
			user := entry.userServer
			if d, exists := dist[user]; exists && d != math.MaxInt64 {
				results[entry.reqIndex] = [2]int{originMap[user], d}
			} else {
				results[entry.reqIndex] = [2]int{-1, -1}
			}
		}
	}
	return results
}