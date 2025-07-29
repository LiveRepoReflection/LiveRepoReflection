package order_optimizer

import (
	"sort"
	"strconv"
	"strings"
)

// CalculateOptimalBuy processes a stream of order book events and determines the optimal market order placement.
// It returns the optimal ask price at which the order can be placed and the total executed quantity.
func CalculateOptimalBuy(events []string, targetQty int, slippage float64, maxOrderSize int, commission float64) (int, int) {
	// order books: price -> quantity aggregated
	bidBook := make(map[int]int)
	askBook := make(map[int]int)

	// Process each event in the stream
	for _, event := range events {
		parts := strings.Split(event, ",")
		if len(parts) != 4 {
			continue
		}
		eventType := parts[0]
		side := parts[1]
		price, err1 := strconv.Atoi(parts[2])
		quantity, err2 := strconv.Atoi(parts[3])
		if err1 != nil || err2 != nil || price <= 0 || quantity <= 0 {
			continue
		}

		switch eventType {
		case "NEW":
			if side == "BID" {
				bidBook[price] += quantity
			} else if side == "ASK" {
				askBook[price] += quantity
			}
		case "CANCEL", "TRADE":
			if side == "BID" {
				cur := bidBook[price]
				if quantity >= cur {
					delete(bidBook, price)
				} else {
					bidBook[price] = cur - quantity
				}
			} else if side == "ASK" {
				cur := askBook[price]
				if quantity >= cur {
					delete(askBook, price)
				} else {
					askBook[price] = cur - quantity
				}
			}
		}
	}

	// There must be at least one ask order to place a buy order.
	if len(askBook) == 0 {
		return -1, 0
	}

	// Determine the best bid price (the highest bid).
	bestBid := 0
	for price := range bidBook {
		if price > bestBid {
			bestBid = price
		}
	}
	// If no bids available, we cannot compute slippage correctly. Return -1.
	if bestBid == 0 {
		return -1, 0
	}

	// Sort ask prices in ascending order.
	var askPrices []int
	for price := range askBook {
		askPrices = append(askPrices, price)
	}
	sort.Ints(askPrices)

	// If target quantity is zero, return the lowest ask price and zero executed quantity.
	if targetQty == 0 {
		return askPrices[0], 0
	}

	// Iteratively accumulate ask orders while ensuring slippage constraint holds.
	executed := 0
	totalCost := 0
	optimalPrice := -1
	// Acceptable effective execution price must be below this threshold.
	threshold := float64(bestBid) * (1.0 + slippage)

	for _, price := range askPrices {
		// Cap fill per level by maxOrderSize.
		available := askBook[price]
		fillAvailable := available
		if fillAvailable > maxOrderSize {
			fillAvailable = maxOrderSize
		}
		// If no quantity is available at this level, continue.
		if fillAvailable <= 0 {
			continue
		}

		// Determine how many units we want to fill from this level.
		need := targetQty - executed
		fill := fillAvailable
		if need < fill {
			fill = need
		}

		// Calculate new cumulative execution result if full fill from this level is added.
		newExecuted := executed + fill
		newCost := totalCost + fill*price
		newAvg := float64(newCost) / float64(newExecuted)
		effectivePrice := newAvg * (1.0 + commission)

		// Check if the effective execution price respects the slippage constraint.
		if effectivePrice <= threshold {
			// Accept the fill from the entire level (or as much as needed).
			executed = newExecuted
			totalCost = newCost
			optimalPrice = price
			// If target quantity is met, we stop.
			if executed == targetQty {
				break
			}
		} else {
			// Cannot add this level without violating slippage constraint; do not consider partial fill.
			break
		}
	}

	// If no orders could be executed without breaking the slippage constraint, return -1.
	if optimalPrice == -1 {
		return -1, 0
	}

	return optimalPrice, executed
}