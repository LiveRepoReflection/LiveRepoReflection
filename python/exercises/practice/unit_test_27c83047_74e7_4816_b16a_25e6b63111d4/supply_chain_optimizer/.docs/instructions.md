## Question: Dynamic Supply Chain Optimization

### Description

You are tasked with building a system to optimize a dynamic supply chain for a nationwide retailer. The retailer has multiple warehouses and stores across the country. Each warehouse holds a limited inventory of products, and each store has a demand for those products. The supply chain is "dynamic" because both the inventory levels at warehouses and the demands at stores change frequently and unpredictably.

The goal is to minimize the overall cost of fulfilling store demands by strategically shipping products from warehouses. The cost is primarily driven by transportation expenses, which vary based on the distance between warehouses and stores, and the quantity of products shipped. However, there is also a penalty for unfulfilled demand at each store.

**Specifics:**

*   **Warehouses:** Each warehouse has a unique ID, location (latitude and longitude), and a dictionary representing its current inventory. The dictionary keys are product IDs, and the values are the quantity of each product available. The inventory is updated in real-time.
*   **Stores:** Each store has a unique ID, location (latitude and longitude), a dictionary representing its current demand, and a penalty cost per unit of unfulfilled demand for each product. Similar to the warehouse, dictionary keys are product IDs, and the values are the quantity of each product required. The demand is updated in real-time.
*   **Products:** Products are identified by unique IDs.
*   **Transportation Cost:** The cost of shipping one unit of a product from a warehouse to a store is proportional to the Euclidean distance between them. A `transportation_rate` is provided as input, which is the cost per unit distance per unit of product.
*   **Optimization Goal:** Minimize the total cost, which is the sum of transportation costs and unfulfilled demand penalties across all stores and products.

**Constraints:**

1.  **Warehouse Capacity:** The total quantity of each product shipped from a warehouse cannot exceed its current inventory.
2.  **Store Demand:** The total quantity of each product received by a store cannot exceed its current demand.
3.  **Real-time Updates:** Inventory and demand levels change frequently. The system must be able to re-optimize the supply chain quickly in response to these changes.
4.  **Scalability:** The system should be designed to handle a large number of warehouses, stores, and products.
5.  **No Splitting Product Units**: You can only ship whole units of a product, that is, no fractional units.

**Input:**

*   A list of `Warehouse` objects, each containing the `id`, `location`, and `inventory`.
*   A list of `Store` objects, each containing the `id`, `location`, `demand`, and `unfulfilled_penalty`.
*   A `transportation_rate` (a float representing the cost per unit distance per unit of product).

**Output:**

*   A dictionary representing the optimal shipping plan. The keys are tuples `(warehouse_id, store_id, product_id)`, and the values are the quantity of the product to be shipped from the warehouse to the store. The shipping plan should minimize the total cost.

**Requirements:**

1.  Implement the core optimization logic.
2.  The solution must be efficient enough to handle hundreds of warehouses and stores.
3.  The solution should consider both transportation costs and unfulfilled demand penalties to minimize the total cost.
4.  Provide a clear justification for the algorithm chosen and its time complexity.

**Bonus Challenges:**

*   Implement a caching mechanism to speed up calculations of distances between warehouses and stores.
*   Consider the possibility of shipping products through intermediate hubs (e.g., cross-docking facilities) to further optimize costs.
*   Explore alternative optimization algorithms and compare their performance.
*   Implement a simulation to test your system with randomly generated data and realistic updates to inventory and demand.
