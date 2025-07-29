package datastream

import (
	"container/heap"
	"errors"
	"math"
	"sort"
	"sync"
	"time"
)

// DataStream represents a real-time data analytics system for sensor networks
type DataStream struct {
	numSensors       int
	maxRetentionSec  int64
	dataStore        map[int]map[int64][]float64 // sensorID -> timestamp -> values
	currentTimestamp int64                        // Used for retention management
	mu               sync.RWMutex                 // Protects the data store
}

// NewDataStream creates a new DataStream with the specified number of sensors and retention period
func NewDataStream(numSensors int, maxRetentionSec int64) *DataStream {
	return &DataStream{
		numSensors:       numSensors,
		maxRetentionSec:  maxRetentionSec,
		dataStore:        make(map[int]map[int64][]float64),
		currentTimestamp: time.Now().Unix(),
	}
}

// IngestData adds a data point to the system
func (ds *DataStream) IngestData(sensorID int, timestamp int64, value float64) error {
	if sensorID < 0 || sensorID >= ds.numSensors {
		return errors.New("sensor ID out of range")
	}

	ds.mu.Lock()
	defer ds.mu.Unlock()

	// Update current timestamp if the new one is greater
	if timestamp > ds.currentTimestamp {
		ds.currentTimestamp = timestamp
		// Cleanup old data after updating timestamp
		ds.cleanupOldData()
	}

	// Check if data is too old to be stored
	if ds.currentTimestamp-timestamp > ds.maxRetentionSec {
		return nil // Silently ignore too old data
	}

	// Initialize sensor map if it doesn't exist
	if _, exists := ds.dataStore[sensorID]; !exists {
		ds.dataStore[sensorID] = make(map[int64][]float64)
	}

	// Add the data point
	ds.dataStore[sensorID][timestamp] = append(ds.dataStore[sensorID][timestamp], value)

	return nil
}

// cleanupOldData removes data points older than the retention period
func (ds *DataStream) cleanupOldData() {
	cutoffTimestamp := ds.currentTimestamp - ds.maxRetentionSec

	for sensorID, timestamps := range ds.dataStore {
		for timestamp := range timestamps {
			if timestamp < cutoffTimestamp {
				delete(ds.dataStore[sensorID], timestamp)
			}
		}
	}
}

// getDataPointsInWindow returns all data points within the specified time window
func (ds *DataStream) getDataPointsInWindow(startTime, endTime int64) []float64 {
	ds.mu.RLock()
	defer ds.mu.RUnlock()

	var result []float64
	for _, timestamps := range ds.dataStore {
		for timestamp, values := range timestamps {
			if timestamp >= startTime && timestamp <= endTime {
				result = append(result, values...)
			}
		}
	}

	return result
}

// CalculateMean computes the average value across all sensors within the specified time window
func (ds *DataStream) CalculateMean(startTime, endTime int64) (float64, error) {
	if startTime > endTime {
		return 0, errors.New("start time must be less than or equal to end time")
	}

	dataPoints := ds.getDataPointsInWindow(startTime, endTime)
	if len(dataPoints) == 0 {
		return 0, errors.New("no data points in the specified time window")
	}

	sum := 0.0
	for _, value := range dataPoints {
		sum += value
	}

	return sum / float64(len(dataPoints)), nil
}

// CalculateMedian computes the median value across all sensors within the specified time window
func (ds *DataStream) CalculateMedian(startTime, endTime int64) (float64, error) {
	if startTime > endTime {
		return 0, errors.New("start time must be less than or equal to end time")
	}

	dataPoints := ds.getDataPointsInWindow(startTime, endTime)
	if len(dataPoints) == 0 {
		return 0, errors.New("no data points in the specified time window")
	}

	// For smaller datasets, use exact median calculation
	if len(dataPoints) < 100000 {
		sort.Float64s(dataPoints)
		middle := len(dataPoints) / 2
		if len(dataPoints)%2 == 0 {
			return (dataPoints[middle-1] + dataPoints[middle]) / 2, nil
		}
		return dataPoints[middle], nil
	}

	// For larger datasets, use an approximate algorithm
	return ds.approximateMedian(dataPoints), nil
}

// approximateMedian uses a streaming algorithm to approximate the median
// This implementation uses a reservoir sampling approach combined with binning
func (ds *DataStream) approximateMedian(dataPoints []float64) float64 {
	const numBins = 100
	
	// Find min and max to create bins
	min, max := dataPoints[0], dataPoints[0]
	for _, v := range dataPoints {
		if v < min {
			min = v
		}
		if v > max {
			max = v
		}
	}
	
	// Add small delta to avoid edge cases
	max += 0.001
	
	// Create bins
	binSize := (max - min) / float64(numBins)
	bins := make([]int, numBins)
	
	// Count values in each bin
	for _, v := range dataPoints {
		binIndex := int((v - min) / binSize)
		if binIndex >= numBins {
			binIndex = numBins - 1
		}
		bins[binIndex]++
	}
	
	// Find the bin containing the median
	totalCount := len(dataPoints)
	medianPos := totalCount / 2
	countSoFar := 0
	medianBin := 0
	
	for i, count := range bins {
		countSoFar += count
		if countSoFar > medianPos {
			medianBin = i
			break
		}
	}
	
	// Approximate the median as the center of the bin
	return min + (float64(medianBin) + 0.5) * binSize
}

// CalculatePercentile computes the specified percentile across all sensors within the time window
func (ds *DataStream) CalculatePercentile(startTime, endTime int64, percentile float64) (float64, error) {
	if startTime > endTime {
		return 0, errors.New("start time must be less than or equal to end time")
	}
	
	if percentile < 0 || percentile > 100 {
		return 0, errors.New("percentile must be between 0 and 100")
	}

	dataPoints := ds.getDataPointsInWindow(startTime, endTime)
	if len(dataPoints) == 0 {
		return 0, errors.New("no data points in the specified time window")
	}

	// For smaller datasets, calculate exact percentile
	if len(dataPoints) < 100000 {
		sort.Float64s(dataPoints)
		index := int(math.Ceil(percentile/100 * float64(len(dataPoints)) - 1))
		if index < 0 {
			index = 0
		}
		return dataPoints[index], nil
	}

	// For larger datasets, use the GK algorithm (simplified version)
	return ds.approximatePercentile(dataPoints, percentile), nil
}

// approximatePercentile uses a simplified version of the GK algorithm for approximate percentiles
func (ds *DataStream) approximatePercentile(dataPoints []float64, percentile float64) float64 {
	const numQuantiles = 1000
	
	// Use a min heap to maintain the top k elements where k is a small sample
	sampleSize := min(len(dataPoints), 10000)
	
	// Initialize minHeap with the first sampleSize elements
	h := &minHeap{}
	heap.Init(h)
	
	// Fill the heap with initial values
	for i := 0; i < len(dataPoints) && i < sampleSize; i++ {
		heap.Push(h, dataPoints[i])
	}
	
	// Replace elements in heap if we find larger ones
	for i := sampleSize; i < len(dataPoints); i++ {
		if dataPoints[i] > (*h)[0] {
			heap.Pop(h)
			heap.Push(h, dataPoints[i])
		}
	}
	
	// Convert heap to sorted array
	sample := make([]float64, h.Len())
	for i := h.Len() - 1; i >= 0; i-- {
		sample[i] = heap.Pop(h).(float64)
	}
	
	// Calculate the index corresponding to the percentile
	index := int(math.Floor((percentile / 100) * float64(len(sample) - 1)))
	return sample[index]
}

// CalculateVariance computes the variance across all sensors within the specified time window
func (ds *DataStream) CalculateVariance(startTime, endTime int64) (float64, error) {
	if startTime > endTime {
		return 0, errors.New("start time must be less than or equal to end time")
	}

	dataPoints := ds.getDataPointsInWindow(startTime, endTime)
	if len(dataPoints) == 0 {
		return 0, errors.New("no data points in the specified time window")
	}

	// Calculate mean
	mean := 0.0
	for _, value := range dataPoints {
		mean += value
	}
	mean /= float64(len(dataPoints))

	// Calculate variance
	variance := 0.0
	for _, value := range dataPoints {
		diff := value - mean
		variance += diff * diff
	}
	variance /= float64(len(dataPoints))

	return variance, nil
}

// UpdateCurrentTime manually updates the current timestamp (mainly for testing)
func (ds *DataStream) UpdateCurrentTime(timestamp int64) {
	ds.mu.Lock()
	defer ds.mu.Unlock()
	
	ds.currentTimestamp = timestamp
	ds.cleanupOldData()
}

// Helper min function for int values
func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// minHeap is a min-heap implementation for float64 values
type minHeap []float64

func (h minHeap) Len() int           { return len(h) }
func (h minHeap) Less(i, j int) bool { return h[i] < h[j] }
func (h minHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *minHeap) Push(x interface{}) {
	*h = append(*h, x.(float64))
}

func (h *minHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}