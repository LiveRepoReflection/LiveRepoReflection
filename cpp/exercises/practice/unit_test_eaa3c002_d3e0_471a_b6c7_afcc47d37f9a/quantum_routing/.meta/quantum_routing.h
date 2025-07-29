#ifndef QUANTUM_ROUTING_H
#define QUANTUM_ROUTING_H

#include <vector>

std::vector<int> quantumRouting(int N, const std::vector<std::vector<double>>& channel_probabilities, int S, int D, int max_attempts);

#endif // QUANTUM_ROUTING_H