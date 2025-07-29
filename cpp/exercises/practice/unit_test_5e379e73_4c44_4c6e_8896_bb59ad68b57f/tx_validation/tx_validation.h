#if !defined(TX_VALIDATION_H)
#define TX_VALIDATION_H

#include <string>
#include <vector>
#include <iostream>

namespace tx_validation {
    bool validate_transactions(const std::vector<std::string>& logs);
    bool validate_transactions(std::istream& log_stream);
}

#endif