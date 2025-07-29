package dex_matching

import (
	"container/heap"
)

type Order struct {
	OrderID   string
	UserID    string
	Side      string
	Price     int
	Quantity  int
	Timestamp int
}

type Trade struct {
	BuyOrderID  string
	SellOrderID string
	Price       int
	Quantity    int
}

type OrderBook struct {
	buyOrders  *OrderHeap
	sellOrders *OrderHeap
}

type OrderHeap struct {
	orders []Order
	isBuy  bool
}

func (h OrderHeap) Len() int { return len(h.orders) }
func (h OrderHeap) Less(i, j int) bool {
	if h.orders[i].Price == h.orders[j].Price {
		return h.orders[i].Timestamp < h.orders[j].Timestamp
	}
	if h.isBuy {
		return h.orders[i].Price > h.orders[j].Price
	}
	return h.orders[i].Price < h.orders[j].Price
}
func (h OrderHeap) Swap(i, j int) { h.orders[i], h.orders[j] = h.orders[j], h.orders[i] }

func (h *OrderHeap) Push(x interface{}) {
	h.orders = append(h.orders, x.(Order))
}

func (h *OrderHeap) Pop() interface{} {
	old := h.orders
	n := len(old)
	x := old[n-1]
	h.orders = old[0 : n-1]
	return x
}

func NewMatchingEngine() *OrderBook {
	return &OrderBook{
		buyOrders:  &OrderHeap{isBuy: true},
		sellOrders: &OrderHeap{isBuy: false},
	}
}

func (ob *OrderBook) ProcessOrder(order Order) []Trade {
	var trades []Trade
	heap.Init(ob.buyOrders)
	heap.Init(ob.sellOrders)

	if order.Side == "buy" {
		trades = ob.matchBuyOrder(order)
		if order.Quantity > 0 {
			heap.Push(ob.buyOrders, order)
		}
	} else {
		trades = ob.matchSellOrder(order)
		if order.Quantity > 0 {
			heap.Push(ob.sellOrders, order)
		}
	}

	return trades
}

func (ob *OrderBook) matchBuyOrder(buyOrder Order) []Trade {
	var trades []Trade

	for ob.sellOrders.Len() > 0 && buyOrder.Quantity > 0 {
		bestAsk := ob.sellOrders.orders[0]
		if bestAsk.Price > buyOrder.Price {
			break
		}

		tradeQuantity := min(bestAsk.Quantity, buyOrder.Quantity)
		trades = append(trades, Trade{
			BuyOrderID:  buyOrder.OrderID,
			SellOrderID: bestAsk.OrderID,
			Price:       bestAsk.Price,
			Quantity:    tradeQuantity,
		})

		buyOrder.Quantity -= tradeQuantity
		ob.sellOrders.orders[0].Quantity -= tradeQuantity

		if ob.sellOrders.orders[0].Quantity == 0 {
			heap.Pop(ob.sellOrders)
		}
	}

	return trades
}

func (ob *OrderBook) matchSellOrder(sellOrder Order) []Trade {
	var trades []Trade

	for ob.buyOrders.Len() > 0 && sellOrder.Quantity > 0 {
		bestBid := ob.buyOrders.orders[0]
		if bestBid.Price < sellOrder.Price {
			break
		}

		tradeQuantity := min(bestBid.Quantity, sellOrder.Quantity)
		trades = append(trades, Trade{
			BuyOrderID:  bestBid.OrderID,
			SellOrderID: sellOrder.OrderID,
			Price:       bestBid.Price,
			Quantity:    tradeQuantity,
		})

		sellOrder.Quantity -= tradeQuantity
		ob.buyOrders.orders[0].Quantity -= tradeQuantity

		if ob.buyOrders.orders[0].Quantity == 0 {
			heap.Pop(ob.buyOrders)
		}
	}

	return trades
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}