package distributed_median

import (
	"math/rand"
	"time"
)

type WorkerNode struct {
	buffer     []int
	bufferSize int
}

func NewWorkerNode(bufferSize int) *WorkerNode {
	rand.Seed(time.Now().UnixNano())
	return &WorkerNode{
		buffer:     make([]int, 0, bufferSize),
		bufferSize: bufferSize,
	}
}

func (w *WorkerNode) ReceiveNumber(num int) {
	if len(w.buffer) < w.bufferSize {
		w.buffer = append(w.buffer, num)
	} else {
		// Reservoir sampling implementation
		j := rand.Intn(len(w.buffer))
		w.buffer[j] = num
	}
}

func (w *WorkerNode) GetBuffer() []int {
	return w.buffer
}