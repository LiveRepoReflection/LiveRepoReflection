package distributed_logs

import (
	"errors"
	"sort"
	"sync"
	"time"
)

type Severity string

const (
	DEBUG Severity = "DEBUG"
	INFO  Severity = "INFO"
	WARN  Severity = "WARN"
	ERROR Severity = "ERROR"
)

type LogEntry struct {
	Timestamp int64
	Severity  Severity
	Message   string
}

type Config struct {
	ProducerCount   int
	CollectorCount  int
	AggregatorCount int
	LogRate         int
}

type Aggregator struct {
	mu               sync.Mutex
	logs             []LogEntry
	logSet           map[string]bool
	config           Config
	transientFailure bool
}

// NewAggregator creates a new Aggregator instance.
func NewAggregator() *Aggregator {
	return &Aggregator{
		logs:    make([]LogEntry, 0),
		logSet:  make(map[string]bool),
		config:  Config{},
	}
}

// AddLog adds a log entry with a retry mechanism to handle transient failures.
func (a *Aggregator) AddLog(entry LogEntry) error {
	const maxAttempts = 4
	var err error
	for attempt := 0; attempt < maxAttempts; attempt++ {
		err = a.attemptAddLog(entry, attempt)
		if err == nil {
			return nil
		}
		// Exponential backoff: sleep 10ms * 2^attempt
		time.Sleep(time.Duration(10*(1<<attempt)) * time.Millisecond)
	}
	return err
}

// attemptAddLog tries to add a log entry, simulating a transient failure on the first attempt if activated.
func (a *Aggregator) attemptAddLog(entry LogEntry, attempt int) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	// Simulate transient failure only on the first attempt.
	if a.transientFailure && attempt == 0 {
		return errors.New("transient failure occurred")
	}
	// Check for duplicates based on a composite key.
	key := generateLogKey(entry)
	if _, exists := a.logSet[key]; exists {
		return nil // Duplicate log; skip adding.
	}
	a.logs = append(a.logs, entry)
	a.logSet[key] = true
	return nil
}

// generateLogKey creates a unique key for a log entry based on its fields.
func generateLogKey(entry LogEntry) string {
	return string(entry.Severity) + "_" + time.Unix(0, entry.Timestamp).Format(time.RFC3339Nano) + "_" + entry.Message
}

// QueryLogs returns logs between start and end timestamps (inclusive).
// If severity is non-empty, it returns logs with severity equal to or higher than the specified severity.
// Severity hierarchy: DEBUG < INFO < WARN < ERROR.
func (a *Aggregator) QueryLogs(start, end int64, severity Severity) ([]LogEntry, error) {
	a.mu.Lock()
	defer a.mu.Unlock()
	var result []LogEntry
	for _, log := range a.logs {
		if log.Timestamp >= start && log.Timestamp <= end {
			if severity == "" || severityPriority(log.Severity) >= severityPriority(severity) {
				result = append(result, log)
			}
		}
	}
	// Sort logs by timestamp.
	sort.Slice(result, func(i, j int) bool {
		return result[i].Timestamp < result[j].Timestamp
	})
	return result, nil
}

// severityPriority returns a numerical priority for a given severity.
func severityPriority(s Severity) int {
	switch s {
	case DEBUG:
		return 1
	case INFO:
		return 2
	case WARN:
		return 3
	case ERROR:
		return 4
	default:
		return 0
	}
}

// UpdateConfig updates the aggregator's configuration.
func (a *Aggregator) UpdateConfig(newConfig Config) error {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.config = newConfig
	return nil
}

// GetConfig returns the current configuration.
func (a *Aggregator) GetConfig() Config {
	a.mu.Lock()
	defer a.mu.Unlock()
	return a.config
}

// SetTransientFailure sets the transient failure flag.
func (a *Aggregator) SetTransientFailure(flag bool) {
	a.mu.Lock()
	defer a.mu.Unlock()
	a.transientFailure = flag
}