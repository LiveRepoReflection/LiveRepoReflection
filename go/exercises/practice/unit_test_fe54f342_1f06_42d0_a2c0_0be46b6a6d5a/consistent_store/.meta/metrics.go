package consistentstore

import (
	"sync/atomic"
	"time"
)

type Metrics struct {
	TotalRequests     uint64
	SuccessfulGets    uint64
	SuccessfulPuts    uint64
	FailedRequests    uint64
	AverageLatency    uint64 // in nanoseconds
	lastLatencyUpdate int64
}

func (m *Metrics) RecordRequest(success bool, duration time.Duration) {
	atomic.AddUint64(&m.TotalRequests, 1)
	if success {
		atomic.AddUint64(&m.SuccessfulGets, 1)
	} else {
		atomic.AddUint64(&m.FailedRequests, 1)
	}

	// Update average latency
	currentAvg := atomic.LoadUint64(&m.AverageLatency)
	newLatency := uint64(duration.Nanoseconds())
	atomic.StoreUint64(&m.AverageLatency, (currentAvg+newLatency)/2)
}

func (m *Metrics) GetTotalRequests() uint64 {
	return atomic.LoadUint64(&m.TotalRequests)
}

func (m *Metrics) GetSuccessfulRequests() uint64 {
	return atomic.LoadUint64(&m.SuccessfulGets)
}

func (m *Metrics) GetFailedRequests() uint64 {
	return atomic.LoadUint64(&m.FailedRequests)
}

func (m *Metrics) GetAverageLatency() time.Duration {
	return time.Duration(atomic.LoadUint64(&m.AverageLatency))
}