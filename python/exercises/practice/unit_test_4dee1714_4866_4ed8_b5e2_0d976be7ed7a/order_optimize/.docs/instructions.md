## Question: Optimal Order Fulfillment

**Project Name:** `order_fulfillment`

**Problem Description:**

You are building the backend for a large e-commerce platform. A critical component of this system is the order fulfillment service. You receive a continuous stream of customer orders, each specifying a list of items with their quantities. Your task is to design an algorithm that determines the *optimal* sequence in which to fulfill these orders to minimize the total waiting time for all customers.

Here's the challenge:

The warehouse stores items in different locations. Fulfilling an order requires retrieving all the items in the order. To simplify, assume retrieving an item takes time proportional to its size. Retrieving multiple items simultaneously is not possible.  The time to fulfill an order is the sum of the sizes of all items in that order.  The waiting time for a customer is the time their order spends in the system *before* it is fulfilled.  The *total* waiting time is the sum of the waiting times of *all* customers.

You are given a list of `n` orders.  Each order `i` is represented as a dictionary: `{'order_id': int, 'items': {'item_id_1': int, 'item_id_2': int, ...}}`. The `order_id` is a unique identifier for each order. The `items` dictionary maps each `item_id` (an integer) to its `quantity` (an integer).

You are also provided with a `items_size` dictionary which maps each `item_id` to its `size`.

Your goal is to write a function that takes a list of orders and the `items_size` dictionary and returns a list of `order_id`s representing the optimal fulfillment order to minimize the total waiting time.

**Constraints:**

*   The number of orders, `n`, can be very large (up to 10^5).
*   The number of items in each order can vary.
*   The size of each item is a positive integer.
*   You need to optimize your algorithm for efficiency. A naive solution will likely time out.
*   Assume no two orders have the exact same fulfillment time.
*   All item_id in order must exist in items_size dictionary.

**Example:**

```python
orders = [
    {'order_id': 1, 'items': {1: 2, 2: 1}},
    {'order_id': 2, 'items': {2: 3, 3: 1}},
    {'order_id': 3, 'items': {1: 1, 3: 2}}
]

items_size = {1: 5, 2: 3, 3: 2}

# Expected Output (one possible optimal order): [2, 3, 1]
# Explanation:
# Order 2: fulfillment_time = (3 * 3) + (1 * 2) = 11
# Order 3: fulfillment_time = (1 * 5) + (2 * 2) = 9
# Order 1: fulfillment_time = (2 * 5) + (1 * 3) = 13

# Fulfillment order: [2, 3, 1]
# Order 2 waiting time: 0
# Order 3 waiting time: 11
# Order 1 waiting time: 11 + 9 = 20
# Total waiting time: 0 + 11 + 20 = 31

# Fulfillment order: [1, 2, 3]
# Order 1 waiting time: 0
# Order 2 waiting time: 13
# Order 3 waiting time: 13 + 11 = 24
# Total waiting time: 0 + 13 + 24 = 37

# Fulfillment order: [3, 2, 1]
# Order 3 waiting time: 0
# Order 2 waiting time: 9
# Order 1 waiting time: 9 + 11 = 20
# Total waiting time: 0 + 9 + 20 = 29

# Fulfillment order: [2, 3, 1] is optimal. Other optimal orders may exist.
```

**Function Signature:**

```python
def optimal_fulfillment_order(orders, items_size):
    """
    Calculates the optimal order fulfillment sequence to minimize total waiting time.

    Args:
        orders (list): A list of order dictionaries.
        items_size (dict): A dictionary mapping item_id to its size.

    Returns:
        list: A list of order_id's representing the optimal fulfillment order.
    """
    pass # Replace with your solution
```
