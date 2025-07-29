package social_fof

import (
	"sort"
	"sync"
)

var (
	graph = make(map[int]map[int]struct{})
	mu    sync.RWMutex
)

// AddFriendship adds a bidirectional friendship between user u and user v.
func AddFriendship(u, v int) {
	mu.Lock()
	defer mu.Unlock()
	if graph[u] == nil {
		graph[u] = make(map[int]struct{})
	}
	if graph[v] == nil {
		graph[v] = make(map[int]struct{})
	}
	graph[u][v] = struct{}{}
	graph[v][u] = struct{}{}
}

// getFriends retrieves a slice of direct friends for the given user.
func getFriends(user int) []int {
	mu.RLock()
	defer mu.RUnlock()
	friendsSet, exists := graph[user]
	if !exists {
		return []int{}
	}
	var friends []int
	for id := range friendsSet {
		friends = append(friends, id)
	}
	return friends
}

// FindFoF returns a sorted slice of unique friends-of-friends for the given user.
// It excludes the user itself and their direct friends.
func FindFoF(user int) []int {
	// Retrieve direct friends of the user.
	directFriends := getFriends(user)
	directSet := make(map[int]struct{})
	for _, f := range directFriends {
		directSet[f] = struct{}{}
	}

	// Use candidateSet to collect FoF candidates.
	candidateSet := make(map[int]struct{})
	var wg sync.WaitGroup

	// Mutex to protect concurrent access to candidateSet.
	var candMu sync.Mutex

	// For each direct friend, concurrently gather their friends.
	for _, friend := range directFriends {
		wg.Add(1)
		go func(friend int) {
			defer wg.Done()
			neighbors := getFriends(friend)
			// Use a local set to eliminate duplicates in this branch.
			localSet := make(map[int]struct{})
			for _, candidate := range neighbors {
				localSet[candidate] = struct{}{}
			}
			candMu.Lock()
			for candidate := range localSet {
				candidateSet[candidate] = struct{}{}
			}
			candMu.Unlock()
		}(friend)
	}
	wg.Wait()

	// Exclude the user and their direct friends from the FoF set.
	delete(candidateSet, user)
	for direct := range directSet {
		delete(candidateSet, direct)
	}

	// Convert the remaining candidates to a slice and sort it.
	var result []int
	for candidate := range candidateSet {
		result = append(result, candidate)
	}
	sort.Ints(result)
	return result
}