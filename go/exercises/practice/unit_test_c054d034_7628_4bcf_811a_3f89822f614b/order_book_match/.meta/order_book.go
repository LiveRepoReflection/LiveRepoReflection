package order_book

import (
	"sort"
	"sync"
	"time"
)

type OrderType int

const (
	Buy OrderType = iota
	Sell
)

type Order struct {
	OrderID    string
	OrderType  OrderType
	Price      int
	Quantity   int
	Timestamp  int64
	SubmitterID string
}

type Trade struct {
	BuyOrderID  string
	SellOrderID string
	Price       int
	Quantity    int
	Timestamp   int64
}

type OrderBook struct {
	mu          sync.RWMutex
	buyOrders   []Order
	sellOrders  []Order
}

func NewOrderBook() *OrderBook {
	return &OrderBook{
		buyOrders:  make([]Order, 0),
		sellOrders: make([]Order, 0),
	}
}

func (ob *OrderBook) SubmitOrder(order Order) {
	ob.mu.Lock()
	defer ob.mu.Unlock()

	switch order.OrderType {
	case Buy:
		ob.buyOrders = append(ob.buyOrders, order)
		sort.Slice(ob.buyOrders, func(i, j int) bool {
			if ob.buyOrders[i].Price == ob.buyOrders[j].Price {
				return ob.buyOrders[i].Timestamp < ob.buyOrders[j].Timestamp
			}
			return ob.buyOrders[i].Price > ob.buyOrders[j].Price
		})
	case Sell:
		ob.sellOrders = append(ob.sellOrders, order)
		sort.Slice(ob.sellOrders, func(i, j int) bool {
			if ob.sellOrders[i].Price == ob.sellOrders[j].Price {
				return ob.sellOrders[i].Timestamp < ob.sellOrders[j].Timestamp
			}
			return ob.sellOrders[i].Price < ob.sellOrders[j].Price
		})
	}
}

func (ob *OrderBook) MatchOrders() []Trade {
	ob.mu.Lock()
	defer ob.mu.Unlock()

	var trades []Trade

	for len(ob.buyOrders) > 0 && len(ob.sellOrders) > 0 {
		buyOrder := &ob.buyOrders[0]
		sellOrder := &ob.sellOrders[0]

		if buyOrder.Price < sellOrder.Price {
			break
		}

		tradeQuantity := min(buyOrder.Quantity, sellOrder.Quantity)
		tradePrice := sellOrder.Price // Price is the sell order's price (market price)

		trades = append(trades, Trade{
			BuyOrderID:  buyOrder.OrderID,
			SellOrderID: sellOrder.OrderID,
			Price:       tradePrice,
			Quantity:    tradeQuantity,
			Timestamp:   time.Now().UnixNano(),
		})

		buyOrder.Quantity -= tradeQuantity
		sellOrder.Quantity -= tradeQuantity

		if buyOrder.Quantity == 0 {
			ob.buyOrders = ob.buyOrders[1:]
		}
		if sellOrder.Quantity == 0 {
			ob.sellOrders = ob.sellOrders[1:]
		}
	}

	return trades
}

func (ob *OrderBook) CancelOrder(orderID string) bool {
	ob.mu.Lock()
	defer ob.mu.Unlock()

	for i, order := range ob.buyOrders {
		if order.OrderID == orderID {
			ob.buyOrders = append(ob.buyOrders[:i], ob.buyOrders[i+1:]...)
			return true
		}
	}

	for i, order := range ob.sellOrders {
		if order.OrderID == orderID {
			ob.sellOrders = append(ob.sellOrders[:i], ob.sellOrders[i+1:]...)
			return true
		}
	}

	return false
}

func (ob *OrderBook) GetBuyOrders() []Order {
	ob.mu.RLock()
	defer ob.mu.RUnlock()

	orders := make([]Order, len(ob.buyOrders))
	copy(orders, ob.buyOrders)
	return orders
}

func (ob *OrderBook) GetSellOrders() []Order {
	ob.mu.RLock()
	defer ob.mu.RUnlock()

	orders := make([]Order, len(ob.sellOrders))
	copy(orders, ob.sellOrders)
	return orders
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}