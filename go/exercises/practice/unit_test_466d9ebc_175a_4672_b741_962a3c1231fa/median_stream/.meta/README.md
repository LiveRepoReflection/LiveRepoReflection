# Distributed Median Stream

This package provides an efficient implementation for calculating the running median of a stream of integers arriving from multiple distributed sources.

## Overview

The `DistributedMedianStream` struct efficiently calculates the running median of a stream of integers from multiple sources. It uses a dual-heap approach to maintain the median in O(log n) time per insertion, and O(1) time for retrieval.

## Usage
