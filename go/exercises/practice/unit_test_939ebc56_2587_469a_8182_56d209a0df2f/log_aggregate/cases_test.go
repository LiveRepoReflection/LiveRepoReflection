package log_aggregate

var testCases = []struct {
    description string
    operations  []operation
    expected    []expectedResult
}{
    {
        description: "Basic ingest and query",
        operations: []operation{
            {
                opType: "ingest",
                entry: LogEntry{
                    Timestamp:     1000,
                    ApplicationID: "app1",
                    LogLevel:      2,
                    Message:       "Test message 1",
                },
            },
            {
                opType:      "query",
                startTime:   900,
                endTime:     1100,
                appIDs:      []string{"app1"},
                minLogLevel: 1,
            },
        },
        expected: []expectedResult{
            {err: nil},
            {
                entries: []LogEntry{
                    {
                        Timestamp:     1000,
                        ApplicationID: "app1",
                        LogLevel:      2,
                        Message:       "Test message 1",
                    },
                },
                err: nil,
            },
        },
    },
    {
        description: "Multiple applications and log levels",
        operations: []operation{
            {
                opType: "ingest",
                entry: LogEntry{
                    Timestamp:     1000,
                    ApplicationID: "app1",
                    LogLevel:      2,
                    Message:       "Info message",
                },
            },
            {
                opType: "ingest",
                entry: LogEntry{
                    Timestamp:     1001,
                    ApplicationID: "app2",
                    LogLevel:      4,
                    Message:       "Error message",
                },
            },
            {
                opType:      "query",
                startTime:   900,
                endTime:     1100,
                appIDs:      []string{"app1", "app2"},
                minLogLevel: 3,
            },
        },
        expected: []expectedResult{
            {err: nil},
            {err: nil},
            {
                entries: []LogEntry{
                    {
                        Timestamp:     1001,
                        ApplicationID: "app2",
                        LogLevel:      4,
                        Message:       "Error message",
                    },
                },
                err: nil,
            },
        },
    },
    {
        description: "Empty result query",
        operations: []operation{
            {
                opType: "ingest",
                entry: LogEntry{
                    Timestamp:     1000,
                    ApplicationID: "app1",
                    LogLevel:      2,
                    Message:       "Test message",
                },
            },
            {
                opType:      "query",
                startTime:   2000,
                endTime:     3000,
                appIDs:      []string{"app1"},
                minLogLevel: 1,
            },
        },
        expected: []expectedResult{
            {err: nil},
            {
                entries: []LogEntry{},
                err:     nil,
            },
        },
    },
}

type operation struct {
    opType      string
    entry       LogEntry
    startTime   int64
    endTime     int64
    appIDs      []string
    minLogLevel int
}

type expectedResult struct {
    entries []LogEntry
    err     error
}