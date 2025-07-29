package skyline_reconstruction

import (
	"container/heap"
	"sort"
)

type event struct {
	x       int
	height  int
	isStart bool
}

type maxHeap []int

func (h maxHeap) Len() int           { return len(h) }
func (h maxHeap) Less(i, j int) bool { return h[i] > h[j] }
func (h maxHeap) Swap(i, j int)      { h[i], h[j] = h[j], h[i] }

func (h *maxHeap) Push(x interface{}) {
	*h = append(*h, x.(int))
}

func (h *maxHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

func GetSkyline(buildings [][]int) [][]int {
	if len(buildings) == 0 {
		return [][]int{}
	}

	events := make([]event, 0, 2*len(buildings))
	for _, b := range buildings {
		events = append(events, event{x: b[0], height: b[2], isStart: true})
		events = append(events, event{x: b[1], height: b[2], isStart: false})
	}

	sort.Slice(events, func(i, j int) bool {
		if events[i].x != events[j].x {
			return events[i].x < events[j].x
		}
		if events[i].isStart && events[j].isStart {
			return events[i].height > events[j].height
		}
		if !events[i].isStart && !events[j].isStart {
			return events[i].height < events[j].height
		}
		return events[i].isStart
	})

	h := &maxHeap{}
	heap.Init(h)
	heap.Push(h, 0)

	prevMax := 0
	result := [][]int{}

	for _, e := range events {
		if e.isStart {
			heap.Push(h, e.height)
		} else {
			for i := 0; i < len(*h); i++ {
				if (*h)[i] == e.height {
					heap.Remove(h, i)
					break
				}
			}
		}

		currentMax := (*h)[0]
		if currentMax != prevMax {
			result = append(result, []int{e.x, currentMax})
			prevMax = currentMax
		}
	}

	return result
}