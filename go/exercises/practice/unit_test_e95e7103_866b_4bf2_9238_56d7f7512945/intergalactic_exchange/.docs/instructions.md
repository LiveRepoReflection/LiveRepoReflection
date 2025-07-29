Okay, here's a challenging Go coding problem designed to be difficult and sophisticated, focusing on optimization, multiple edge cases, and algorithmic efficiency.

**Project Name:** `IntergalacticExchange`

**Question Description:**

The Intergalactic Exchange (IGE) is a decentralized marketplace where traders buy and sell goods across multiple star systems. Each star system uses its own unique cryptocurrency, and the IGE facilitates trades by automatically converting currencies along optimal exchange routes.

You are tasked with implementing the core routing engine for the IGE. Given a network of star systems, their respective cryptocurrencies, and the exchange rates between them, determine the most profitable sequence of exchanges to maximize the value of a trader's initial investment.

**Specifics:**

1.  **Input:**
    *   `systems map[string]string`: A map where the key is the name of a star system (e.g., "AlphaCentauri") and the value is the ticker symbol of its cryptocurrency (e.g., "AC").  System names are unique.
    *   `rates map[string]map[string]float64`: A nested map representing the exchange rates between currencies. `rates["AC"]["BC"]` would represent the exchange rate from cryptocurrency "AC" to cryptocurrency "BC".  Not all currency pairs will have a direct exchange rate. If no direct route exists, there will be no entry. Exchange rates are positive floats. `rates["AC"]["AC"]` is implicitly 1.0 and not explicitly stored.
    *   `startSystem string`: The name of the star system where the trader begins.
    *   `endSystem string`: The name of the star system where the trader wants to end up.
    *   `initialInvestment float64`: The trader's initial investment amount in the cryptocurrency of the `startSystem`.

2.  **Output:**
    *   A `[]string` representing the optimal sequence of star systems to visit, **including** the start and end systems. If no profitable route exists, return an empty slice (`[]string{}`). If the start and end systems are the same, return a slice containing only the start/end system (`[]string{startSystem}`).
    *   The sequence must maximize the final amount of currency in the `endSystem`.

3.  **Constraints and Edge Cases:**
    *   The number of star systems can be large (up to 1000).
    *   The exchange rate data may contain cycles. You must handle the possibility of arbitrage (finding a cycle that yields a profit).
    *   Not all star systems are necessarily connected.  If there's no path from the `startSystem` to the `endSystem`, return an empty slice.
    *   Exchange rates can fluctuate rapidly. Minimize the number of exchanges to reduce the risk of rate changes invalidating the route.
    *   The `initialInvestment` is always a positive number.
    *   System and currency names are case-sensitive.
    *   A direct exchange rate between two currencies might not exist (requiring intermediate exchanges).
    *   If multiple routes yield the same maximum profit, return the shortest route (fewest number of exchanges).  If still tied, return the lexicographically smallest route (comparing system names).
    *   Handle potential floating-point precision issues.
    *   The solution must have acceptable performance, ideally avoiding brute-force approaches. A solution with a time complexity better than O(N!) is required.

4. **Implicit Requirements**
    * If startSystem and endSystem are the same, the function should return `[]string{startSystem}`.

5.  **Evaluation Criteria:**
    *   Correctness: The solution must produce the optimal route in all test cases.
    *   Efficiency: The solution must be performant, especially with a large number of star systems.
    *   Handling Edge Cases: The solution must correctly handle all specified edge cases.
    *   Code Quality: The code should be well-structured, readable, and maintainable.

This problem requires a combination of graph algorithms (finding paths), dynamic programming (optimizing for profit), and careful handling of edge cases. Good luck!
