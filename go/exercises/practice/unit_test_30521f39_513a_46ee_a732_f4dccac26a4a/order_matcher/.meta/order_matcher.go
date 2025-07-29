package ordermatcher

import (
	"sort"
	"sync"
)

// orderBook represents a price-time priority order book
type orderBook struct {
	orders []Order
	mutex  sync.RWMutex
}

// newOrderBook creates a new order book
func newOrderBook() *orderBook {
	return &orderBook{
		orders: make([]Order, 0),
	}
}

// add inserts an order into the order book maintaining price-time priority
func (ob *orderBook) add(order Order) {
	ob.mutex.Lock()
	defer ob.mutex.Unlock()

	// Ignore invalid orders
	if order.Price <= 0 || order.Quantity <= 0 {
		return
	}

	ob.orders = append(ob.orders, order)
}

// sortBuyOrders sorts buy orders by price (highest first) and time (earliest first)
func sortBuyOrders(orders []Order) {
	sort.Slice(orders, func(i, j int) bool {
		if orders[i].Price != orders[j].Price {
			return orders[i].Price > orders[j].Price
		}
		return orders[i].Timestamp < orders[j].Timestamp
	})
}

// sortSellOrders sorts sell orders by price (lowest first) and time (earliest first)
func sortSellOrders(orders []Order) {
	sort.Slice(orders, func(i, j int) bool {
		if orders[i].Price != orders[j].Price {
			return orders[i].Price < orders[j].Price
		}
		return orders[i].Timestamp < orders[j].Timestamp
	})
}

// MatchOrders matches buy and sell orders based on price-time priority
func MatchOrders(buyOrders []Order, sellOrders []Order) []Trade {
	trades := make([]Trade, 0)
	
	// Create order books
	buyBook := newOrderBook()
	sellBook := newOrderBook()

	// Add valid orders to the books
	for _, order := range buyOrders {
		buyBook.add(order)
	}
	for _, order := range sellOrders {
		sellBook.add(order)
	}

	// Sort orders by price-time priority
	sortBuyOrders(buyBook.orders)
	sortSellOrders(sellBook.orders)

	// Track remaining quantities for partial fills
	remainingQty := make(map[string]int)
	for _, order := range buyBook.orders {
		remainingQty[order.OrderID] = order.Quantity
	}
	for _, order := range sellBook.orders {
		remainingQty[order.OrderID] = order.Quantity
	}

	// Match orders
	for _, buy := range buyBook.orders {
		if remainingQty[buy.OrderID] <= 0 {
			continue
		}

		for j := 0; j < len(sellBook.orders); j++ {
			sell := sellBook.orders[j]
			
			// Skip if sell order is fully matched
			if remainingQty[sell.OrderID] <= 0 {
				continue
			}

			// Check if price matches (buy price >= sell price)
			if buy.Price < sell.Price {
				break
			}

			// Prevent self-trading
			if buy.UserID == sell.UserID {
				continue
			}

			// Calculate trade quantity
			quantity := min(remainingQty[buy.OrderID], remainingQty[sell.OrderID])
			
			if quantity > 0 {
				// Create trade
				trade := Trade{
					BuyOrderID:  buy.OrderID,
					SellOrderID: sell.OrderID,
					Price:       sell.Price,
					Quantity:    quantity,
				}
				trades = append(trades, trade)

				// Update remaining quantities
				remainingQty[buy.OrderID] -= quantity
				remainingQty[sell.OrderID] -= quantity
			}

			// If buy order is fully matched, move to next buy order
			if remainingQty[buy.OrderID] <= 0 {
				break
			}
		}
	}

	// Sort trades by buy order timestamp
	sort.Slice(trades, func(i, j int) bool {
		var buyI, buyJ Order
		for _, order := range buyBook.orders {
			if order.OrderID == trades[i].BuyOrderID {
				buyI = order
			}
			if order.OrderID == trades[j].BuyOrderID {
				buyJ = order
			}
		}
		return buyI.Timestamp < buyJ.Timestamp
	})

	return trades
}

func min(a, b int) int {
	if a < b {
		return a
	}
	return b
}