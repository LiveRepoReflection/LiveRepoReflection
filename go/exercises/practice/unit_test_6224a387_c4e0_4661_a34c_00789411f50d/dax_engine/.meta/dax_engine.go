package dax_engine

import (
	"sync"
	"time"
)

type Order struct {
	OrderID   string
	TokenPair string
	OrderType string
	Price     uint64
	Quantity  uint64
	Timestamp int64
}

type TradeRecord struct {
	BuyOrderID  string
	SellOrderID string
	Price       uint64
	Quantity    uint64
	Timestamp   int64
}

type OrderBook struct {
	BuyOrders  []Order
	SellOrders []Order
}

type DAXEngine struct {
	orderBooks map[string]*OrderBook
	mu         sync.RWMutex
}

func NewDAXEngine() *DAXEngine {
	return &DAXEngine{
		orderBooks: make(map[string]*OrderBook),
	}
}

func (e *DAXEngine) PlaceOrder(order Order) []TradeRecord {
	e.mu.Lock()
	defer e.mu.Unlock()

	if _, exists := e.orderBooks[order.TokenPair]; !exists {
		e.orderBooks[order.TokenPair] = &OrderBook{
			BuyOrders:  make([]Order, 0),
			SellOrders: make([]Order, 0),
		}
	}

	orderBook := e.orderBooks[order.TokenPair]
	var trades []TradeRecord

	if order.OrderType == "BUY" {
		trades = e.matchBuyOrder(order, orderBook)
	} else if order.OrderType == "SELL" {
		trades = e.matchSellOrder(order, orderBook)
	}

	return trades
}

func (e *DAXEngine) matchBuyOrder(buyOrder Order, orderBook *OrderBook) []TradeRecord {
	var trades []TradeRecord
	remainingQuantity := buyOrder.Quantity

	for i := 0; i < len(orderBook.SellOrders) && remainingQuantity > 0; {
		sellOrder := &orderBook.SellOrders[i]

		if sellOrder.Price > buyOrder.Price {
			break
		}

		tradeQuantity := min(remainingQuantity, sellOrder.Quantity)
		trade := TradeRecord{
			BuyOrderID:  buyOrder.OrderID,
			SellOrderID: sellOrder.OrderID,
			Price:       sellOrder.Price,
			Quantity:    tradeQuantity,
			Timestamp:   time.Now().Unix(),
		}
		trades = append(trades, trade)

		if sellOrder.Quantity > tradeQuantity {
			sellOrder.Quantity -= tradeQuantity
			remainingQuantity = 0
		} else {
			remainingQuantity -= sellOrder.Quantity
			orderBook.SellOrders = append(orderBook.SellOrders[:i], orderBook.SellOrders[i+1:]...)
		}
	}

	if remainingQuantity > 0 {
		buyOrder.Quantity = remainingQuantity
		e.insertBuyOrder(buyOrder, orderBook)
	}

	return trades
}

func (e *DAXEngine) matchSellOrder(sellOrder Order, orderBook *OrderBook) []TradeRecord {
	var trades []TradeRecord
	remainingQuantity := sellOrder.Quantity

	for i := 0; i < len(orderBook.BuyOrders) && remainingQuantity > 0; {
		buyOrder := &orderBook.BuyOrders[i]

		if buyOrder.Price < sellOrder.Price {
			break
		}

		tradeQuantity := min(remainingQuantity, buyOrder.Quantity)
		trade := TradeRecord{
			BuyOrderID:  buyOrder.OrderID,
			SellOrderID: sellOrder.OrderID,
			Price:       buyOrder.Price,
			Quantity:    tradeQuantity,
			Timestamp:   time.Now().Unix(),
		}
		trades = append(trades, trade)

		if buyOrder.Quantity > tradeQuantity {
			buyOrder.Quantity -= tradeQuantity
			remainingQuantity = 0
		} else {
			remainingQuantity -= buyOrder.Quantity
			orderBook.BuyOrders = append(orderBook.BuyOrders[:i], orderBook.BuyOrders[i+1:]...)
		}
	}

	if remainingQuantity > 0 {
		sellOrder.Quantity = remainingQuantity
		e.insertSellOrder(sellOrder, orderBook)
	}

	return trades
}

func (e *DAXEngine) insertBuyOrder(order Order, orderBook *OrderBook) {
	i := 0
	for ; i < len(orderBook.BuyOrders); i++ {
		if orderBook.BuyOrders[i].Price < order.Price ||
			(orderBook.BuyOrders[i].Price == order.Price && orderBook.BuyOrders[i].Timestamp > order.Timestamp) {
			break
		}
	}
	orderBook.BuyOrders = append(orderBook.BuyOrders[:i], append([]Order{order}, orderBook.BuyOrders[i:]...)...)
}

func (e *DAXEngine) insertSellOrder(order Order, orderBook *OrderBook) {
	i := 0
	for ; i < len(orderBook.SellOrders); i++ {
		if orderBook.SellOrders[i].Price > order.Price ||
			(orderBook.SellOrders[i].Price == order.Price && orderBook.SellOrders[i].Timestamp > order.Timestamp) {
			break
		}
	}
	orderBook.SellOrders = append(orderBook.SellOrders[:i], append([]Order{order}, orderBook.SellOrders[i:]...)...)
}

func (e *DAXEngine) CancelOrder(orderID string, tokenPair string) bool {
	e.mu.Lock()
	defer e.mu.Unlock()

	orderBook, exists := e.orderBooks[tokenPair]
	if !exists {
		return false
	}

	for i, order := range orderBook.BuyOrders {
		if order.OrderID == orderID {
			orderBook.BuyOrders = append(orderBook.BuyOrders[:i], orderBook.BuyOrders[i+1:]...)
			return true
		}
	}

	for i, order := range orderBook.SellOrders {
		if order.OrderID == orderID {
			orderBook.SellOrders = append(orderBook.SellOrders[:i], orderBook.SellOrders[i+1:]...)
			return true
		}
	}

	return false
}

func (e *DAXEngine) GetOrderBook(tokenPair string) OrderBook {
	e.mu.RLock()
	defer e.mu.RUnlock()

	orderBook, exists := e.orderBooks[tokenPair]
	if !exists {
		return OrderBook{
			BuyOrders:  make([]Order, 0),
			SellOrders: make([]Order, 0),
		}
	}

	var buyOrders []Order
	if len(orderBook.BuyOrders) > 10 {
		buyOrders = orderBook.BuyOrders[:10]
	} else {
		buyOrders = make([]Order, len(orderBook.BuyOrders))
		copy(buyOrders, orderBook.BuyOrders)
	}

	var sellOrders []Order
	if len(orderBook.SellOrders) > 10 {
		sellOrders = orderBook.SellOrders[:10]
	} else {
		sellOrders = make([]Order, len(orderBook.SellOrders))
		copy(sellOrders, orderBook.SellOrders)
	}

	return OrderBook{
		BuyOrders:  buyOrders,
		SellOrders: sellOrders,
	}
}

func min(a, b uint64) uint64 {
	if a < b {
		return a
	}
	return b
}