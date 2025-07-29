package data_stats

import (
	"math"
	"sort"
	"sync"
)

type event struct {
	timestamp int64
	value     int
}

type sensorData struct {
	mu         sync.Mutex
	events     []event
	sum        int64
	sumSquares int64
	count      int
}

type DataStreamProcessor struct {
	windowSize int64
	mu         sync.RWMutex
	globalMax  int64
	sensors    map[string]*sensorData
}

// NewDataStreamProcessor creates a new DataStreamProcessor with the given time window in milliseconds.
func NewDataStreamProcessor(windowSizeMs int64) *DataStreamProcessor {
	return &DataStreamProcessor{
		windowSize: windowSizeMs,
		sensors:    make(map[string]*sensorData),
	}
}

// Ingest ingests a new data packet into the system.
func (dsp *DataStreamProcessor) Ingest(timestamp int64, sensorID string, value int) {
	// Update global max timestamp if needed.
	dsp.mu.Lock()
	if timestamp > dsp.globalMax {
		dsp.globalMax = timestamp
	}
	sd, exists := dsp.sensors[sensorID]
	if !exists {
		sd = &sensorData{}
		dsp.sensors[sensorID] = sd
	}
	dsp.mu.Unlock()

	// Insert the event in the sensor's event list.
	sd.mu.Lock()
	newEvent := event{timestamp: timestamp, value: value}
	n := len(sd.events)
	if n == 0 || sd.events[n-1].timestamp <= timestamp {
		sd.events = append(sd.events, newEvent)
	} else {
		idx := sort.Search(n, func(i int) bool { return sd.events[i].timestamp > timestamp })
		sd.events = append(sd.events, event{})
		copy(sd.events[idx+1:], sd.events[idx:])
		sd.events[idx] = newEvent
	}
	sd.sum += int64(value)
	sd.sumSquares += int64(value) * int64(value)
	sd.count++
	sd.mu.Unlock()
}

// purgeOldEvents removes events older than the given cutoff timestamp.
func (sd *sensorData) purgeOldEvents(cutoff int64) {
	idx := 0
	for idx < len(sd.events) && sd.events[idx].timestamp < cutoff {
		evt := sd.events[idx]
		sd.sum -= int64(evt.value)
		sd.sumSquares -= int64(evt.value) * int64(evt.value)
		sd.count--
		idx++
	}
	if idx > 0 {
		sd.events = sd.events[idx:]
	}
}

// GetStatistics retrieves the windowed average and standard deviation for the specified sensor.
func (dsp *DataStreamProcessor) GetStatistics(sensorID string) (average float64, stdDev float64, found bool) {
	dsp.mu.RLock()
	globalTime := dsp.globalMax
	sd, exists := dsp.sensors[sensorID]
	dsp.mu.RUnlock()
	if !exists {
		return 0.0, 0.0, false
	}

	sd.mu.Lock()
	cutoff := globalTime - dsp.windowSize
	sd.purgeOldEvents(cutoff)
	if sd.count == 0 {
		sd.mu.Unlock()
		return 0.0, 0.0, false
	}
	avg := float64(sd.sum) / float64(sd.count)
	if sd.count > 1 {
		variance := (float64(sd.sumSquares) - (float64(sd.sum)*float64(sd.sum))/float64(sd.count)) / float64(sd.count-1)
		if variance < 0 {
			variance = 0
		}
		stdDev = math.Sqrt(variance)
	} else {
		stdDev = 0.0
	}
	sd.mu.Unlock()
	return avg, stdDev, true
}