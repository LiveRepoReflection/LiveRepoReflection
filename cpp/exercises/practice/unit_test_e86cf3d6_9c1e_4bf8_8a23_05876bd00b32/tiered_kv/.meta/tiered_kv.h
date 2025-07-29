#ifndef TIERED_KV_H
#define TIERED_KV_H

#include <string>
#include <optional>

namespace tiered_kv {

bool put(const std::string& key, const std::string& value);
std::optional<std::string> get(const std::string& key);
bool deleteKey(const std::string& key);

}

#endif // TIERED_KV_H