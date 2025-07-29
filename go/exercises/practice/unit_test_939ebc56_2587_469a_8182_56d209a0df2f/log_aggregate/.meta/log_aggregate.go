package log_aggregate

import (
    "fmt"
    "sort"
    "sync"
)

// LogEntry represents a single log entry in the system
type LogEntry struct {
    Timestamp     int64
    ApplicationID string
    LogLevel      int
    Message       string
}

// LogSystem represents the log aggregation system
type LogSystem struct {
    // Main storage for logs, keyed by ApplicationID
    logs map[string]*applicationLogs
    // Mutex for concurrent access
    mutex sync.RWMutex
}

// applicationLogs holds logs for a specific application
type applicationLogs struct {
    entries []LogEntry
    // Mutex for concurrent access within a single application's logs
    mutex sync.RWMutex
}

// NewLogSystem creates a new instance of LogSystem
func NewLogSystem() *LogSystem {
    return &LogSystem{
        logs: make(map[string]*applicationLogs),
    }
}

// IngestLog adds a new log entry to the system
func (s *LogSystem) IngestLog(entry LogEntry) error {
    if entry.LogLevel < 1 || entry.LogLevel > 5 {
        return fmt.Errorf("invalid log level: %d", entry.LogLevel)
    }

    s.mutex.Lock()
    appLogs, exists := s.logs[entry.ApplicationID]
    if !exists {
        appLogs = &applicationLogs{
            entries: make([]LogEntry, 0),
        }
        s.logs[entry.ApplicationID] = appLogs
    }
    s.mutex.Unlock()

    appLogs.mutex.Lock()
    defer appLogs.mutex.Unlock()

    // Verify timestamp ordering within application
    if len(appLogs.entries) > 0 && appLogs.entries[len(appLogs.entries)-1].Timestamp > entry.Timestamp {
        return fmt.Errorf("timestamp ordering violation for application %s", entry.ApplicationID)
    }

    appLogs.entries = append(appLogs.entries, entry)
    return nil
}

// QueryLogs retrieves log entries based on the specified criteria
func (s *LogSystem) QueryLogs(startTime, endTime int64, appIDs []string, minLogLevel int) ([]LogEntry, error) {
    if startTime > endTime {
        return nil, fmt.Errorf("invalid time range: start time %d is after end time %d", startTime, endTime)
    }

    if minLogLevel < 0 || minLogLevel > 5 {
        return nil, fmt.Errorf("invalid minimum log level: %d", minLogLevel)
    }

    result := make([]LogEntry, 0)

    s.mutex.RLock()
    defer s.mutex.RUnlock()

    // If no specific appIDs provided, query all applications
    if len(appIDs) == 0 {
        for _, appLogs := range s.logs {
            entries := s.queryApplicationLogs(appLogs, startTime, endTime, minLogLevel)
            result = append(result, entries...)
        }
    } else {
        // Query only specified applications
        for _, appID := range appIDs {
            if appLogs, exists := s.logs[appID]; exists {
                entries := s.queryApplicationLogs(appLogs, startTime, endTime, minLogLevel)
                result = append(result, entries...)
            }
        }
    }

    // Sort results by timestamp
    sort.Slice(result, func(i, j int) bool {
        return result[i].Timestamp < result[j].Timestamp
    })

    return result, nil
}

// queryApplicationLogs performs binary search and filtering for a single application's logs
func (s *LogSystem) queryApplicationLogs(appLogs *applicationLogs, startTime, endTime int64, minLogLevel int) []LogEntry {
    appLogs.mutex.RLock()
    defer appLogs.mutex.RUnlock()

    result := make([]LogEntry, 0)

    // Find start index using binary search
    startIdx := sort.Search(len(appLogs.entries), func(i int) bool {
        return appLogs.entries[i].Timestamp >= startTime
    })

    // Collect matching entries
    for i := startIdx; i < len(appLogs.entries); i++ {
        entry := appLogs.entries[i]
        if entry.Timestamp > endTime {
            break
        }
        if entry.LogLevel >= minLogLevel || minLogLevel == 0 {
            result = append(result, entry)
        }
    }

    return result
}