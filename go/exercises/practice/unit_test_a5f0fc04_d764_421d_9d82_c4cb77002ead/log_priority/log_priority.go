package logpriority

// LogEvent represents a single log event
type LogEvent struct {
	Timestamp int64
	Severity  string
	Message   string
	Origin    string
}

// LogAggregator interface defines the methods required for a log aggregator
type LogAggregator interface {
	Ingest(event LogEvent)
	GetTopN(n int) []LogEvent
}

// Implementation of the LogAggregator will be provided by the student.
// NewLogAggregator should return an object that implements the LogAggregator interface.
func NewLogAggregator() LogAggregator {
	// Student will implement this
	return nil
}