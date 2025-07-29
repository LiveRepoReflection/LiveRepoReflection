# Transaction Optimizer

This module provides functionality to optimize the ordering of services within distributed transactions 
to minimize the maximum latency across all transactions.

## Problem Description

In a distributed system, transactions often span multiple independent services. A distributed transaction 
coordinator (DTC) manages these transactions using a two-phase commit protocol. The goal of this optimizer
is to determine an optimal ordering of services within each transaction to minimize the worst-case latency.

## Usage
