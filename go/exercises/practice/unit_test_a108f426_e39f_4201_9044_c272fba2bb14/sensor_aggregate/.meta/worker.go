package sensor_aggregate

import "sync"

type Worker struct {
	id                 string
	windowStart        int64
	windowEnd          int64
	partialAggregation map[string]int
	mu                 sync.Mutex
}

func NewWorker(id string, windowStart, windowEnd int64) *Worker {
	return &Worker{
		id:                 id,
		windowStart:        windowStart,
		windowEnd:          windowEnd,
		partialAggregation: make(map[string]int),
	}
}

func (w *Worker) ProcessSensorData(sensorID string, timestamp int64, data map[string]int) error {
	// Accept data only if the timestamp is within the window [windowStart, windowEnd] inclusive.
	if timestamp < w.windowStart || timestamp > w.windowEnd {
		return nil
	}

	w.mu.Lock()
	defer w.mu.Unlock()

	for key, value := range data {
		w.partialAggregation[key] += value
	}
	return nil
}

func (w *Worker) SendAggregation() map[string]int {
	w.mu.Lock()
	defer w.mu.Unlock()

	result := make(map[string]int)
	for key, value := range w.partialAggregation {
		result[key] = value
	}
	return result
}