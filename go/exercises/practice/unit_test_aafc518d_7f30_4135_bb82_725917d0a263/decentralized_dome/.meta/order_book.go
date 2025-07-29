package decentralized_dome

import (
	"errors"
	"sort"
	"sync"
	"time"
)

type OrderType string

const (
	Buy  OrderType = "Buy"
	Sell OrderType = "Sell"
)

type Order struct {
	OrderID   string
	Symbol    string
	OrderType OrderType
	Price     float64
	Quantity  int
	Timestamp int64
	NodeID    string
}

type TradeExecution struct {
	BuyOrderID  string
	SellOrderID string
	Price       float64
	Quantity    int
	Timestamp   int64
}

type OrderBook struct {
	buyOrders  []Order
	sellOrders []Order
	mutex      sync.RWMutex
	tradeChan  chan []TradeExecution
}

func NewOrderBook() *OrderBook {
	return &OrderBook{
		tradeChan: make(chan []TradeExecution, 1000),
	}
}

func (ob *OrderBook) AddOrder(order Order) error {
	ob.mutex.Lock()
	defer ob.mutex.Unlock()

	if err := validateOrder(order); err != nil {
		return err
	}

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

	return nil
}

func (ob *OrderBook) RemoveOrder(orderID string) error {
	ob.mutex.Lock()
	defer ob.mutex.Unlock()

	for i, order := range ob.buyOrders {
		if order.OrderID == orderID {
			ob.buyOrders = append(ob.buyOrders[:i], ob.buyOrders[i+1:]...)
			return nil
		}
	}

	for i, order := range ob.sellOrders {
		if order.OrderID == orderID {
			ob.sellOrders = append(ob.sellOrders[:i], ob.sellOrders[i+1:]...)
			return nil
		}
	}

	return errors.New("order not found")
}

func (ob *OrderBook) GetBestBid() float64 {
	ob.mutex.RLock()
	defer ob.mutex.RUnlock()

	if len(ob.buyOrders) == 0 {
		return 0
	}
	return ob.buyOrders[0].Price
}

func (ob *OrderBook) GetBestAsk() float64 {
	ob.mutex.RLock()
	defer ob.mutex.RUnlock()

	if len(ob.sellOrders) == 0 {
		return 0
	}
	return ob.sellOrders[0].Price
}

func (ob *OrderBook) GetOrders(orderType string) []Order {
	ob.mutex.RLock()
	defer ob.mutex.RUnlock()

	switch OrderType(orderType) {
	case Buy:
		return append([]Order(nil), ob.buyOrders...)
	case Sell:
		return append([]Order(nil), ob.sellOrders...)
	default:
		return nil
	}
}

func (ob *OrderBook) StartMatching() {
	for {
		ob.matchOrders()
		time.Sleep(10 * time.Millisecond)
	}
}

func (ob *OrderBook) matchOrders() {
	ob.mutex.Lock()
	defer ob.mutex.Unlock()

	var trades []TradeExecution

	for len(ob.buyOrders) > 0 && len(ob.sellOrders) > 0 {
		bestBuy := ob.buyOrders[0]
		bestSell := ob.sellOrders[0]

		if bestBuy.Price >= bestSell.Price {
			tradeQuantity := min(bestBuy.Quantity, bestSell.Quantity)
			tradePrice := bestSell.Price

			trades = append(trades, TradeExecution{
				BuyOrderID:  bestBuy.OrderID,
				SellOrderID: bestSell.OrderID,
				Price:       tradePrice,
				Quantity:    tradeQuantity,
				Timestamp:   time.Now().UnixNano(),
			})

			if bestBuy.Quantity == tradeQuantity {
				ob.buyOrders = ob.buyOrders[1:]
			} else {
				ob.buyOrders[0].Quantity -= tradeQuantity
			}

			if bestSell.Quantity == tradeQuantity {
				ob.sellOrders = ob.sellOrders[1:]
			} else {
				ob.sellOrders[0].Quantity -= tradeQuantity
			}
		} else {
			break
		}
	}

	if len(trades) > 0 {
		ob.tradeChan <- trades
	}
}

func (ob *OrderBook) GetTradeChan() <-chan []TradeExecution {
	return ob.tradeChan
}

func validateOrder(order Order) error {
	if order.Symbol != "BTCUSD" && order.Symbol != "ETHUSD" {
		return errors.New("unsupported symbol")
	}
	if order.Price <= 0 {
		return errors.New("price must be positive")
	}
	if order.Quantity <= 0 {
		return errors.New("quantity must be positive")
	}
	if order.Timestamp > time.Now().UnixNano()+int64(time.Second) {
		return errors.New("timestamp is in the future")
	}
	return nil
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}