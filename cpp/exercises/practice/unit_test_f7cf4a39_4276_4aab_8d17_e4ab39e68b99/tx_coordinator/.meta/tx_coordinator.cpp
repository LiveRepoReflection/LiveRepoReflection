#include "tx_coordinator.h"
#include <unordered_map>
#include <mutex>

namespace tx_coordinator {

struct Service {
    std::function<bool()> prepare;
    std::function<bool()> commit;
    std::function<bool()> rollback;
};

static std::unordered_map<std::string, Service> service_registry;
static std::mutex registry_mutex;

bool register_service(const std::string& id, std::function<bool()> prepare, std::function<bool()> commit, std::function<bool()> rollback) {
    std::lock_guard<std::mutex> lock(registry_mutex);
    if (service_registry.find(id) != service_registry.end()) {
        return false;
    }
    Service new_service {prepare, commit, rollback};
    service_registry[id] = new_service;
    return true;
}

void clear_services() {
    std::lock_guard<std::mutex> lock(registry_mutex);
    service_registry.clear();
}

bool execute_transaction(const std::vector<std::string>& service_ids) {
    std::vector<std::string> prepared_services;

    {
        std::lock_guard<std::mutex> lock(registry_mutex);
        for (const auto& id : service_ids) {
            if (service_registry.find(id) == service_registry.end()) {
                return false;
            }
        }
    }

    // Phase 1: Prepare
    for (const auto& id : service_ids) {
        bool success = false;
        {
            std::lock_guard<std::mutex> lock(registry_mutex);
            auto it = service_registry.find(id);
            if (it != service_registry.end()) {
                success = it->second.prepare();
            }
        }
        if (success) {
            prepared_services.push_back(id);
        } else {
            // Rollback all services that have already prepared in case of failure.
            for (const auto& pid : prepared_services) {
                std::lock_guard<std::mutex> lock(registry_mutex);
                auto it = service_registry.find(pid);
                if (it != service_registry.end()) {
                    it->second.rollback();
                }
            }
            return false;
        }
    }

    // Phase 2: Commit
    for (const auto& id : service_ids) {
        bool success = false;
        {
            std::lock_guard<std::mutex> lock(registry_mutex);
            auto it = service_registry.find(id);
            if (it != service_registry.end()) {
                success = it->second.commit();
            }
        }
        if (!success) {
            // On commit failure, attempt to rollback all services.
            for (const auto& pid : service_ids) {
                std::lock_guard<std::mutex> lock(registry_mutex);
                auto it = service_registry.find(pid);
                if (it != service_registry.end()) {
                    it->second.rollback();
                }
            }
            return false;
        }
    }

    return true;
}

} // namespace tx_coordinator