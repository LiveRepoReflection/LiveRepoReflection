package orderbook_aggregator

import (
	"container/heap"
	"sync"
)

type Order struct {
	Price    int64
	Quantity int64
	IsBid    bool
}

type OrderBookAggregator struct {
	bids      *OrderHeap
	asks      *OrderHeap
	orderMap  map[int64]*Order
	orderLock sync.RWMutex
}

func NewOrderBookAggregator(nodes []<-chan []Order) *OrderBookAggregator {
	agg := &OrderBookAggregator{
		bids:     &OrderHeap{isMaxHeap: true},
		asks:     &OrderHeap{isMaxHeap: false},
		orderMap: make(map[int64]*Order),
	}

	for _, node := range nodes {
		go agg.processNode(node)
	}

	return agg
}

func (agg *OrderBookAggregator) processNode(node <-chan []Order) {
	for orders := range node {
		agg.updateOrderBook(orders)
	}
}

func (agg *OrderBookAggregator) updateOrderBook(orders []Order) {
	agg.orderLock.Lock()
	defer agg.orderLock.Unlock()

	for _, order := range orders {
		if existing, exists := agg.orderMap[order.Price]; exists {
			existing.Quantity += order.Quantity
			if existing.Quantity <= 0 {
				delete(agg.orderMap, order.Price)
				if existing.IsBid {
					agg.bids.Remove(existing)
				} else {
					agg.asks.Remove(existing)
				}
			} else {
				if existing.IsBid {
					agg.bids.Fix(existing)
				} else {
					agg.asks.Fix(existing)
				}
			}
		} else if order.Quantity > 0 {
			newOrder := &Order{
				Price:    order.Price,
				Quantity: order.Quantity,
				IsBid:    order.IsBid,
			}
			agg.orderMap[order.Price] = newOrder
			if order.IsBid {
				heap.Push(agg.bids, newOrder)
			} else {
				heap.Push(agg.asks, newOrder)
			}
		}
	}
}

func (agg *OrderBookAggregator) GetTopOrders(n int) ([]Order, []Order) {
	agg.orderLock.RLock()
	defer agg.orderLock.RUnlock()

	bids := make([]Order, 0, n)
	asks := make([]Order, 0, n)

	bidsCopy := agg.bids.Copy()
	asksCopy := agg.asks.Copy()

	for i := 0; i < n && bidsCopy.Len() > 0; i++ {
		order := heap.Pop(bidsCopy).(*Order)
		bids = append(bids, *order)
	}

	for i := 0; i < n && asksCopy.Len() > 0; i++ {
		order := heap.Pop(asksCopy).(*Order)
		asks = append(asks, *order)
	}

	return bids, asks
}

type OrderHeap struct {
	orders    []*Order
	isMaxHeap bool
}

func (h OrderHeap) Len() int { return len(h.orders) }
func (h OrderHeap) Less(i, j int) bool {
	if h.isMaxHeap {
		return h.orders[i].Price > h.orders[j].Price
	}
	return h.orders[i].Price < h.orders[j].Price
}
func (h OrderHeap) Swap(i, j int) { h.orders[i], h.orders[j] = h.orders[j], h.orders[i] }

func (h *OrderHeap) Push(x interface{}) {
	h.orders = append(h.orders, x.(*Order))
}

func (h *OrderHeap) Pop() interface{} {
	old := h.orders
	n := len(old)
	x := old[n-1]
	h.orders = old[0 : n-1]
	return x
}

func (h *OrderHeap) Remove(order *Order) {
	for i, o := range h.orders {
		if o == order {
			heap.Remove(h, i)
			return
		}
	}
}

func (h *OrderHeap) Fix(order *Order) {
	for i, o := range h.orders {
		if o == order {
			heap.Fix(h, i)
			return
		}
	}
}

func (h *OrderHeap) Copy() *OrderHeap {
	copyHeap := &OrderHeap{
		orders:    make([]*Order, len(h.orders)),
		isMaxHeap: h.isMaxHeap,
	}
	copy(copyHeap.orders, h.orders)
	heap.Init(copyHeap)
	return copyHeap
}