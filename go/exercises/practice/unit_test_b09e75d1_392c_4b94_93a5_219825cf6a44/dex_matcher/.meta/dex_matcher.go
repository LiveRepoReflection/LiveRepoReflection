package dex_matcher

import (
	"container/heap"
	"sync"
	"time"
)

type OrderType int

const (
	BUY OrderType = iota
	SELL
)

type Order struct {
	ID        string
	Type      OrderType
	Price     float64
	Quantity  float64
	Timestamp int64
}

type Trade struct {
	BuyerOrderID  string
	SellerOrderID string
	Price         float64
	Quantity      float64
	Timestamp     int64
}

type orderQueue []*Order

func (oq orderQueue) Len() int { return len(oq) }

func (oq orderQueue) Less(i, j int) bool {
	if oq[i].Price == oq[j].Price {
		return oq[i].Timestamp < oq[j].Timestamp
	}
	if oq[i].Type == BUY {
		return oq[i].Price > oq[j].Price
	}
	return oq[i].Price < oq[j].Price
}

func (oq orderQueue) Swap(i, j int) {
	oq[i], oq[j] = oq[j], oq[i]
}

func (oq *orderQueue) Push(x interface{}) {
	*oq = append(*oq, x.(*Order))
}

func (oq *orderQueue) Pop() interface{} {
	old := *oq
	n := len(old)
	item := old[n-1]
	*oq = old[0 : n-1]
	return item
}

type MatchingEngine struct {
	buyOrders  orderQueue
	sellOrders orderQueue
	mu         sync.Mutex
}

func NewMatchingEngine() *MatchingEngine {
	engine := &MatchingEngine{
		buyOrders:  make(orderQueue, 0),
		sellOrders: make(orderQueue, 0),
	}
	heap.Init(&engine.buyOrders)
	heap.Init(&engine.sellOrders)
	return engine
}

func (e *MatchingEngine) MatchOrder(order Order) []Trade {
	e.mu.Lock()
	defer e.mu.Unlock()

	var trades []Trade
	var oppositeQueue *orderQueue

	if order.Type == BUY {
		oppositeQueue = &e.sellOrders
	} else {
		oppositeQueue = &e.buyOrders
	}

	for order.Quantity > 0 && oppositeQueue.Len() > 0 {
		bestOpposite := (*oppositeQueue)[0]

		if (order.Type == BUY && order.Price < bestOpposite.Price) ||
			(order.Type == SELL && order.Price > bestOpposite.Price) {
			break
		}

		tradeQuantity := min(order.Quantity, bestOpposite.Quantity)
		tradePrice := bestOpposite.Price

		var trade Trade
		if order.Type == BUY {
			trade = Trade{
				BuyerOrderID:  order.ID,
				SellerOrderID: bestOpposite.ID,
				Price:         tradePrice,
				Quantity:      tradeQuantity,
				Timestamp:     time.Now().UnixNano(),
			}
		} else {
			trade = Trade{
				BuyerOrderID:  bestOpposite.ID,
				SellerOrderID: order.ID,
				Price:         tradePrice,
				Quantity:      tradeQuantity,
				Timestamp:     time.Now().UnixNano(),
			}
		}
		trades = append(trades, trade)

		order.Quantity -= tradeQuantity
		bestOpposite.Quantity -= tradeQuantity

		if bestOpposite.Quantity == 0 {
			heap.Pop(oppositeQueue)
		}
	}

	if order.Quantity > 0 {
		var targetQueue *orderQueue
		if order.Type == BUY {
			targetQueue = &e.buyOrders
		} else {
			targetQueue = &e.sellOrders
		}
		heap.Push(targetQueue, &order)
	}

	return trades
}

func min(a, b float64) float64 {
	if a < b {
		return a
	}
	return b
}