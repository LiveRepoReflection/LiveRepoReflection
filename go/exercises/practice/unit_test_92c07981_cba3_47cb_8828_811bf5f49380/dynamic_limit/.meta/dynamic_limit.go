package dynamic_limit

import (
	"net/http"
	"sync"
)

var (
	mutex           sync.Mutex
	currentCapacity int
	tokensUsed      int
)

// UpdateCapacity sets the new capacity and resets the used tokens.
// If a negative capacity is provided, it is treated as zero.
func UpdateCapacity(cap int) {
	mutex.Lock()
	defer mutex.Unlock()
	if cap < 0 {
		currentCapacity = 0
	} else {
		currentCapacity = cap
	}
	tokensUsed = 0
}

// Handler returns an HTTP handler which enforces rate limiting based on the current capacity.
// For each incoming request, if the number of requests served in the current cycle is less than
// the current capacity, the request is allowed and returns 200. Otherwise, it returns 429.
func Handler() http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		mutex.Lock()
		defer mutex.Unlock()
		if tokensUsed < currentCapacity {
			tokensUsed++
			w.WriteHeader(http.StatusOK)
		} else {
			w.WriteHeader(http.StatusTooManyRequests)
		}
	})
}