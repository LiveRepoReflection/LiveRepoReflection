#if !defined(TX_COORDINATOR_H)
#define TX_COORDINATOR_H

#include <string>
#include <vector>
#include <functional>

bool coordinate_transaction(
    int N,
    const std::vector<std::string>& service_addresses,
    const std::vector<std::function<std::string(const std::string&)>>& participant_behavior,
    int prepare_timeout_ms,
    int completion_timeout_ms
);

#endif // TX_COORDINATOR_H