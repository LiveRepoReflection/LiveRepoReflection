package data_percentiles

import (
	"errors"
	"math"
	"sort"
	"sync"
	"time"
)

// AnalyticsPlatform defines the interface for the data percentiles system.
type AnalyticsPlatform interface {
	AddDataPoint(userID string, timestamp int64, value float64) error
	GetPercentile(userID string, percentile float64) (float64, error)
	SetCompressionFactor(compressionFactor float64) error // For adjusting approximation error
	SetDecayFactor(decayFactor float64) error             // For enabling time decay (optional)
}

// dataPoint represents an individual event with a timestamp and value.
type dataPoint struct {
	timestamp int64
	value     float64
}

// userData stores data points for a specific user along with a lock for concurrent access.
type userData struct {
	lock sync.Mutex
	data []dataPoint
}

// analyticsPlatform is the concrete implementation of AnalyticsPlatform.
type analyticsPlatform struct {
	users             map[string]*userData
	usersLock         sync.RWMutex
	configLock        sync.Mutex
	compressionFactor float64 // currently unused in calculations, placeholder for future optimizations.
	decayFactor       float64 // valid range: (0, 1]. 0 means no decay.
}

// NewAnalyticsPlatform creates and returns a new instance of AnalyticsPlatform.
func NewAnalyticsPlatform() (AnalyticsPlatform, error) {
	return &analyticsPlatform{
		users:             make(map[string]*userData),
		compressionFactor: 100.0, // default value
		decayFactor:       0.0,   // no time decay by default
	}, nil
}

// AddDataPoint ingests a new data point for a user.
func (ap *analyticsPlatform) AddDataPoint(userID string, timestamp int64, value float64) error {
	if userID == "" {
		return errors.New("userID cannot be empty")
	}

	// Retrieve or create userData
	ap.usersLock.RLock()
	ud, exists := ap.users[userID]
	ap.usersLock.RUnlock()
	if !exists {
		// Need to create new userData under write lock
		ap.usersLock.Lock()
		if ud, exists = ap.users[userID]; !exists {
			ud = &userData{
				data: make([]dataPoint, 0),
			}
			ap.users[userID] = ud
		}
		ap.usersLock.Unlock()
	}

	// Lock the user's data and append the new data point.
	ud.lock.Lock()
	defer ud.lock.Unlock()
	ud.data = append(ud.data, dataPoint{timestamp: timestamp, value: value})
	return nil
}

// GetPercentile returns the approximate percentile for the given user.
// If decayFactor is set (> 0), it computes a weighted percentile with exponential decay.
func (ap *analyticsPlatform) GetPercentile(userID string, percentile float64) (float64, error) {
	if percentile < 0 || percentile > 100 {
		return 0, errors.New("percentile must be between 0 and 100")
	}

	// Retrieve userData
	ap.usersLock.RLock()
	ud, exists := ap.users[userID]
	ap.usersLock.RUnlock()
	if !exists {
		return 0, errors.New("user not found")
	}

	ud.lock.Lock()
	if len(ud.data) == 0 {
		ud.lock.Unlock()
		return 0, errors.New("no data available for user")
	}
	// Make a copy of data points for processing.
	dataCopy := make([]dataPoint, len(ud.data))
	copy(dataCopy, ud.data)
	ud.lock.Unlock()

	// Sort data points by their value.
	sort.Slice(dataCopy, func(i, j int) bool {
		return dataCopy[i].value < dataCopy[j].value
	})

	// Check decay configuration.
	ap.configLock.Lock()
	decay := ap.decayFactor
	ap.configLock.Unlock()

	// If no decay factor is set, use the simple index-based approach.
	if decay == 0 {
		n := len(dataCopy)
		// Handle edge cases for 0 and 100 percentiles explicitly.
		if percentile == 0 {
			return dataCopy[0].value, nil
		}
		if percentile == 100 {
			return dataCopy[n-1].value, nil
		}
		// Compute index: using nearest rank method.
		index := int(math.Ceil((percentile / 100.0) * float64(n)))
		if index > 0 {
			index = index - 1
		}
		return dataCopy[index].value, nil
	}

	// If a decay factor is set, compute weighted percentile.
	currentTime := time.Now().Unix()
	weights := make([]float64, len(dataCopy))
	var totalWeight float64
	for i, dp := range dataCopy {
		// Compute exponential decay weight based on time difference.
		age := float64(currentTime - dp.timestamp)
		weight := math.Exp(-decay * age)
		weights[i] = weight
		totalWeight += weight
	}

	// Determine the threshold weight that corresponds to the desired percentile.
	targetWeight := (percentile / 100.0) * totalWeight

	var cumulativeWeight float64
	for i, dp := range dataCopy {
		cumulativeWeight += weights[i]
		if cumulativeWeight >= targetWeight {
			return dp.value, nil
		}
	}

	// Fallback: return the maximum value if threshold is never reached.
	return dataCopy[len(dataCopy)-1].value, nil
}

// SetCompressionFactor configures the approximation error level.
// For simplicity, this implementation accepts any positive compression factor.
func (ap *analyticsPlatform) SetCompressionFactor(compressionFactor float64) error {
	if compressionFactor <= 0 {
		return errors.New("compressionFactor must be positive")
	}
	ap.configLock.Lock()
	ap.compressionFactor = compressionFactor
	ap.configLock.Unlock()
	return nil
}

// SetDecayFactor configures the decay factor for time weighting.
// Valid decayFactor values are in the range (0, 1]. A value outside this range is considered invalid.
func (ap *analyticsPlatform) SetDecayFactor(decayFactor float64) error {
	if decayFactor <= 0 || decayFactor > 1 {
		return errors.New("decayFactor must be in the range (0, 1]")
	}
	ap.configLock.Lock()
	ap.decayFactor = decayFactor
	ap.configLock.Unlock()
	return nil
}