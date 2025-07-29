package log_aggregator

import (
	"errors"
	"sort"
	"sync"
	"time"
)

type LogEntry struct {
	Timestamp int64
	Level     string
	Message   string
	AppID     string
}

type LogAggregator struct {
	logs      []LogEntry
	logsByApp map[string][]LogEntry
	levels    map[string]struct{}
	mu        sync.RWMutex
}

var validLevels = map[string]struct{}{
	"DEBUG": {},
	"INFO":  {},
	"WARN":  {},
	"ERROR": {},
	"FATAL": {},
}

func NewLogAggregator() *LogAggregator {
	return &LogAggregator{
		logs:      make([]LogEntry, 0),
		logsByApp: make(map[string][]LogEntry),
		levels:    make(map[string]struct{}),
	}
}

func (la *LogAggregator) IngestLog(timestamp int64, level, message, appID string) error {
	if _, valid := validLevels[level]; !valid {
		return errors.New("invalid log level")
	}

	if appID == "" {
		return errors.New("appID cannot be empty")
	}

	if timestamp > time.Now().UnixNano() {
		return errors.New("timestamp cannot be in the future")
	}

	entry := LogEntry{
		Timestamp: timestamp,
		Level:     level,
		Message:   message,
		AppID:     appID,
	}

	la.mu.Lock()
	defer la.mu.Unlock()

	la.logs = append(la.logs, entry)
	la.logsByApp[appID] = append(la.logsByApp[appID], entry)
	la.levels[level] = struct{}{}

	return nil
}

func (la *LogAggregator) QueryLogs(appID string, start, end int64, levels []string) ([]LogEntry, error) {
	if start > end {
		return nil, errors.New("start time must be before end time")
	}

	la.mu.RLock()
	defer la.mu.RUnlock()

	var logs []LogEntry
	if appID != "" {
		logs = la.logsByApp[appID]
	} else {
		logs = la.logs
	}

	levelSet := make(map[string]struct{})
	for _, l := range levels {
		levelSet[l] = struct{}{}
	}

	result := make([]LogEntry, 0)
	for _, log := range logs {
		if log.Timestamp < start || log.Timestamp > end {
			continue
		}

		if len(levels) > 0 {
			if _, ok := levelSet[log.Level]; !ok {
				continue
			}
		}

		result = append(result, log)
	}

	sort.Slice(result, func(i, j int) bool {
		return result[i].Timestamp < result[j].Timestamp
	})

	return result, nil
}

func (la *LogAggregator) GetLevelCounts(start, end int64) (map[string]int, error) {
	if start > end {
		return nil, errors.New("start time must be before end time")
	}

	la.mu.RLock()
	defer la.mu.RUnlock()

	counts := make(map[string]int)
	for level := range la.levels {
		counts[level] = 0
	}

	for _, log := range la.logs {
		if log.Timestamp >= start && log.Timestamp <= end {
			counts[log.Level]++
		}
	}

	return counts, nil
}

func (la *LogAggregator) Shutdown() {
	la.mu.Lock()
	defer la.mu.Unlock()

	la.logs = nil
	la.logsByApp = nil
	la.levels = nil
}