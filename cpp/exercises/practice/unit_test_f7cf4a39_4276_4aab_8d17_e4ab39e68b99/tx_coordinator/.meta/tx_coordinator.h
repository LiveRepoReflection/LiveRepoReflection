#ifndef TX_COORDINATOR_H
#define TX_COORDINATOR_H

#include <string>
#include <functional>
#include <vector>

namespace tx_coordinator {

bool register_service(const std::string& id, std::function<bool()> prepare, std::function<bool()> commit, std::function<bool()> rollback);
void clear_services();
bool execute_transaction(const std::vector<std::string>& service_ids);

} // namespace tx_coordinator

#endif