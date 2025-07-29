# Urban Delivery System

This project implements an optimal multi-depot vehicle routing algorithm with time windows and dynamic order insertion. It's designed for an e-commerce company operating in a dense urban environment with multiple delivery depots.

## Overview

The system handles:

1. Multiple depots across a city
2. Multiple vehicles with limited capacity
3. Customer orders with time windows
4. Dynamic order insertion in real-time
5. Optimization for maximum profit

## Core Components

- `Depot`: Represents a distribution center with location and available vehicles
- `Vehicle`: Represents a delivery vehicle with capacity and maximum route duration
- `Order`: Represents a customer order with location, time window, size, and profit
- `DeliverySystem`: Manages the depots and vehicles
- `RoutePlanner`: Processes new orders and optimizes delivery routes

## Key Algorithms

- Haversine distance calculation for accurate geographic distances
- Time window feasibility checking
- Insertion cost calculation
- Route optimization

## Usage Example
