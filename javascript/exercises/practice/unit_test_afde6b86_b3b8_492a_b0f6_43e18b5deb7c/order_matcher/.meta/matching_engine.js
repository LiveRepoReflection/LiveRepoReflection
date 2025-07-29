class MatchingEngine {
  constructor() {
    // Using immutable updates by replacing the arrays on each modification.
    this.bids = [];
    this.asks = [];
    this.trades = [];
  }

  addOrder(order) {
    // Validate the order: price and quantity must be positive numbers.
    if (order.price <= 0 || order.quantity <= 0) {
      throw new Error("Invalid order: Price and quantity must be positive");
    }
    if (order.type !== "buy" && order.type !== "sell") {
      throw new Error("Invalid order type");
    }

    // Process buy orders
    if (order.type === "buy") {
      let incomingOrder = { ...order }; // create a copy for immutability

      // Attempt to match the buy order with the best available asks.
      while (
        incomingOrder.quantity > 0 &&
        this.asks.length > 0 &&
        this.asks[0].price <= incomingOrder.price
      ) {
        // Use the first ask (lowest price and oldest order when prices are equal).
        let askOrder = { ...this.asks[0] };
        const tradeQuantity = Math.min(incomingOrder.quantity, askOrder.quantity);
        const tradePrice = askOrder.price; // trade at the price of the resting ask order

        // Generate the trade object.
        const trade = {
          buyOrderId: incomingOrder.id,
          sellOrderId: askOrder.id,
          price: tradePrice,
          quantity: tradeQuantity,
          timestamp: Date.now()
        };
        this.trades.push(trade);

        // Reduce quantities for both orders based on the trade executed.
        incomingOrder.quantity -= tradeQuantity;
        askOrder.quantity -= tradeQuantity;

        // Create a new asks array with the updated ask order.
        if (askOrder.quantity === 0) {
          this.asks = this.asks.slice(1);
        } else {
          // Replace the matched ask with the reduced quantity.
          this.asks = [askOrder, ...this.asks.slice(1)];
        }
      }

      // If the incoming order is not completely filled, add it to the order book.
      if (incomingOrder.quantity > 0) {
        const newBid = incomingOrder;
        const newBids = [...this.bids, newBid];
        // Sort bids in descending order by price, then ascending order by timestamp.
        newBids.sort((a, b) => {
          if (b.price === a.price) {
            return a.timestamp - b.timestamp;
          }
          return b.price - a.price;
        });
        this.bids = newBids;
      }
    }

    // Process sell orders
    if (order.type === "sell") {
      let incomingOrder = { ...order }; // create a copy for immutability

      // Attempt to match the sell order with the best available bids.
      while (
        incomingOrder.quantity > 0 &&
        this.bids.length > 0 &&
        this.bids[0].price >= incomingOrder.price
      ) {
        // Use the first bid (highest price and oldest order when prices are equal).
        let bidOrder = { ...this.bids[0] };
        const tradeQuantity = Math.min(incomingOrder.quantity, bidOrder.quantity);
        const tradePrice = bidOrder.price; // trade at the price of the resting bid order

        // Generate the trade object.
        const trade = {
          buyOrderId: bidOrder.id,
          sellOrderId: incomingOrder.id,
          price: tradePrice,
          quantity: tradeQuantity,
          timestamp: Date.now()
        };
        this.trades.push(trade);

        // Reduce quantities for both orders based on the trade executed.
        incomingOrder.quantity -= tradeQuantity;
        bidOrder.quantity -= tradeQuantity;

        // Create a new bids array with the updated bid order.
        if (bidOrder.quantity === 0) {
          this.bids = this.bids.slice(1);
        } else {
          this.bids = [bidOrder, ...this.bids.slice(1)];
        }
      }

      // If the incoming order is not completely filled, add it to the order book.
      if (incomingOrder.quantity > 0) {
        const newAsk = incomingOrder;
        const newAsks = [...this.asks, newAsk];
        // Sort asks in ascending order by price, then ascending order by timestamp.
        newAsks.sort((a, b) => {
          if (a.price === b.price) {
            return a.timestamp - b.timestamp;
          }
          return a.price - b.price;
        });
        this.asks = newAsks;
      }
    }
  }

  cancelOrder(orderId) {
    // Attempt to cancel in bids first.
    const bidIndex = this.bids.findIndex((order) => order.id === orderId);
    if (bidIndex !== -1) {
      this.bids = [
        ...this.bids.slice(0, bidIndex),
        ...this.bids.slice(bidIndex + 1)
      ];
      return true;
    }
    // Attempt to cancel in asks next.
    const askIndex = this.asks.findIndex((order) => order.id === orderId);
    if (askIndex !== -1) {
      this.asks = [
        ...this.asks.slice(0, askIndex),
        ...this.asks.slice(askIndex + 1)
      ];
      return true;
    }
    return false;
  }

  getOrderBook() {
    // Return copies of the order arrays.
    return {
      bids: [...this.bids],
      asks: [...this.asks]
    };
  }
}

module.exports = MatchingEngine;