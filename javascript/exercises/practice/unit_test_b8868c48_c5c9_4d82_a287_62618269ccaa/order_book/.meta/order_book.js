class OrderBookAggregator {
  constructor() {
    // books structure: { [symbol]: { buy: Map, sell: Map } }
    // Each side's Map: key = price (number), value = { total: Number, exchanges: Map }
    // exchanges Map: key = exchange (string), value = { quantity: Number, timestamp: Number }
    this.books = {};
  }

  update(update) {
    const { timestamp, symbol, side, price, quantity, exchange } = update;

    if (!this.books[symbol]) {
      this.books[symbol] = { buy: new Map(), sell: new Map() };
    }

    const sideBook = this.books[symbol][side];
    // Check if the price level already exists.
    if (!sideBook.has(price)) {
      if (quantity === 0) {
        // Nothing to remove if level doesn't exist.
        return;
      }
      // Create new price level.
      const exchanges = new Map();
      exchanges.set(exchange, { quantity, timestamp });
      sideBook.set(price, { total: quantity, exchanges });
    } else {
      // Update existing price level.
      const priceLevel = sideBook.get(price);
      const exMap = priceLevel.exchanges;
      if (exMap.has(exchange)) {
        const existingRecord = exMap.get(exchange);
        // Discard out-of-order updates.
        if (timestamp < existingRecord.timestamp) {
          return;
        }
        if (quantity === 0) {
          exMap.delete(exchange);
        } else {
          exMap.set(exchange, { quantity, timestamp });
        }
      } else {
        if (quantity !== 0) {
          exMap.set(exchange, { quantity, timestamp });
        }
      }
      // Recalculate aggregated total quantity at this price level.
      let aggregated = 0;
      for (const record of exMap.values()) {
        aggregated += record.quantity;
      }
      if (aggregated === 0) {
        sideBook.delete(price);
      } else {
        priceLevel.total = aggregated;
      }
    }
  }

  getBestBid(symbol) {
    if (!this.books[symbol]) return null;
    const buyBook = this.books[symbol].buy;
    if (buyBook.size === 0) return null;
    // For buy side, best bid is the highest price.
    let bestPrice = -Infinity;
    for (const price of buyBook.keys()) {
      if (price > bestPrice) {
        bestPrice = price;
      }
    }
    const level = buyBook.get(bestPrice);
    return { price: bestPrice, quantity: level.total };
  }

  getBestAsk(symbol) {
    if (!this.books[symbol]) return null;
    const sellBook = this.books[symbol].sell;
    if (sellBook.size === 0) return null;
    // For sell side, best ask is the lowest price.
    let bestPrice = Infinity;
    for (const price of sellBook.keys()) {
      if (price < bestPrice) {
        bestPrice = price;
      }
    }
    const level = sellBook.get(bestPrice);
    return { price: bestPrice, quantity: level.total };
  }

  getDepth(symbol, depth) {
    if (!this.books[symbol]) return { buy: 0, sell: 0 };
    const buyEntries = Array.from(this.books[symbol].buy.entries());
    const sellEntries = Array.from(this.books[symbol].sell.entries());
    // Sort: buy side in descending order, sell side in ascending order.
    buyEntries.sort((a, b) => b[0] - a[0]);
    sellEntries.sort((a, b) => a[0] - b[0]);

    let totalBuy = 0;
    let totalSell = 0;
    for (let i = 0; i < Math.min(depth, buyEntries.length); i++) {
      totalBuy += buyEntries[i][1].total;
    }
    for (let i = 0; i < Math.min(depth, sellEntries.length); i++) {
      totalSell += sellEntries[i][1].total;
    }
    return { buy: totalBuy, sell: totalSell };
  }

  calculateWAP(symbol, side, desiredQuantity) {
    if (!this.books[symbol]) return null;
    const sideBook = Array.from(this.books[symbol][side].entries());
    if (sideBook.length === 0) return null;
    // For buy side, iterate from highest to lowest price.
    // For sell side, iterate from lowest to highest price.
    if (side === "buy") {
      sideBook.sort((a, b) => b[0] - a[0]);
    } else if (side === "sell") {
      sideBook.sort((a, b) => a[0] - b[0]);
    }
    let remaining = desiredQuantity;
    let weightedSum = 0;
    for (const [price, level] of sideBook) {
      if (remaining <= level.total) {
        weightedSum += price * remaining;
        remaining = 0;
        break;
      } else {
        weightedSum += price * level.total;
        remaining -= level.total;
      }
    }
    if (remaining > 0) {
      return null;
    }
    return weightedSum / desiredQuantity;
  }

  getSymbols() {
    return Object.keys(this.books);
  }
}

module.exports = { OrderBookAggregator };