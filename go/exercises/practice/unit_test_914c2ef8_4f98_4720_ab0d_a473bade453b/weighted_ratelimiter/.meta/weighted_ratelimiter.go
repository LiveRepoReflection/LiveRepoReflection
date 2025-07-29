package weighted_ratelimiter

import (
	"errors"
	"math/rand"
	"sync"
	"time"
)

// userLimiter tracks a user's rate limit state.
// buckets represent the remaining tokens in each bucket.
// capacities represent the original capacities based on bucket weights.
type userLimiter struct {
	buckets    []int
	capacities []int
	mutex      sync.Mutex
}

var (
	userLimiters   = make(map[string]*userLimiter)
	userLimitersMu sync.RWMutex

	rnd   = rand.New(rand.NewSource(time.Now().UnixNano()))
	rndMu sync.Mutex
)

// UpdateUserLimits updates or creates the rate limiter configuration for a given user.
// numBuckets is the number of buckets, bucketWeights is the slice of weights for each bucket and totalLimit is the total token limit.
// The sum of bucketWeights must equal 100; otherwise, an error is returned.
func UpdateUserLimits(userID string, numBuckets int, bucketWeights []int, totalLimit int) error {
	if len(bucketWeights) != numBuckets {
		return errors.New("number of bucket weights does not match numBuckets")
	}
	sum := 0
	for _, w := range bucketWeights {
		sum += w
	}
	if sum != 100 {
		return errors.New("sum of bucket weights must be 100")
	}

	buckets := make([]int, numBuckets)
	capacities := make([]int, numBuckets)
	for i, weight := range bucketWeights {
		// Calculate capacity for each bucket proportional to its weight.
		capacity := totalLimit * weight / 100
		buckets[i] = capacity
		capacities[i] = capacity
	}

	ul := &userLimiter{
		buckets:    buckets,
		capacities: capacities,
	}

	userLimitersMu.Lock()
	defer userLimitersMu.Unlock()
	userLimiters[userID] = ul
	return nil
}

// Allow checks if a request with a given cost for the specified userID can be allowed.
// It picks one of the user's buckets uniformly at random and, if that bucket has enough tokens,
// it deducts the cost and returns true. Otherwise, it returns false.
func Allow(userID string, cost int) bool {
	userLimitersMu.RLock()
	ul, ok := userLimiters[userID]
	userLimitersMu.RUnlock()
	if !ok {
		return false
	}

	rndMu.Lock()
	idx := rnd.Intn(len(ul.buckets))
	rndMu.Unlock()

	ul.mutex.Lock()
	defer ul.mutex.Unlock()
	if ul.buckets[idx] >= cost {
		ul.buckets[idx] -= cost
		return true
	}
	return false
}