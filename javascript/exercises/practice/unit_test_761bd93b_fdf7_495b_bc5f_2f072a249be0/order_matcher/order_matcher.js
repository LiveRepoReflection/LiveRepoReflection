/**
 * @typedef {Object.<number, string[]>} OrderBook - A map of prices to an array of order IDs.
 * @typedef {Object.<string, number>} OrderQuantities - A map of order IDs to their quantities.
 */

/**
 * Allocates a market buy order against the existing limit sell orders in the order book.
 *
 * @param {OrderBook} orderBook - The ask side of the order book. Prices are keys.
 * @param {OrderQuantities} orderQuantities - A map of order IDs to their quantities.
 * @param {number} marketBuyOrderQuantity - The quantity of the asset to buy.
 * @returns {Array<[string, number]>} A list of filled orders, each as a [orderId, filledQuantity] tuple.
 */
function allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity) {
    // If there's nothing to buy, return immediately.
    if (marketBuyOrderQuantity <= 0) {
        return [];
    }

    // Get all price levels from the order book.
    // Object.keys() returns strings, so we map them to numbers.
    const sortedPrices = Object.keys(orderBook).map(Number).sort((a, b) => a - b);

    // This will store the final list of trades.
    const filledOrders = [];
    let remainingQuantityToFill = marketBuyOrderQuantity;

    // Iterate through the price levels, starting from the lowest (best price for a buyer).
    for (const price of sortedPrices) {
        const orderIdsAtPrice = orderBook[price];

        // Iterate through the orders at this price level (respecting FIFO).
        for (const orderId of orderIdsAtPrice) {
            const orderAvailableQuantity = orderQuantities[orderId];
            if (!orderAvailableQuantity || orderAvailableQuantity <= 0) {
                continue; // Skip if order has no quantity (e.g., already filled or invalid data).
            }

            // Determine the amount to fill from this order.
            // It's the smaller of what's left to fill and what this order has available.
            const fillAmount = Math.min(remainingQuantityToFill, orderAvailableQuantity);

            if (fillAmount > 0) {
                filledOrders.push([orderId, fillAmount]);
                remainingQuantityToFill -= fillAmount;
            }

            // If the market order is completely filled, we can stop and return.
            if (remainingQuantityToFill <= 0) {
                return filledOrders;
            }
        }
    }

    // If the loop finishes but the order is not fully filled, return what we have.
    return filledOrders;
}

module.exports = {
    allocateMarketBuyOrder
};