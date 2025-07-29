package social_reach

import (
	"sync"
)

// SocialGraph represents a directed social network graph where each user can follow others.
type SocialGraph struct {
	// graph maps a follower user ID to a set of followee user IDs.
	graph map[int64]map[int64]struct{}
	mu    sync.RWMutex
}

// NewSocialGraph creates and returns a pointer to a new SocialGraph.
func NewSocialGraph() *SocialGraph {
	return &SocialGraph{
		graph: make(map[int64]map[int64]struct{}),
	}
}

// AddFollow adds a directed edge from follower to followee. It returns an error only if the operation fails.
func (sg *SocialGraph) AddFollow(follower, followee int64) error {
	// Acquire write lock for modifying the graph.
	sg.mu.Lock()
	defer sg.mu.Unlock()

	// Initialize the follower's set if it does not exist.
	if _, exists := sg.graph[follower]; !exists {
		sg.graph[follower] = make(map[int64]struct{})
	}
	// Add the followee to the follower's set.
	sg.graph[follower][followee] = struct{}{}
	return nil
}

// IsReachable checks whether user 'source' can reach user 'target' via one or more follows.
// A user is always considered reachable from itself.
func (sg *SocialGraph) IsReachable(source, target int64) bool {
	// Early exit: a user is always reachable from itself.
	if source == target {
		return true
	}

	// Acquire read lock for traversing the graph.
	sg.mu.RLock()
	defer sg.mu.RUnlock()

	visited := make(map[int64]struct{})
	queue := []int64{source}
	visited[source] = struct{}{}

	// Perform a BFS starting from source.
	for len(queue) > 0 {
		// Dequeue the first element.
		current := queue[0]
		queue = queue[1:]
		// Get the list of followees for the current user.
		if followers, exists := sg.graph[current]; exists {
			for followee := range followers {
				// If we reach the target, return true.
				if followee == target {
					return true
				}
				// If not yet visited, add to the queue.
				if _, seen := visited[followee]; !seen {
					visited[followee] = struct{}{}
					queue = append(queue, followee)
				}
			}
		}
	}
	return false
}