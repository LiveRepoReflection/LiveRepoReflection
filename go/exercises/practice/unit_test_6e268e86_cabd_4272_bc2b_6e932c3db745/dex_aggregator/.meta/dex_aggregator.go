package dex_aggregator

import (
	"errors"
	"sort"
	"sync"
)

type Order struct {
	DexID    string
	OrderID  string
	Price    float64
	Quantity float64
	Side     string // "bid" or "ask"
}

type OrderChange struct {
	Type     string  // "Add", "Modify", "Remove"
	Side     string  // "bid" or "ask"
	Price    float64
	Quantity float64
	OrderID  string
}

type OrderUpdate struct {
	DEXID     string
	TokenPair string
	Changes   []OrderChange
}

type AggregatedOrder struct {
	Price    float64
	Quantity float64
}

type AggregatedBook struct {
	Bids []AggregatedOrder
	Asks []AggregatedOrder
}

type Aggregator struct {
	tokenPair string
	topK      int
	mu        sync.Mutex
	orders    map[string]Order // composite key "DEXID:OrderID" -> Order
}

func NewAggregator(tokenPair string, topK int) *Aggregator {
	return &Aggregator{
		tokenPair: tokenPair,
		topK:      topK,
		orders:    make(map[string]Order),
	}
}

func compositeKey(dexID, orderID string) string {
	return dexID + ":" + orderID
}

func (agg *Aggregator) ProcessUpdate(update OrderUpdate) error {
	// Process update only if the token pair matches.
	if update.TokenPair != agg.tokenPair {
		return nil
	}

	agg.mu.Lock()
	defer agg.mu.Unlock()

	for _, change := range update.Changes {
		key := compositeKey(update.DEXID, change.OrderID)
		switch change.Type {
		case "Add":
			// If the order already exists, return an error.
			if _, exists := agg.orders[key]; exists {
				return errors.New("order already exists for Add")
			}
			agg.orders[key] = Order{
				DexID:    update.DEXID,
				OrderID:  change.OrderID,
				Price:    change.Price,
				Quantity: change.Quantity,
				Side:     change.Side,
			}
		case "Modify":
			// Modify an existing order.
			order, exists := agg.orders[key]
			if !exists {
				return errors.New("order does not exist for Modify")
			}
			order.Price = change.Price
			order.Quantity = change.Quantity
			agg.orders[key] = order
		case "Remove":
			if _, exists := agg.orders[key]; !exists {
				return errors.New("order does not exist for Remove")
			}
			delete(agg.orders, key)
		default:
			return errors.New("invalid update type")
		}
	}
	return nil
}

func (agg *Aggregator) GetAggregatedBook() AggregatedBook {
	agg.mu.Lock()
	defer agg.mu.Unlock()

	var bids []Order
	var asks []Order
	for _, order := range agg.orders {
		if order.Side == "bid" {
			bids = append(bids, order)
		} else if order.Side == "ask" {
			asks = append(asks, order)
		}
	}

	sort.Slice(bids, func(i, j int) bool {
		return bids[i].Price > bids[j].Price
	})

	sort.Slice(asks, func(i, j int) bool {
		return asks[i].Price < asks[j].Price
	})

	var aggregatedBids []AggregatedOrder
	var aggregatedAsks []AggregatedOrder

	k := agg.topK
	if len(bids) < k {
		k = len(bids)
	}
	for i := 0; i < k; i++ {
		aggregatedBids = append(aggregatedBids, AggregatedOrder{
			Price:    bids[i].Price,
			Quantity: bids[i].Quantity,
		})
	}

	k = agg.topK
	if len(asks) < k {
		k = len(asks)
	}
	for i := 0; i < k; i++ {
		aggregatedAsks = append(aggregatedAsks, AggregatedOrder{
			Price:    asks[i].Price,
			Quantity: asks[i].Quantity,
		})
	}

	return AggregatedBook{
		Bids: aggregatedBids,
		Asks: aggregatedAsks,
	}
}