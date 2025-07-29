package stream_merger

import (
	"container/heap"
	"sync"
)

// Stream is an interface representing a sorted data stream.
type Stream interface {
	Next() (int, bool)
}

type streamState struct {
	stream Stream
	value  int
	valid  bool
}

type mergerHeap []*streamState

func (h mergerHeap) Len() int           { return len(h) }
func (h mergerHeap) Less(i, j int) bool { return h[i].value < h[j].value }
func (h mergerHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *mergerHeap) Push(x interface{}) {
	*h = append(*h, x.(*streamState))
}

func (h *mergerHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

type mergedStream struct {
	heap   *mergerHeap
	mu     sync.Mutex
	cond   *sync.Cond
	closed bool
}

func (m *mergedStream) Next() (int, bool) {
	m.mu.Lock()
	defer m.mu.Unlock()

	for m.heap.Len() == 0 && !m.closed {
		m.cond.Wait()
	}

	if m.closed && m.heap.Len() == 0 {
		return 0, false
	}

	state := heap.Pop(m.heap).(*streamState)
	val := state.value

	// Get next value from the stream
	if nextVal, ok := state.stream.Next(); ok {
		state.value = nextVal
		state.valid = true
		heap.Push(m.heap, state)
	} else {
		state.valid = false
	}

	m.cond.Broadcast()
	return val, true
}

func MergeKSortedStreams(streams []Stream) Stream {
	if len(streams) == 0 {
		return &emptyStream{}
	}

	h := make(mergerHeap, 0, len(streams))
	heap.Init(&h)

	ms := &mergedStream{
		heap: &h,
	}
	ms.cond = sync.NewCond(&ms.mu)

	// Initialize heap with first elements from each stream
	for _, stream := range streams {
		if val, ok := stream.Next(); ok {
			heap.Push(&h, &streamState{
				stream: stream,
				value:  val,
				valid:  true,
			})
		}
	}

	go func() {
		ms.mu.Lock()
		defer ms.mu.Unlock()
		if ms.heap.Len() == 0 {
			ms.closed = true
		}
		ms.cond.Broadcast()
	}()

	return ms
}

type emptyStream struct{}

func (e *emptyStream) Next() (int, bool) {
	return 0, false
}