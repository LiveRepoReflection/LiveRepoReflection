#ifndef QUANTUM_ROUTING_H
#define QUANTUM_ROUTING_H

#include <vector>

namespace quantum_routing {
    // Finds the path with the highest probability of successful delivery
    // from the start node to the end node in a quantum network.
    //
    // Parameters:
    //   probabilities - A matrix where probabilities[i][j] represents the probability
    //                  of successful message transmission from node i to node j.
    //                  If probabilities[i][j] = 0.0, there is no direct channel.
    //   start - The source node index.
    //   end - The destination node index.
    //
    // Returns:
    //   The highest probability of successful message delivery from start to end.
    //   Returns 1.0 if start equals end.
    //   Returns 0.0 if no path exists.
    double find_highest_probability(const std::vector<std::vector<double>>& probabilities,
                                   int start, int end);
}

#endif // QUANTUM_ROUTING_H