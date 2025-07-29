package dynamic_rmq

import (
	"errors"
	"math"
	"sync"
)

type DynamicRMQ interface {
	Query(l, r int) (int, error)
	Update(index, value int) error
}

type dynamicRMQ struct {
	n    int
	size int
	tree []int
	lock sync.RWMutex
}

// NewDynamicRMQ builds a new dynamicRMQ instance using the provided array.
func NewDynamicRMQ(arr []int) (DynamicRMQ, error) {
	if len(arr) == 0 {
		return nil, errors.New("array cannot be empty")
	}
	n := len(arr)
	// Find next power of two
	size := 1
	for size < n {
		size *= 2
	}
	tree := make([]int, 2*size)
	// Initialize leaves
	for i := 0; i < size; i++ {
		if i < n {
			tree[size+i] = arr[i]
		} else {
			tree[size+i] = math.MaxInt32
		}
	}
	// Build internal nodes.
	for i := size - 1; i > 0; i-- {
		tree[i] = min(tree[2*i], tree[2*i+1])
	}
	return &dynamicRMQ{
		n:    n,
		size: size,
		tree: tree,
	}, nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}

// Query returns the minimum value in the subarray arr[l...r] inclusively.
func (d *dynamicRMQ) Query(l, r int) (int, error) {
	if l < 0 || r < 0 || l >= d.n || r >= d.n || l > r {
		return math.MaxInt32, errors.New("invalid query indices")
	}
	d.lock.RLock()
	defer d.lock.RUnlock()
	l += d.size
	r += d.size
	res := math.MaxInt32
	for l <= r {
		if l%2 == 1 {
			res = min(res, d.tree[l])
			l++
		}
		if r%2 == 0 {
			res = min(res, d.tree[r])
			r--
		}
		l /= 2
		r /= 2
	}
	return res, nil
}

// Update sets arr[index] to the provided value and updates the RMQ structure.
func (d *dynamicRMQ) Update(index, value int) error {
	if index < 0 || index >= d.n {
		return errors.New("invalid update index")
	}
	d.lock.Lock()
	defer d.lock.Unlock()
	pos := index + d.size
	d.tree[pos] = value
	pos /= 2
	for pos >= 1 {
		d.tree[pos] = min(d.tree[2*pos], d.tree[2*pos+1])
		pos /= 2
	}
	return nil
}