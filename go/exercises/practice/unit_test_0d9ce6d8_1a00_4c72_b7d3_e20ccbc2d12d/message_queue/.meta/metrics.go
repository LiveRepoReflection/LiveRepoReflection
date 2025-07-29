package message_queue

import (
	"sync/atomic"
	"time"
)

// Metrics tracks various statistics about the message queue
type Metrics struct {
	totalMessagesPublished uint64
	totalMessagesDelivered uint64
	totalSubscriptions     uint64
	startTime             time.Time
}

// NewMetrics creates a new Metrics instance
func NewMetrics() *Metrics {
	return &Metrics{
		startTime: time.Now(),
	}
}

// IncrementPublished increments the total messages published counter
func (m *Metrics) IncrementPublished() {
	atomic.AddUint64(&m.totalMessagesPublished, 1)
}

// IncrementDelivered increments the total messages delivered counter
func (m *Metrics) IncrementDelivered() {
	atomic.AddUint64(&m.totalMessagesDelivered, 1)
}

// IncrementSubscriptions increments the total subscriptions counter
func (m *Metrics) IncrementSubscriptions() {
	atomic.AddUint64(&m.totalSubscriptions, 1)
}

// DecrementSubscriptions decrements the total subscriptions counter
func (m *Metrics) DecrementSubscriptions() {
	atomic.AddUint64(&m.totalSubscriptions, ^uint64(0))
}

// GetStats returns the current metrics
func (m *Metrics) GetStats() (published, delivered, subscriptions uint64, uptime time.Duration) {
	published = atomic.LoadUint64(&m.totalMessagesPublished)
	delivered = atomic.LoadUint64(&m.totalMessagesDelivered)
	subscriptions = atomic.LoadUint64(&m.totalSubscriptions)
	uptime = time.Since(m.startTime)
	return
}