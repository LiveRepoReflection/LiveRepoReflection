package logpriority

import (
	"container/heap"
	"sort"
	"sync"
)

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

// severityRank maps severity strings to numeric ranks for comparison
var severityRank = map[string]int{
	"DEBUG":    1,
	"INFO":     2,
	"WARNING":  3,
	"ERROR":    4,
	"CRITICAL": 5,
}

// logAggregatorImpl implements the LogAggregator interface
type logAggregatorImpl struct {
	events      []LogEvent           // Stores all log events
	originCount map[string]int       // Counts events per origin
	mutex       sync.RWMutex         // Protects concurrent access to data
	sortedCache []LogEvent           // Cache for sorted events
	cacheValid  bool                 // Flag indicating if cache is valid
}

// NewLogAggregator creates a new LogAggregator
func NewLogAggregator() LogAggregator {
	return &logAggregatorImpl{
		events:      make([]LogEvent, 0),
		originCount: make(map[string]int),
		cacheValid:  false,
	}
}

// Ingest adds a new log event to the aggregator
func (la *logAggregatorImpl) Ingest(event LogEvent) {
	la.mutex.Lock()
	defer la.mutex.Unlock()

	// Add the event to our collection
	la.events = append(la.events, event)

	// Update the count for this origin
	la.originCount[event.Origin]++

	// Invalidate the cache since we've added a new event
	la.cacheValid = false
}

// GetTopN returns the n most important log events
func (la *logAggregatorImpl) GetTopN(n int) []LogEvent {
	if n <= 0 {
		return []LogEvent{}
	}

	la.mutex.RLock() // Get a read lock first to check cache
	if la.cacheValid && la.sortedCache != nil {
		result := la.sortedCache
		if n < len(result) {
			result = result[:n]
		}
		la.mutex.RUnlock()
		return result
	}
	la.mutex.RUnlock() // Release read lock before acquiring write lock

	// Cache is invalid, need to rebuild it
	la.mutex.Lock()
	defer la.mutex.Unlock()

	// Double-check if cache became valid while waiting for write lock
	if la.cacheValid && la.sortedCache != nil {
		result := la.sortedCache
		if n < len(result) {
			result = result[:n]
		}
		return result
	}

	// No events to return
	if len(la.events) == 0 {
		la.sortedCache = []LogEvent{}
		la.cacheValid = true
		return []LogEvent{}
	}

	// Sort all events by our importance criteria
	// Create a copy to avoid modifying the original slice
	sortedEvents := make([]LogEvent, len(la.events))
	copy(sortedEvents, la.events)

	// Use a stable sort to maintain order for equivalent events
	sort.SliceStable(sortedEvents, func(i, j int) bool {
		// 1. Sort by severity (higher severity first)
		sevRankI := severityRank[sortedEvents[i].Severity]
		sevRankJ := severityRank[sortedEvents[j].Severity]
		if sevRankI != sevRankJ {
			return sevRankI > sevRankJ
		}

		// 2. Sort by timestamp (more recent first)
		if sortedEvents[i].Timestamp != sortedEvents[j].Timestamp {
			return sortedEvents[i].Timestamp > sortedEvents[j].Timestamp
		}

		// 3. Sort by origin count (higher count first)
		countI := la.originCount[sortedEvents[i].Origin]
		countJ := la.originCount[sortedEvents[j].Origin]
		if countI != countJ {
			return countI > countJ
		}

		// 4. If everything is the same, sort by origin string lexicographically
		return sortedEvents[i].Origin < sortedEvents[j].Origin
	})

	// Update cache
	la.sortedCache = sortedEvents
	la.cacheValid = true

	// Return the top n events
	if n < len(sortedEvents) {
		return sortedEvents[:n]
	}
	return sortedEvents
}

// Below is an alternative implementation using a heap for potentially better performance
// with very large datasets. The main implementation above uses a simple sort approach which
// is more readable and likely sufficient for most use cases.

// LogEventWithContext adds context to a LogEvent for the priority queue
type LogEventWithContext struct {
	Event      LogEvent
	OriginRank int // Higher is more important
}

// priorityQueue implements heap.Interface for LogEventWithContext
type priorityQueue []*LogEventWithContext

func (pq priorityQueue) Len() int { return len(pq) }

func (pq priorityQueue) Less(i, j int) bool {
	// Severity comparison (higher first)
	sevRankI := severityRank[pq[i].Event.Severity]
	sevRankJ := severityRank[pq[j].Event.Severity]
	if sevRankI != sevRankJ {
		return sevRankI > sevRankJ
	}

	// Timestamp comparison (more recent first)
	if pq[i].Event.Timestamp != pq[j].Event.Timestamp {
		return pq[i].Event.Timestamp > pq[j].Event.Timestamp
	}

	// Origin rank comparison (higher first)
	if pq[i].OriginRank != pq[j].OriginRank {
		return pq[i].OriginRank > pq[j].OriginRank
	}

	// Lexicographical comparison as final tiebreaker
	return pq[i].Event.Origin < pq[j].Event.Origin
}

func (pq priorityQueue) Swap(i, j int) {
	pq[i], pq[j] = pq[j], pq[i]
}

func (pq *priorityQueue) Push(x interface{}) {
	item := x.(*LogEventWithContext)
	*pq = append(*pq, item)
}

func (pq *priorityQueue) Pop() interface{} {
	old := *pq
	n := len(old)
	item := old[n-1]
	*pq = old[0 : n-1]
	return item
}

// heapBasedLogAggregator is an alternative implementation using a heap
type heapBasedLogAggregator struct {
	events      []LogEvent
	originCount map[string]int
	mutex       sync.RWMutex
	pq          *priorityQueue
	cacheValid  bool
}

func NewHeapBasedLogAggregator() LogAggregator {
	return &heapBasedLogAggregator{
		events:      make([]LogEvent, 0),
		originCount: make(map[string]int),
		cacheValid:  false,
	}
}

func (la *heapBasedLogAggregator) Ingest(event LogEvent) {
	la.mutex.Lock()
	defer la.mutex.Unlock()

	la.events = append(la.events, event)
	la.originCount[event.Origin]++
	la.cacheValid = false
}

func (la *heapBasedLogAggregator) GetTopN(n int) []LogEvent {
	if n <= 0 {
		return []LogEvent{}
	}

	la.mutex.Lock()
	defer la.mutex.Unlock()

	// Rebuild the priority queue if cache is invalid
	if !la.cacheValid || la.pq == nil {
		pq := make(priorityQueue, 0, len(la.events))
		for _, event := range la.events {
			pq = append(pq, &LogEventWithContext{
				Event:      event,
				OriginRank: la.originCount[event.Origin],
			})
		}
		heap.Init(&pq)
		la.pq = &pq
		la.cacheValid = true
	}

	// Extract the top n events from the heap
	result := make([]LogEvent, 0, n)
	tempPQ := make(priorityQueue, len(*la.pq))
	copy(tempPQ, *la.pq)

	for i := 0; i < n && len(tempPQ) > 0; i++ {
		item := heap.Pop(&tempPQ).(*LogEventWithContext)
		result = append(result, item.Event)
	}

	return result
}