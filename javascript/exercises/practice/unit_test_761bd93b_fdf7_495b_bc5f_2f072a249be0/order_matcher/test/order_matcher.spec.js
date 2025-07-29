const { allocateMarketBuyOrder } = require('../solution');

describe('Optimal Order Allocation', () => {

    // Test case from the problem description
    test('should correctly fill the market order from the example', () => {
        const orderBook = {
            100: ["order1", "order2"],
            101: ["order3"],
            102: ["order4", "order5"]
        };
        const orderQuantities = {
            "order1": 5,
            "order2": 10,
            "order3": 7,
            "order4": 3,
            "order5": 8
        };
        const marketBuyOrderQuantity = 15;
        const expected = [
            ["order1", 5],
            ["order2", 10]
        ];
        expect(allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity)).toEqual(expected);
    });

    // Test case for partial fill due to insufficient liquidity
    test('should fill as much as possible when market order is larger than total book quantity', () => {
        const orderBook = {
            100: ["order1"],
            101: ["order2"]
        };
        const orderQuantities = {
            "order1": 10,
            "order2": 15
        };
        const marketBuyOrderQuantity = 30; // More than available 25
        const expected = [
            ["order1", 10],
            ["order2", 15]
        ];
        expect(allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity)).toEqual(expected);
    });

    // Test case where market order is smaller than the first available limit order
    test('should partially fill the first available order if market order is smaller', () => {
        const orderBook = {
            100: ["order1", "order2"]
        };
        const orderQuantities = {
            "order1": 20,
            "order2": 10
        };
        const marketBuyOrderQuantity = 5;
        const expected = [
            ["order1", 5]
        ];
        expect(allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity)).toEqual(expected);
    });

    // Test case for an empty order book
    test('should return an empty array for an empty order book', () => {
        const orderBook = {};
        const orderQuantities = {};
        const marketBuyOrderQuantity = 100;
        expect(allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity)).toEqual([]);
    });

    // Test case for a zero quantity market order
    test('should return an empty array for a zero quantity market buy order', () => {
        const orderBook = {
            100: ["order1"]
        };
        const orderQuantities = {
            "order1": 10
        };
        const marketBuyOrderQuantity = 0;
        expect(allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity)).toEqual([]);
    });

    // Test case to verify correct handling of unsorted prices in the input object
    test('should prioritize lowest price even if keys in orderBook are not sorted', () => {
        const orderBook = {
            105: ["order3"],
            100: ["order1"],
            102: ["order2"]
        };
        const orderQuantities = {
            "order1": 10,
            "order2": 10,
            "order3": 10
        };
        const marketBuyOrderQuantity = 15;
        const expected = [
            ["order1", 10],
            ["order2", 5]
        ];
        expect(allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity)).toEqual(expected);
    });

    // Test case to verify FIFO logic at the same price level
    test('should respect FIFO order for multiple orders at the same price', () => {
        const orderBook = {
            100: ["orderA", "orderB", "orderC"]
        };
        const orderQuantities = {
            "orderA": 5,
            "orderB": 5,
            "orderC": 5
        };
        const marketBuyOrderQuantity = 12;
        const expected = [
            ["orderA", 5],
            ["orderB", 5],
            ["orderC", 2]
        ];
        expect(allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity)).toEqual(expected);
    });

    // More complex scenario spanning multiple price levels
    test('should correctly fill across multiple price levels', () => {
        const orderBook = {
            202: ["orderE"],
            200: ["orderA", "orderB"],
            201: ["orderC", "orderD"],
        };
        const orderQuantities = {
            "orderA": 10,
            "orderB": 15,
            "orderC": 5,
            "orderD": 20,
            "orderE": 30
        };
        const marketBuyOrderQuantity = 45;
        // Expected fill: 10 (A) + 15 (B) = 25 @ 200. Remaining: 20
        // Fill: 5 (C) + 15 (from D) @ 201. Total Filled: 25 + 20 = 45
        const expected = [
            ["orderA", 10],
            ["orderB", 15],
            ["orderC", 5],
            ["orderD", 15]
        ];
        expect(allocateMarketBuyOrder(orderBook, orderQuantities, marketBuyOrderQuantity)).toEqual(expected);
    });
});