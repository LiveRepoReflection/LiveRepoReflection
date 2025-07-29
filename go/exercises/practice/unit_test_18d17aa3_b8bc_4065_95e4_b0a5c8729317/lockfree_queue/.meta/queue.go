package lockfree_queue

import (
	"errors"
	"sync/atomic"
	"unsafe"
)

var (
	ErrQueueFull  = errors.New("queue is full")
	ErrQueueEmpty = errors.New("queue is empty")
)

type node[T any] struct {
	value T
	next  unsafe.Pointer
}

type Queue[T any] struct {
	head       unsafe.Pointer
	tail       unsafe.Pointer
	_          [64]byte // padding to prevent false sharing
	capacity   int
	count      atomic.Int32
}

func NewQueue[T any](capacity int) *Queue[T] {
	if capacity <= 0 {
		return nil
	}

	dummy := &node[T]{}
	return &Queue[T]{
		head:     unsafe.Pointer(dummy),
		tail:     unsafe.Pointer(dummy),
		capacity: capacity,
	}
}

func (q *Queue[T]) Enqueue(item T) error {
	if q.count.Load() >= int32(q.capacity) {
		return ErrQueueFull
	}

	newNode := &node[T]{value: item}

	for {
		tail := atomic.LoadPointer(&q.tail)
		tailNode := (*node[T])(tail)
		next := atomic.LoadPointer(&tailNode.next)

		if next == nil {
			if atomic.CompareAndSwapPointer(&tailNode.next, nil, unsafe.Pointer(newNode)) {
				atomic.CompareAndSwapPointer(&q.tail, tail, unsafe.Pointer(newNode))
				q.count.Add(1)
				return nil
			}
		} else {
			atomic.CompareAndSwapPointer(&q.tail, tail, next)
		}
	}
}

func (q *Queue[T]) Dequeue() (T, error) {
	var zero T
	if q.count.Load() <= 0 {
		return zero, ErrQueueEmpty
	}

	for {
		head := atomic.LoadPointer(&q.head)
		headNode := (*node[T])(head)
		tail := atomic.LoadPointer(&q.tail)
		next := atomic.LoadPointer(&headNode.next)

		if next == nil {
			return zero, ErrQueueEmpty
		}

		if head == tail {
			atomic.CompareAndSwapPointer(&q.tail, tail, next)
		} else {
			nextNode := (*node[T])(next)
			if atomic.CompareAndSwapPointer(&q.head, head, next) {
				q.count.Add(-1)
				return nextNode.value, nil
			}
		}
	}
}

func (q *Queue[T]) Len() int {
	return int(q.count.Load())
}

func (q *Queue[T]) Cap() int {
	return q.capacity
}