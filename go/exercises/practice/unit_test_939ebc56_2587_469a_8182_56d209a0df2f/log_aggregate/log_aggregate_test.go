package log_aggregate

import (
    "reflect"
    "testing"
)

func TestLogSystem(t *testing.T) {
    for _, tc := range testCases {
        t.Run(tc.description, func(t *testing.T) {
            system := NewLogSystem()

            for i, op := range tc.operations {
                var err error
                var entries []LogEntry

                switch op.opType {
                case "ingest":
                    err = system.IngestLog(op.entry)
                case "query":
                    entries, err = system.QueryLogs(op.startTime, op.endTime, op.appIDs, op.minLogLevel)
                }

                expected := tc.expected[i]

                if err != expected.err {
                    t.Errorf("Operation %d: expected error %v, got %v", i, expected.err, err)
                }

                if entries != nil {
                    if !reflect.DeepEqual(entries, expected.entries) {
                        t.Errorf("Operation %d: expected entries %v, got %v", i, expected.entries, entries)
                    }
                }
            }
        })
    }
}

func BenchmarkIngestLog(b *testing.B) {
    system := NewLogSystem()
    entry := LogEntry{
        Timestamp:     1000,
        ApplicationID: "app1",
        LogLevel:      2,
        Message:       "Benchmark message",
    }

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        system.IngestLog(entry)
    }
}

func BenchmarkQueryLogs(b *testing.B) {
    system := NewLogSystem()
    // Setup some test data
    entries := []LogEntry{
        {Timestamp: 1000, ApplicationID: "app1", LogLevel: 2, Message: "Message 1"},
        {Timestamp: 1001, ApplicationID: "app2", LogLevel: 3, Message: "Message 2"},
        {Timestamp: 1002, ApplicationID: "app1", LogLevel: 4, Message: "Message 3"},
    }
    for _, entry := range entries {
        system.IngestLog(entry)
    }

    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        system.QueryLogs(900, 1100, []string{"app1"}, 2)
    }
}