package order_aggregator

import (
	"container/heap"
)

type Order struct {
	Price    float64
	Quantity int
	NodeID   int
}

type BuyHeap []Order

func (h BuyHeap) Len() int { return len(h) }
func (h BuyHeap) Less(i, j int) bool {
	if h[i].Price == h[j].Price {
		return h[i].NodeID < h[j].NodeID
	}
	return h[i].Price > h[j].Price
}
func (h BuyHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *BuyHeap) Push(x interface{}) { *h = append(*h, x.(Order)) }
func (h *BuyHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

type SellHeap []Order

func (h SellHeap) Len() int { return len(h) }
func (h SellHeap) Less(i, j int) bool {
	if h[i].Price == h[j].Price {
		return h[i].NodeID < h[j].NodeID
	}
	return h[i].Price < h[j].Price
}
func (h SellHeap) Swap(i, j int)       { h[i], h[j] = h[j], h[i] }
func (h *SellHeap) Push(x interface{}) { *h = append(*h, x.(Order)) }
func (h *SellHeap) Pop() interface{} {
	old := *h
	n := len(old)
	x := old[n-1]
	*h = old[0 : n-1]
	return x
}

func AggregateOrderBook(orderBooks [][]Order, k int) ([]Order, []Order) {
	buyHeap := &BuyHeap{}
	sellHeap := &SellHeap{}
	heap.Init(buyHeap)
	heap.Init(sellHeap)

	for _, nodeOrders := range orderBooks {
		for _, order := range nodeOrders {
			heap.Push(buyHeap, order)
			heap.Push(sellHeap, order)
		}
	}

	var topBuyOrders []Order
	var topSellOrders []Order

	for i := 0; i < k && buyHeap.Len() > 0; i++ {
		topBuyOrders = append(topBuyOrders, heap.Pop(buyHeap).(Order))
	}

	for i := 0; i < k && sellHeap.Len() > 0; i++ {
		topSellOrders = append(topSellOrders, heap.Pop(sellHeap).(Order))
	}

	return topBuyOrders, topSellOrders
}