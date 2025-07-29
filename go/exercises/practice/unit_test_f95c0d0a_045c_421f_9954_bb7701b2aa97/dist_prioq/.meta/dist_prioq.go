package dist_prioq

import (
	"container/heap"
	"errors"
	"hash/fnv"
	"sync"
	"sync/atomic"
	"time"
)

// Item represents an element in the priority queue.
type Item struct {
	Value     string
	Priority  int
	Timestamp int64
}

// DistributedPrioQueue represents the distributed priority queue system.
type DistributedPrioQueue interface {
	Enqueue(item Item) error
	Dequeue() (Item, error)
	Stop()
	FailNode(nodeID int) error
}

// queueItem is an internal wrapper for Item including metadata.
type queueItem struct {
	id      int64
	item    Item
	primary int // primary node index
	backup  int // backup node index (replica)
}

// PriorityQueue implements heap.Interface for queueItem pointers.
type PriorityQueue []*queueItem

func (pq PriorityQueue) Len() int { return len(pq) }
func (pq PriorityQueue) Less(i, j int) bool {
	// Higher priority first; if equal, earlier Timestamp wins.
	if pq[i].item.Priority == pq[j].item.Priority {
		return pq[i].item.Timestamp < pq[j].item.Timestamp
	}
	return pq[i].item.Priority > pq[j].item.Priority
}
func (pq PriorityQueue) Swap(i, j int) { pq[i], pq[j] = pq[j], pq[i] }
func (pq *PriorityQueue) Push(x interface{}) {
	*pq = append(*pq, x.(*queueItem))
}
func (pq *PriorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	x := old[n-1]
	*pq = old[0 : n-1]
	return x
}

// node represents a single node in the distributed system.
type node struct {
	id    int
	queue PriorityQueue
	alive bool
	lock  sync.Mutex
}

// distributedPrioQueue is the main structure implementing DistributedPrioQueue.
type distributedPrioQueue struct {
	nodes []*node
	mu    sync.Mutex
	stop  int32 // 0 running, 1 stopped
}

// globalID is a counter for unique queue item identifiers.
var globalID int64

// InitializeSystem initializes the distributed priority queue with numNodes.
func InitializeSystem(numNodes int) (DistributedPrioQueue, error) {
	if numNodes <= 0 {
		return nil, errors.New("numNodes must be positive")
	}
	dpq := &distributedPrioQueue{
		nodes: make([]*node, numNodes),
	}
	for i := 0; i < numNodes; i++ {
		n := &node{
			id:    i,
			queue: make(PriorityQueue, 0),
			alive: true,
		}
		heap.Init(&n.queue)
		dpq.nodes[i] = n
	}
	return dpq, nil
}

// hashValue computes a simple hash of a string.
func hashValue(s string) uint32 {
	h := fnv.New32a()
	h.Write([]byte(s))
	return h.Sum32()
}

// Enqueue inserts an item into the distributed priority queue.
func (dpq *distributedPrioQueue) Enqueue(item Item) error {
	if atomic.LoadInt32(&dpq.stop) == 1 {
		return errors.New("system stopped")
	}
	// Generate unique id and assign timestamp if not set.
	id := atomic.AddInt64(&globalID, 1)
	if item.Timestamp == 0 {
		item.Timestamp = time.Now().UnixNano()
	}
	numNodes := len(dpq.nodes)
	hashVal := hashValue(item.Value)
	primary := int(hashVal % uint32(numNodes))
	backup := (primary + 1) % numNodes

	qi := &queueItem{
		id:      id,
		item:    item,
		primary: primary,
		backup:  backup,
	}

	// Insert into primary node if alive.
	dpq.nodes[primary].lock.Lock()
	if dpq.nodes[primary].alive {
		heap.Push(&dpq.nodes[primary].queue, qi)
	}
	dpq.nodes[primary].lock.Unlock()

	// Always insert a replica into the backup node.
	dpq.nodes[backup].lock.Lock()
	heap.Push(&dpq.nodes[backup].queue, qi)
	dpq.nodes[backup].lock.Unlock()

	return nil
}

// removeItemByID removes a queueItem with the given id from the node's queue.
func removeItemByID(n *node, id int64) {
	n.lock.Lock()
	defer n.lock.Unlock()
	for i, qi := range n.queue {
		if qi.id == id {
			heap.Remove(&n.queue, i)
			break
		}
	}
}

// removeCandidate removes the candidate item from both its primary and backup nodes.
func (dpq *distributedPrioQueue) removeCandidate(qi *queueItem) {
	// Remove from primary node.
	if qi.primary >= 0 && qi.primary < len(dpq.nodes) {
		removeItemByID(dpq.nodes[qi.primary], qi.id)
	}
	// Remove from backup node.
	if qi.backup >= 0 && qi.backup < len(dpq.nodes) {
		removeItemByID(dpq.nodes[qi.backup], qi.id)
	}
}

// Dequeue extracts the highest-priority item from the distributed system.
func (dpq *distributedPrioQueue) Dequeue() (Item, error) {
	if atomic.LoadInt32(&dpq.stop) == 1 {
		return Item{}, errors.New("system stopped")
	}
	dpq.mu.Lock()
	defer dpq.mu.Unlock()

	var candidate *queueItem
	// Iterate over all nodes to find the best candidate among alive nodes.
	for _, n := range dpq.nodes {
		n.lock.Lock()
		if n.alive && n.queue.Len() > 0 {
			top := n.queue[0]
			if candidate == nil {
				candidate = top
			} else {
				if top.item.Priority > candidate.item.Priority ||
					(top.item.Priority == candidate.item.Priority && top.item.Timestamp < candidate.item.Timestamp) {
					candidate = top
				}
			}
		}
		n.lock.Unlock()
	}
	if candidate == nil {
		return Item{}, errors.New("no items to dequeue")
	}
	// Remove the candidate from both primary and backup nodes.
	dpq.removeCandidate(candidate)
	return candidate.item, nil
}

// Stop terminates the distributed system.
func (dpq *distributedPrioQueue) Stop() {
	atomic.StoreInt32(&dpq.stop, 1)
}

// FailNode simulates a failure of a node identified by nodeID.
func (dpq *distributedPrioQueue) FailNode(nodeID int) error {
	if nodeID < 0 || nodeID >= len(dpq.nodes) {
		return errors.New("invalid nodeID")
	}
	dpq.nodes[nodeID].lock.Lock()
	dpq.nodes[nodeID].alive = false
	dpq.nodes[nodeID].lock.Unlock()
	return nil
}