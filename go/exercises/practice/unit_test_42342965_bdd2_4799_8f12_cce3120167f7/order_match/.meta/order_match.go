package order_match

import (
	"errors"
	"math"
	"sort"
	"sync"
)

// Order represents a buy or sell order.
type Order struct {
	OrderID   string
	Symbol    string
	Type      string  // "BUY" or "SELL"
	Price     float64 // Price of the order. Price = 0 for a market order.
	Quantity  int
	Timestamp int64
}

// Trade represents an executed trade between a buy and a sell order.
type Trade struct {
	Price       float64
	Quantity    int
	BuyOrderID  string
	SellOrderID string
}

// OrderBook holds a list of buy and sell orders for a specific symbol.
type OrderBook struct {
	buyOrders  []Order
	sellOrders []Order
}

// Engine is the order matching engine which maintains order books for various symbols.
type Engine struct {
	books map[string]*OrderBook
	mu    sync.Mutex
}

// NewEngine creates and returns a new Engine instance.
func NewEngine() *Engine {
	return &Engine{
		books: make(map[string]*OrderBook),
	}
}

// PlaceOrder adds a new order to the appropriate order book.
func (e *Engine) PlaceOrder(order Order) error {
	e.mu.Lock()
	defer e.mu.Unlock()

	book, exists := e.books[order.Symbol]
	if !exists {
		book = &OrderBook{}
		e.books[order.Symbol] = book
	}
	if order.Type == "BUY" {
		book.buyOrders = append(book.buyOrders, order)
	} else if order.Type == "SELL" {
		book.sellOrders = append(book.sellOrders, order)
	} else {
		return errors.New("invalid order type")
	}
	return nil
}

// CancelOrder removes an order identified by orderID from the order books.
func (e *Engine) CancelOrder(orderID string) error {
	e.mu.Lock()
	defer e.mu.Unlock()
	found := false
	for _, book := range e.books {
		// Check buy orders.
		for i, o := range book.buyOrders {
			if o.OrderID == orderID {
				book.buyOrders = append(book.buyOrders[:i], book.buyOrders[i+1:]...)
				found = true
				break
			}
		}
		// Check sell orders.
		for i, o := range book.sellOrders {
			if o.OrderID == orderID {
				book.sellOrders = append(book.sellOrders[:i], book.sellOrders[i+1:]...)
				found = true
				break
			}
		}
	}
	if !found {
		return errors.New("order not found")
	}
	return nil
}

// effectivePrice computes the effective price for ordering purposes.
// For a BUY market order (Price == 0) it returns MaxFloat64 to prioritize it,
// and for a SELL market order it returns 0.
func effectivePrice(order Order) float64 {
	if order.Price == 0 {
		if order.Type == "BUY" {
			return math.MaxFloat64
		} else if order.Type == "SELL" {
			return 0
		}
	}
	return order.Price
}

// MatchOrders processes matching for orders of a given symbol and returns the executed trades.
func (e *Engine) MatchOrders(symbol string) []Trade {
	e.mu.Lock()
	defer e.mu.Unlock()

	trades := []Trade{}
	book, exists := e.books[symbol]
	if !exists {
		return trades
	}

	// Sort buy orders: descending by effective price, then ascending by timestamp.
	sort.Slice(book.buyOrders, func(i, j int) bool {
		pi := effectivePrice(book.buyOrders[i])
		pj := effectivePrice(book.buyOrders[j])
		if pi == pj {
			return book.buyOrders[i].Timestamp < book.buyOrders[j].Timestamp
		}
		return pi > pj
	})

	// Sort sell orders: ascending by effective price, then ascending by timestamp.
	sort.Slice(book.sellOrders, func(i, j int) bool {
		pi := effectivePrice(book.sellOrders[i])
		pj := effectivePrice(book.sellOrders[j])
		if pi == pj {
			return book.sellOrders[i].Timestamp < book.sellOrders[j].Timestamp
		}
		return pi < pj
	})

	// Process matching until no more orders can be matched.
	for len(book.buyOrders) > 0 && len(book.sellOrders) > 0 {
		buyOrder := &book.buyOrders[0]
		sellOrder := &book.sellOrders[0]

		// For limit buy orders, ensure the buy price is high enough to cover the sell price.
		// Market buy orders (Price == 0) are prioritized and matched regardless.
		if buyOrder.Price > 0 && buyOrder.Price < sellOrder.Price {
			break
		}

		// Determine the quantity to trade.
		quantity := buyOrder.Quantity
		if sellOrder.Quantity < quantity {
			quantity = sellOrder.Quantity
		}
		tradePrice := sellOrder.Price

		// Record the trade.
		trade := Trade{
			Price:       tradePrice,
			Quantity:    quantity,
			BuyOrderID:  buyOrder.OrderID,
			SellOrderID: sellOrder.OrderID,
		}
		trades = append(trades, trade)

		// Update the order quantities.
		buyOrder.Quantity -= quantity
		sellOrder.Quantity -= quantity

		// Remove fully executed orders.
		if buyOrder.Quantity == 0 {
			book.buyOrders = book.buyOrders[1:]
		}
		if sellOrder.Quantity == 0 {
			book.sellOrders = book.sellOrders[1:]
		}
	}
	return trades
}