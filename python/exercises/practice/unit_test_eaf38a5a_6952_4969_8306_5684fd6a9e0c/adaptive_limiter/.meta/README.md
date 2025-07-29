# Adaptive Rate Limiter

## Overview

This implementation provides a distributed rate limiter with adaptive thresholding for high-volume API protection. It dynamically adjusts rate limits based on system metrics like CPU utilization, request latency, and error rates, providing robust protection against overload while maximizing throughput for legitimate users.

## System Architecture

The system consists of three main components:

1. **SystemMetrics**: Collects and provides system health metrics
2. **AdaptiveThresholder**: Analyzes metrics and calculates appropriate rate limits
3. **DistributedRateLimiter**: Enforces rate limits across distributed API servers

## Key Features

- **Distributed Operation**: Functions across multiple servers using Redis for shared state
- **Adaptive Thresholding**: Dynamically adjusts rate limits based on system health
- **Multi-level Granularity**: Supports global, user-specific, and endpoint-specific rate limiting
- **Fault Tolerance**: Handles Redis failures with fallback mechanisms
- **Trend Analysis**: Considers metric trends for proactive scaling

## Data Structures

The implementation uses the following key data structures:

1. **Redis Counters**: For distributed rate limit tracking
2. **Time Windows**: Fixed windows for counting requests
3. **Metric History**: For trend analysis and prediction

## Algorithm

The adaptive thresholding algorithm:

1. Collects system metrics (CPU, latency, error rate)
2. Converts each metric to a scaling factor (0-1)
3. Combines factors using configurable weights
4. Adjusts for historical trends
5. Scales the base rate limit accordingly

## Complexity Analysis

- **Time Complexity**: O(1) for rate limit checks
- **Space Complexity**: O(n) where n is the number of unique rate limit keys (users × endpoints)

## Usage
