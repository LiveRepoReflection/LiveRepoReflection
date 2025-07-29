const { OptimalRoutePlanner } = require('../route_optimize');

describe("OptimalRoutePlanner", () => {
  test("returns route with cost 0 when source equals destination", () => {
    const network = {
      centers: {
        "A": { capacity: 50, products: ["X"], transportCosts: {} }
      },
      initialInventory: { "A": { "X": 20 } }
    };
    const planner = new OptimalRoutePlanner();
    const result = planner.findOptimalRoute(network, "A", "A", "X", 10);
    expect(result).toEqual({ route: ["A"], cost: 0 });
  });

  test("returns null when source does not handle the product", () => {
    const network = {
      centers: {
        "A": { capacity: 50, products: ["Y"], transportCosts: { "B": { "X": 10 } } },
        "B": { capacity: 50, products: ["X"], transportCosts: {} }
      },
      initialInventory: { "A": { "Y": 20 } }
    };
    const planner = new OptimalRoutePlanner();
    const result = planner.findOptimalRoute(network, "A", "B", "X", 10);
    expect(result).toBeNull();
  });

  test("returns null when destination does not support the product", () => {
    const network = {
      centers: {
        "A": { capacity: 50, products: ["X"], transportCosts: { "B": { "X": 10 } } },
        "B": { capacity: 50, products: ["Y"], transportCosts: {} }
      },
      initialInventory: { "A": { "X": 20 } }
    };
    const planner = new OptimalRoutePlanner();
    const result = planner.findOptimalRoute(network, "A", "B", "X", 10);
    expect(result).toBeNull();
  });

  test("returns null when inventory is insufficient at the source", () => {
    const network = {
      centers: {
        "A": { capacity: 50, products: ["X"], transportCosts: { "B": { "X": 10 } } },
        "B": { capacity: 50, products: ["X"], transportCosts: {} }
      },
      initialInventory: { "A": { "X": 5 } }
    };
    const planner = new OptimalRoutePlanner();
    const result = planner.findOptimalRoute(network, "A", "B", "X", 10);
    expect(result).toBeNull();
  });

  test("finds the optimal route with cost minimization", () => {
    const network = {
      centers: {
        "A": { capacity: 100, products: ["X"], transportCosts: { "B": { "X": 5 }, "C": { "X": 10 } } },
        "B": { capacity: 100, products: ["X"], transportCosts: { "C": { "X": 3 }, "D": { "X": 1 } } },
        "C": { capacity: 100, products: ["X"], transportCosts: { "D": { "X": 2 } } },
        "D": { capacity: 100, products: ["X"], transportCosts: {} }
      },
      initialInventory: {
        "A": { "X": 20 },
        "B": { "X": 5 },
        "C": { "X": 10 },
        "D": { "X": 0 }
      }
    };
    const planner = new OptimalRoutePlanner();
    const result = planner.findOptimalRoute(network, "A", "D", "X", 10);
    expect(result).toEqual({ route: ["A", "B", "D"], cost: 6 });
  });

  test("returns null when an intermediate center exceeds capacity constraints", () => {
    const network = {
      centers: {
        "A": { capacity: 15, products: ["X"], transportCosts: { "B": { "X": 3 } } },
        "B": { capacity: 10, products: ["X"], transportCosts: { "C": { "X": 4 } } },
        "C": { capacity: 20, products: ["X"], transportCosts: {} }
      },
      initialInventory: {
        "A": { "X": 15 },
        "B": { "X": 5 },
        "C": { "X": 0 }
      }
    };
    const planner = new OptimalRoutePlanner();
    const result = planner.findOptimalRoute(network, "A", "C", "X", 10);
    expect(result).toBeNull();
  });

  test("selects the route with the lowest cost when multiple routes are available", () => {
    const network = {
      centers: {
        "A": { capacity: 100, products: ["X"], transportCosts: { "B": { "X": 10 }, "C": { "X": 20 } } },
        "B": { capacity: 100, products: ["X"], transportCosts: { "D": { "X": 10 } } },
        "C": { capacity: 100, products: ["X"], transportCosts: { "D": { "X": 1 } } },
        "D": { capacity: 100, products: ["X"], transportCosts: {} }
      },
      initialInventory: {
        "A": { "X": 30 },
        "B": { "X": 0 },
        "C": { "X": 0 },
        "D": { "X": 0 }
      }
    };
    const planner = new OptimalRoutePlanner();
    const result = planner.findOptimalRoute(network, "A", "D", "X", 10);
    expect(result).toEqual({ route: ["A", "B", "D"], cost: 20 });
  });
});