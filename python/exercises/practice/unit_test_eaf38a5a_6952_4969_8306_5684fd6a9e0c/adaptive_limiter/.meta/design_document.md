# Distributed Rate Limiter with Adaptive Thresholding - Design Document

## 1. System Architecture

### Overview

The distributed rate limiter system is designed to protect APIs from overuse while maximizing legitimate throughput. It dynamically adjusts rate limits based on system health metrics and enforces these limits across a distributed environment.

### Architecture Diagram
