const { findOptimalRoute } = require('./route_optimizer');

describe('findOptimalRoute', () => {
  test('simple direct route', () => {
    const cityMap = {
      "A": [{
        to: "B",
        travelTime: 10,
        congestionFunction: (t) => 1.0
      }],
      "B": []
    };
    const result = findOptimalRoute(cityMap, "A", "B");
    expect(result.totalTime).toBeCloseTo(10.00, 2);
    expect(result.route).toEqual(["A", "B"]);
  });

  test('multiple routes with different congestion', () => {
    const cityMap = {
      "A": [
        { to: "B", travelTime: 10, congestionFunction: (t) => 1.0 },
        { to: "C", travelTime: 20, congestionFunction: (t) => 0.5 }
      ],
      "B": [
        { to: "D", travelTime: 15, congestionFunction: (t) => 1.0 }
      ],
      "C": [
        { to: "D", travelTime: 5, congestionFunction: (t) => 1.0 }
      ],
      "D": []
    };
    // A -> C -> D: travel time = (20 * 0.5) + (5 * 1.0) = 10 + 5 = 15
    // A -> B -> D: travel time = 10 + 15 = 25
    const result = findOptimalRoute(cityMap, "A", "D");
    expect(result.totalTime).toBeCloseTo(15.00, 2);
    expect(result.route).toEqual(["A", "C", "D"]);
  });

  test('time dependent congestion', () => {
    const cityMap = {
      "A": [{
        to: "B",
        travelTime: 10,
        congestionFunction: (t) => t < 5 ? 0.8 : 1.2
      }],
      "B": [{
        to: "C",
        travelTime: 15,
        congestionFunction: (t) => t < 15 ? 1.0 : 0.9
      }],
      "C": []
    };
    // For route A->B->C:
    // Road A->B: at time 0, congestion = 0.8, so time = 10*0.8 = 8
    // Road B->C: starting at time 8 (<15), congestion = 1.0, so time = 15
    // Total = 8 + 15 = 23
    const result = findOptimalRoute(cityMap, "A", "C");
    expect(result.totalTime).toBeCloseTo(23.00, 2);
    expect(result.route).toEqual(["A", "B", "C"]);
  });

  test('no route available', () => {
    const cityMap = {
      "A": [{ to: "B", travelTime: 10, congestionFunction: (t) => 1.0 }],
      "B": [],
      "C": []  // C is isolated
    };
    const result = findOptimalRoute(cityMap, "A", "C");
    expect(result.totalTime).toBe(-1);
    expect(result.route).toEqual([]);
  });

  test('handling cycle in the graph', () => {
    // Graph with cycle: A -> B, B -> C, C -> A, and B -> D
    const cityMap = {
      "A": [{ to: "B", travelTime: 5, congestionFunction: (t) => 1.0 }],
      "B": [
        { to: "C", travelTime: 5, congestionFunction: (t) => 1.0 },
        { to: "D", travelTime: 20, congestionFunction: (t) => 1.0 }
      ],
      "C": [{ to: "A", travelTime: 5, congestionFunction: (t) => 1.0 }],
      "D": []
    };
    // Best route should be A -> B -> D = 5 + 20 = 25
    const result = findOptimalRoute(cityMap, "A", "D");
    expect(result.totalTime).toBeCloseTo(25.00, 2);
    expect(result.route).toEqual(["A", "B", "D"]);
  });

  test('multiple valid approaches with trade-offs', () => {
    const cityMap = {
      "A": [
        { to: "B", travelTime: 8, congestionFunction: (t) => 1.0 },
        { to: "C", travelTime: 20, congestionFunction: (t) => 0.9 }
      ],
      "B": [
        { to: "D", travelTime: 12, congestionFunction: (t) => t < 10 ? 1.2 : 1.0 },
        { to: "E", travelTime: 30, congestionFunction: (t) => 1.0 }
      ],
      "C": [
        { to: "D", travelTime: 5, congestionFunction: (t) => 1.1 },
        { to: "E", travelTime: 10, congestionFunction: (t) => 1.0 }
      ],
      "D": [
        { to: "F", travelTime: 7, congestionFunction: (t) => 1.0 }
      ],
      "E": [
        { to: "F", travelTime: 5, congestionFunction: (t) => 1.2 }
      ],
      "F": []
    };
    // Evaluate potential routes:
    // Route 1: A -> B -> D -> F:
    //   A->B: 8 * 1.0 = 8 (arrival at 8)
    //   B->D: at t=8, congestionFunction returns 1.2, so 12 * 1.2 = 14.4 (arrival at 22.4)
    //   D->F: 7 * 1.0 = 7, total = 8 + 14.4 + 7 = 29.4
    // Route 2: A -> C -> E -> F:
    //   A->C: 20 * 0.9 = 18 (arrival at 18)
    //   C->E: 10 * 1.0 = 10 (arrival at 28)
    //   E->F: 5 * 1.2 = 6, total = 18 + 10 + 6 = 34
    // Route 3: A -> C -> D -> F:
    //   A->C: 18 (arrival at 18)
    //   C->D: 5 * 1.1 = 5.5 (arrival at 23.5)
    //   D->F: 7 * 1.0 = 7, total = 18 + 5.5 + 7 = 30.5
    const result = findOptimalRoute(cityMap, "A", "F");
    expect(result.totalTime).toBeCloseTo(29.40, 2);
    expect(result.route).toEqual(["A", "B", "D", "F"]);
  });
});