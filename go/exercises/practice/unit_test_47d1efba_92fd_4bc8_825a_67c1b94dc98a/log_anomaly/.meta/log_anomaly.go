package log_anomaly

import (
	"errors"
	"sync"
	"time"
)

type LogLevel string

const (
	DEBUG LogLevel = "DEBUG"
	INFO  LogLevel = "INFO"
	WARN  LogLevel = "WARN"
	ERROR LogLevel = "ERROR"
)

type LogEntry struct {
	Timestamp   int64
	ServiceName string
	LogLevel    LogLevel
	Message     string
}

type StorageNode struct {
	mu    sync.RWMutex
	logs  []LogEntry
	index map[string][]int // serviceName to log indices
}

type DistributedStorage struct {
	nodes    []*StorageNode
	nodeLock sync.RWMutex
}

type LogIngestor struct {
	storage *DistributedStorage
}

type AnomalyDetector struct {
	windowSize int
	threshold  int
	history   map[string][]LogLevel
	mu        sync.Mutex
}

func NewDistributedStorage() *DistributedStorage {
	nodes := make([]*StorageNode, 3) // 3 nodes for example
	for i := range nodes {
		nodes[i] = &StorageNode{
			logs:  make([]LogEntry, 0),
			index: make(map[string][]int),
		}
	}
	return &DistributedStorage{nodes: nodes}
}

func (ds *DistributedStorage) Store(entry LogEntry) error {
	if entry.Timestamp <= 0 {
		return errors.New("invalid timestamp")
	}

	nodeIndex := len(entry.ServiceName) % len(ds.nodes)
	ds.nodeLock.RLock()
	node := ds.nodes[nodeIndex]
	ds.nodeLock.RUnlock()

	node.mu.Lock()
	defer node.mu.Unlock()

	node.logs = append(node.logs, entry)
	node.index[entry.ServiceName] = append(node.index[entry.ServiceName], len(node.logs)-1)

	return nil
}

func (ds *DistributedStorage) Retrieve(serviceName string, start, end time.Time) ([]LogEntry, error) {
	if start.After(end) {
		return nil, errors.New("invalid time range")
	}

	results := make([]LogEntry, 0)
	ds.nodeLock.RLock()
	defer ds.nodeLock.RUnlock()

	for _, node := range ds.nodes {
		node.mu.RLock()
		if indices, ok := node.index[serviceName]; ok {
			for _, idx := range indices {
				log := node.logs[idx]
				logTime := time.Unix(0, log.Timestamp)
				if logTime.After(start) && logTime.Before(end) {
					results = append(results, log)
				}
			}
		}
		node.mu.RUnlock()
	}

	return results, nil
}

func NewLogIngestor(storage *DistributedStorage) *LogIngestor {
	return &LogIngestor{storage: storage}
}

func (li *LogIngestor) Ingest(entry LogEntry) error {
	return li.storage.Store(entry)
}

func NewAnomalyDetector(windowSize, threshold int) *AnomalyDetector {
	return &AnomalyDetector{
		windowSize: windowSize,
		threshold:  threshold,
		history:    make(map[string][]LogLevel),
	}
}

func (ad *AnomalyDetector) AddLog(entry LogEntry) {
	ad.mu.Lock()
	defer ad.mu.Unlock()

	history := ad.history[entry.ServiceName]
	history = append(history, entry.LogLevel)
	if len(history) > ad.windowSize {
		history = history[1:]
	}
	ad.history[entry.ServiceName] = history
}

func (ad *AnomalyDetector) CheckAnomaly(serviceName string) bool {
	ad.mu.Lock()
	defer ad.mu.Unlock()

	history, exists := ad.history[serviceName]
	if !exists {
		return false
	}

	errorCount := 0
	for _, level := range history {
		if level == ERROR {
			errorCount++
		}
	}

	return errorCount >= ad.threshold
}

func (ad *AnomalyDetector) Reset() {
	ad.mu.Lock()
	defer ad.mu.Unlock()

	ad.history = make(map[string][]LogLevel)
}